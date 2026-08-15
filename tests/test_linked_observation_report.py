import csv
import subprocess
import unittest
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import data_manifest
import data_quality
import linked_observation_report as linked_report
import session_report
from fixture_helpers import (
    make_active_rows,
    make_placeholder_only_day,
    production_csv_filename,
    write_csv,
    write_daily_csv,
)
from session_tools import SessionDefinition
from source_contracts import (
    ASK,
    BID,
    SourceContract,
    SourceContractError,
    build_raw_csv_filename,
    source_contract_for_side,
)


class LinkedObservationReportTest(unittest.TestCase):
    def read_rows(self, report_path: Path):
        with report_path.open("r", newline="", encoding="utf-8") as report_file:
            return list(csv.DictReader(report_file))

    def create_report(
        self,
        start_day,
        end_day,
        data_dir: Path,
        reports_dir: Path,
        source_contract=None,
        legacy_side_omitted=True,
    ):
        if source_contract is None:
            source_contract = source_contract_for_side(BID)
        with (
            patch("linked_observation_report.REPORTS_DIR", reports_dir),
            patch("linked_observation_report.get_software_revision", return_value="testrev"),
        ):
            summary = linked_report.create_linked_observation_report(
                start_day,
                end_day,
                data_dir,
                source_contract,
                legacy_side_omitted=legacy_side_omitted,
            )

        return summary, self.read_rows(summary.output_path)

    def build_linked_row_from_rows(self, day, rows, source_contract=None):
        if source_contract is None:
            source_contract = source_contract_for_side(BID)
        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root)
            csv_path = write_csv(
                data_dir / build_raw_csv_filename(day, source_contract),
                rows,
            )
            raw_bytes = csv_path.read_bytes()

        session_columns = linked_report.expected_session_report_columns()
        manifest_row = linked_report.build_manifest_row_from_assessment(
            day,
            data_quality.assess_raw_csv_bytes(raw_bytes, day).fields,
            source_contract,
        )
        session_row = session_report.process_raw_bytes_for_day(
            day,
            session_columns,
            raw_bytes,
        ).row
        source_identity = linked_report.source_identity_from_bytes(
            build_raw_csv_filename(day, source_contract),
            raw_bytes,
        )
        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity,
            source_read_failed=False,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
            source_contract=source_contract,
        )
        return linked_row, manifest_row, session_row, source_identity

    def completed_git_process(self, stdout=""):
        return subprocess.CompletedProcess(
            args=["git"],
            returncode=0,
            stdout=stdout,
            stderr="",
        )

    def minimal_linked_row(self, day_text="2024-01-02"):
        row = {column: "" for column in linked_report.LINKED_COLUMNS}
        row["linked_schema_version"] = linked_report.LINKED_SCHEMA_VERSION
        row["date"] = day_text
        row["weekday"] = "Tuesday"
        row["provider"] = data_quality.PROVIDER
        row["instrument"] = data_quality.INSTRUMENT
        row["quote_side"] = data_quality.QUOTE_SIDE
        row["timeframe"] = data_quality.TIMEFRAME
        row["linkage_status"] = linked_report.LINKED
        row["quality_tier"] = linked_report.STRICT_VALID
        return row

    def temporary_report_files(self, output_path: Path):
        return list(output_path.parent.glob(f".{output_path.name}.*.tmp"))


    def test_legacy_bid_linked_report_path_is_unchanged(self):
        start_day = date(2024, 1, 1)
        end_day = date(2024, 1, 31)

        self.assertEqual(
            linked_report.build_linked_report_path(start_day, end_day).name,
            "linked_observation_report_2024-01-01_to_2024-01-31.csv",
        )

    def test_explicit_bid_source_contract_preserves_linked_identity(self):
        bid_contract = source_contract_for_side(BID)
        day = date(2024, 1, 2)

        linked_row, _, _, _ = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
            bid_contract,
        )

        self.assertEqual(linked_row["quote_side"], BID)
        self.assertEqual(linked_row["source_filename"], "XAUUSD_2024-01-02_1min_BID_UTC.csv")
        self.assertEqual(linked_row["linkage_status"], linked_report.LINKED)
        self.assertEqual(linked_row["linkage_reasons"], "")

    def test_explicit_ask_source_contract_preserves_linked_identity(self):
        ask_contract = source_contract_for_side(ASK)
        day = date(2024, 1, 2)

        linked_row, _, _, _ = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
            ask_contract,
        )

        self.assertEqual(linked_row["quote_side"], ASK)
        self.assertEqual(linked_row["source_filename"], "XAUUSD_2024-01-02_1min_ASK_UTC.csv")
        self.assertEqual(linked_row["linkage_status"], linked_report.LINKED)
        self.assertNotIn(linked_report.QUOTE_SIDE_MISMATCH, linked_row["linkage_reasons"])

    def test_synthetic_ask_linked_report_uses_side_specific_output_and_identity(self):
        ask_contract = source_contract_for_side(ASK)
        day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            write_csv(
                data_dir / build_raw_csv_filename(day, ask_contract),
                make_active_rows(day, time(0, 0), time(0, 0)),
            )

            summary, rows = self.create_report(
                day,
                day,
                data_dir,
                reports_dir,
                ask_contract,
                legacy_side_omitted=False,
            )

        self.assertEqual(
            summary.output_path.name,
            "linked_observation_report_ASK_2024-01-02_to_2024-01-02.csv",
        )
        self.assertEqual(summary.strict_valid_observations, 1)
        self.assertEqual(rows[0]["quote_side"], ASK)
        self.assertEqual(rows[0]["source_filename"], "XAUUSD_2024-01-02_1min_ASK_UTC.csv")
        self.assertEqual(rows[0]["linkage_status"], linked_report.LINKED)
        self.assertEqual(rows[0]["quality_tier"], linked_report.STRICT_VALID)

    def test_ask_legacy_side_omitted_linked_report_naming_is_rejected(self):
        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            data_dir.mkdir()
            reports_dir = Path(temp_root) / "reports"

            with self.assertRaisesRegex(SourceContractError, "BID-only"):
                self.create_report(
                    date(2024, 1, 1),
                    date(2024, 1, 1),
                    data_dir,
                    reports_dir,
                    source_contract_for_side(ASK),
                )

    def test_mismatched_manifest_quote_side_is_excluded(self):
        day = date(2024, 1, 2)
        ask_contract = source_contract_for_side(ASK)
        _, manifest_row, session_row, source_identity = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
            ask_contract,
        )
        manifest_row["quote_side"] = BID
        manifest_row["source_filename"] = build_raw_csv_filename(day, source_contract_for_side(BID))

        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity,
            source_read_failed=False,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
            source_contract=ask_contract,
        )

        self.assertEqual(linked_row["linkage_status"], linked_report.CONTRADICTION)
        self.assertIn(linked_report.QUOTE_SIDE_MISMATCH, linked_row["linkage_reasons"])
        self.assertIn(linked_report.SOURCE_FILENAME_MISMATCH, linked_row["linkage_reasons"])
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_source_contract_provider_instrument_timeframe_mismatch_is_excluded(self):
        day = date(2024, 1, 2)
        contract = SourceContract(provider="OtherProvider", instrument="EURUSD", timeframe="5min")
        _, manifest_row, session_row, source_identity = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
        )

        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity,
            source_read_failed=False,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
            source_contract=contract,
        )

        self.assertIn(linked_report.PROVIDER_MISMATCH, linked_row["linkage_reasons"])
        self.assertIn(linked_report.INSTRUMENT_MISMATCH, linked_row["linkage_reasons"])
        self.assertIn(linked_report.TIMEFRAME_MISMATCH, linked_row["linkage_reasons"])
        self.assertIn(linked_report.SOURCE_FILENAME_MISMATCH, linked_row["linkage_reasons"])
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_ask_run_does_not_process_legacy_bid_file(self):
        ask_contract = source_contract_for_side(ASK)
        day = date(2024, 1, 26)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()
            write_daily_csv(data_dir, day, make_active_rows(day, time(0, 0), time(0, 2)))

            summary, rows = self.create_report(
                day,
                day,
                data_dir,
                reports_dir,
                ask_contract,
                legacy_side_omitted=False,
            )

        self.assertEqual(summary.calendar_only_observations, 1)
        self.assertEqual(rows[0]["quote_side"], ASK)
        self.assertEqual(rows[0]["source_filename"], "XAUUSD_2024-01-26_1min_ASK_UTC.csv")
        self.assertEqual(rows[0]["manifest_file_status"], "missing_file")
        self.assertEqual(rows[0]["session_status"], "missing_file")
        self.assertEqual(rows[0]["quality_tier"], linked_report.CALENDAR_ONLY)

    def test_atomic_writer_success_writes_complete_report(self):
        with TemporaryDirectory() as temp_root:
            output_path = Path(temp_root) / "reports" / "linked_report.csv"
            rows = [
                self.minimal_linked_row("2024-01-02"),
                self.minimal_linked_row("2024-01-03"),
            ]

            linked_report.write_linked_report(rows, output_path)

            with output_path.open("r", newline="", encoding="utf-8") as report_file:
                reader = csv.DictReader(report_file)
                written_rows = list(reader)

            self.assertEqual(reader.fieldnames, linked_report.LINKED_COLUMNS)
            self.assertEqual([row["date"] for row in written_rows], ["2024-01-02", "2024-01-03"])
            self.assertEqual(self.temporary_report_files(output_path), [])

    def test_existing_final_report_is_preserved_if_csv_writing_fails(self):
        class FailingDictWriter:
            def __init__(self, report_file, fieldnames):
                self.report_file = report_file

            def writeheader(self):
                self.report_file.write("partial temp content")

            def writerows(self, rows):
                raise RuntimeError("csv write failed")

        with TemporaryDirectory() as temp_root:
            output_path = Path(temp_root) / "reports" / "linked_report.csv"
            output_path.parent.mkdir()
            output_path.write_text("old complete report\n", encoding="utf-8")

            with patch("linked_observation_report.csv.DictWriter", FailingDictWriter):
                with self.assertRaisesRegex(OSError, "Failed to write linked report atomically"):
                    linked_report.write_linked_report(
                        [self.minimal_linked_row()],
                        output_path,
                    )

            self.assertEqual(output_path.read_text(encoding="utf-8"), "old complete report\n")

    def test_no_partial_final_report_appears_when_csv_writing_fails(self):
        class FailingDictWriter:
            def __init__(self, report_file, fieldnames):
                self.report_file = report_file

            def writeheader(self):
                self.report_file.write("partial temp content")
                raise RuntimeError("csv header failed")

            def writerows(self, rows):
                raise AssertionError("writerows should not be called")

        with TemporaryDirectory() as temp_root:
            output_path = Path(temp_root) / "reports" / "linked_report.csv"

            with patch("linked_observation_report.csv.DictWriter", FailingDictWriter):
                with self.assertRaisesRegex(OSError, "Failed to write linked report atomically"):
                    linked_report.write_linked_report(
                        [self.minimal_linked_row()],
                        output_path,
                    )

            self.assertFalse(output_path.exists())

    def test_temporary_file_is_removed_after_csv_writing_failure(self):
        class FailingDictWriter:
            def __init__(self, report_file, fieldnames):
                self.report_file = report_file

            def writeheader(self):
                self.report_file.write("partial temp content")

            def writerows(self, rows):
                raise RuntimeError("csv write failed")

        with TemporaryDirectory() as temp_root:
            output_path = Path(temp_root) / "reports" / "linked_report.csv"

            with patch("linked_observation_report.csv.DictWriter", FailingDictWriter):
                with self.assertRaises(OSError):
                    linked_report.write_linked_report(
                        [self.minimal_linked_row()],
                        output_path,
                    )

            self.assertEqual(self.temporary_report_files(output_path), [])

    def test_existing_final_report_is_preserved_if_atomic_replacement_fails(self):
        with TemporaryDirectory() as temp_root:
            output_path = Path(temp_root) / "reports" / "linked_report.csv"
            output_path.parent.mkdir()
            output_path.write_text("old complete report\n", encoding="utf-8")

            with patch(
                "linked_observation_report.os.replace",
                side_effect=OSError("replace failed"),
            ):
                with self.assertRaisesRegex(OSError, "Failed to write linked report atomically"):
                    linked_report.write_linked_report(
                        [self.minimal_linked_row()],
                        output_path,
                    )

            self.assertEqual(output_path.read_text(encoding="utf-8"), "old complete report\n")

    def test_temporary_file_is_removed_after_atomic_replacement_failure(self):
        with TemporaryDirectory() as temp_root:
            output_path = Path(temp_root) / "reports" / "linked_report.csv"
            output_path.parent.mkdir()

            with patch(
                "linked_observation_report.os.replace",
                side_effect=OSError("replace failed"),
            ):
                with self.assertRaises(OSError):
                    linked_report.write_linked_report(
                        [self.minimal_linked_row()],
                        output_path,
                    )

            self.assertEqual(self.temporary_report_files(output_path), [])

    def test_successful_atomic_replacement_replaces_older_report(self):
        with TemporaryDirectory() as temp_root:
            output_path = Path(temp_root) / "reports" / "linked_report.csv"
            output_path.parent.mkdir()
            output_path.write_text("old complete report\nold extra line\n", encoding="utf-8")

            linked_report.write_linked_report(
                [self.minimal_linked_row("2024-01-02")],
                output_path,
            )

            output_text = output_path.read_text(encoding="utf-8")
            with output_path.open("r", newline="", encoding="utf-8") as report_file:
                written_rows = list(csv.DictReader(report_file))

            self.assertNotIn("old complete report", output_text)
            self.assertEqual(len(written_rows), 1)
            self.assertEqual(written_rows[0]["date"], "2024-01-02")

    def test_clean_repository_revision_returns_full_commit_hash(self):
        full_hash = "1e4d02329be7717e8a1638729aa68fb6696a5c67"

        with patch(
            "linked_observation_report.subprocess.run",
            side_effect=[
                self.completed_git_process(f"{full_hash}\n"),
                self.completed_git_process(""),
            ],
        ):
            revision = linked_report.get_software_revision()

        self.assertEqual(revision, full_hash)

    def test_modified_tracked_file_revision_is_marked_dirty(self):
        full_hash = "1e4d02329be7717e8a1638729aa68fb6696a5c67"

        with patch(
            "linked_observation_report.subprocess.run",
            side_effect=[
                self.completed_git_process(f"{full_hash}\n"),
                self.completed_git_process(" M linked_observation_report.py\n"),
            ],
        ):
            revision = linked_report.get_software_revision()

        self.assertEqual(revision, f"{full_hash}-dirty")

    def test_non_ignored_untracked_file_revision_is_marked_dirty(self):
        full_hash = "1e4d02329be7717e8a1638729aa68fb6696a5c67"

        with patch(
            "linked_observation_report.subprocess.run",
            side_effect=[
                self.completed_git_process(f"{full_hash}\n"),
                self.completed_git_process("?? linked_observation_report.py\n"),
            ],
        ):
            revision = linked_report.get_software_revision()

        self.assertEqual(revision, f"{full_hash}-dirty")

    def test_ignored_files_do_not_mark_revision_dirty(self):
        full_hash = "1e4d02329be7717e8a1638729aa68fb6696a5c67"

        with patch(
            "linked_observation_report.subprocess.run",
            side_effect=[
                self.completed_git_process(f"{full_hash}\n"),
                self.completed_git_process(""),
            ],
        ):
            revision = linked_report.get_software_revision()

        self.assertEqual(revision, full_hash)

    def test_git_unavailable_or_command_failure_returns_unknown(self):
        full_hash = "1e4d02329be7717e8a1638729aa68fb6696a5c67"

        with patch(
            "linked_observation_report.subprocess.run",
            side_effect=OSError("git unavailable"),
        ):
            self.assertEqual(linked_report.get_software_revision(), "unknown")

        with patch(
            "linked_observation_report.subprocess.run",
            side_effect=[
                self.completed_git_process(f"{full_hash}\n"),
                subprocess.CalledProcessError(
                    returncode=1,
                    cmd=["git", "status"],
                    stderr="status failed",
                ),
            ],
        ):
            self.assertEqual(linked_report.get_software_revision(), "unknown")

    def test_outside_git_work_tree_returns_unknown(self):
        with patch(
            "linked_observation_report.subprocess.run",
            side_effect=subprocess.CalledProcessError(
                returncode=128,
                cmd=["git", "rev-parse", "HEAD"],
                stderr="fatal: not a git repository",
            ),
        ):
            revision = linked_report.get_software_revision()

        self.assertEqual(revision, "unknown")

    def test_linked_report_records_corrected_revision_value_deterministically(self):
        full_hash = "1e4d02329be7717e8a1638729aa68fb6696a5c67"
        day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()

            write_daily_csv(data_dir, day, make_active_rows(day, time(0, 0), time(0, 0)))

            with (
                patch("linked_observation_report.REPORTS_DIR", reports_dir),
                patch(
                    "linked_observation_report.subprocess.run",
                    side_effect=[
                        self.completed_git_process(f"{full_hash}\n"),
                        self.completed_git_process("?? local_change.py\n"),
                    ],
                ),
            ):
                summary = linked_report.create_linked_observation_report(
                    day,
                    day,
                    data_dir,
                )

            rows = self.read_rows(summary.output_path)

        self.assertEqual(rows[0]["software_revision"], f"{full_hash}-dirty")

    def test_writes_one_linked_row_per_requested_date(self):
        start_day = date(2024, 1, 1)
        end_day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()

            write_daily_csv(data_dir, start_day, make_active_rows(start_day, time(0, 0), time(0, 0)))
            write_daily_csv(data_dir, end_day, make_active_rows(end_day, time(0, 0), time(0, 0)))

            summary, rows = self.create_report(start_day, end_day, data_dir, reports_dir)

        self.assertEqual(summary.requested_dates, 2)
        self.assertEqual([row["date"] for row in rows], ["2024-01-01", "2024-01-02"])

    def test_linked_columns_have_stable_order(self):
        expected_columns = [
            "linked_schema_version",
            "date",
            "weekday",
            "provider",
            "instrument",
            "quote_side",
            "timeframe",
            "source_filename",
            "source_file_size_bytes",
            "source_checksum_algorithm",
            "source_checksum",
            "manifest_schema_version",
            "validation_rule_version",
            "active_filter_rule_identity",
            "session_definition_checksum",
            "software_revision",
            "session_status",
            "manifest_file_status",
            "manifest_quality_status",
            "manifest_quality_reasons",
            "linkage_status",
            "linkage_reasons",
            "quality_tier",
            "manifest_total_row_count",
            "manifest_active_row_count",
            "session_total_csv_rows",
            "session_active_candle_count",
            "session_inactive_placeholder_count",
            "daily_open",
            "daily_high",
            "daily_low",
            "daily_close",
            "daily_range",
            "time_of_daily_high_utc",
            "time_of_daily_low_utc",
            "tokyo_open",
            "tokyo_high",
            "tokyo_low",
            "tokyo_close",
            "tokyo_range",
            "tokyo_time_of_high_utc",
            "tokyo_time_of_low_utc",
            "tokyo_active_candle_count",
            "london_open",
            "london_high",
            "london_low",
            "london_close",
            "london_range",
            "london_time_of_high_utc",
            "london_time_of_low_utc",
            "london_active_candle_count",
            "new_york_open",
            "new_york_high",
            "new_york_low",
            "new_york_close",
            "new_york_range",
            "new_york_time_of_high_utc",
            "new_york_time_of_low_utc",
            "new_york_active_candle_count",
        ]

        self.assertEqual(linked_report.LINKED_COLUMNS, expected_columns)

    def test_valid_complete_processed_valid_observation_is_strict_valid(self):
        day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()

            write_daily_csv(data_dir, day, make_active_rows(day, time(0, 0), time(0, 0)))
            summary, rows = self.create_report(day, day, data_dir, reports_dir)

        row = rows[0]
        self.assertEqual(summary.strict_valid_observations, 1)
        self.assertEqual(row["session_status"], "complete")
        self.assertEqual(row["manifest_file_status"], "processed")
        self.assertEqual(row["manifest_quality_status"], "valid")
        self.assertEqual(row["linkage_status"], linked_report.LINKED)
        self.assertEqual(row["quality_tier"], linked_report.STRICT_VALID)

    def test_warning_observation_is_retained_for_review_with_reason_codes(self):
        day = date(2024, 1, 2)
        rows = make_active_rows(day, time(0, 0), time(0, 0))
        rows.pop(720)

        linked_row, _, _, _ = self.build_linked_row_from_rows(day, rows)

        self.assertEqual(linked_row["session_status"], "complete")
        self.assertEqual(linked_row["manifest_file_status"], "processed")
        self.assertEqual(linked_row["manifest_quality_status"], "warning")
        self.assertEqual(linked_row["manifest_quality_reasons"], data_quality.MISSING_MINUTES)
        self.assertEqual(linked_row["quality_tier"], linked_report.WARNING_REVIEW)

    def test_invalid_observation_is_retained_but_excluded(self):
        day = date(2024, 1, 2)
        rows = make_active_rows(day, time(0, 0), time(0, 1))
        rows[0]["timestamp_utc"] = "2024-01-02 00:00:30"

        linked_row, _, _, _ = self.build_linked_row_from_rows(day, rows)

        self.assertEqual(linked_row["session_status"], "complete")
        self.assertEqual(linked_row["manifest_file_status"], "processed")
        self.assertEqual(linked_row["manifest_quality_status"], "invalid")
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_missing_file_calendar_row_is_retained(self):
        day = date(2024, 1, 3)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()

            _, rows = self.create_report(day, day, data_dir, reports_dir)

        row = rows[0]
        self.assertEqual(row["session_status"], "missing_file")
        self.assertEqual(row["manifest_file_status"], "missing_file")
        self.assertEqual(row["manifest_quality_status"], "not_assessed")
        self.assertEqual(row["linkage_status"], linked_report.CALENDAR_ONLY)
        self.assertEqual(row["quality_tier"], linked_report.CALENDAR_ONLY)

    def test_no_active_candle_calendar_row_is_retained(self):
        day = date(2024, 1, 6)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()

            write_daily_csv(data_dir, day, make_placeholder_only_day(day))
            _, rows = self.create_report(day, day, data_dir, reports_dir)

        row = rows[0]
        self.assertEqual(row["session_status"], "no_active_candles")
        self.assertEqual(row["manifest_file_status"], "no_active_candles")
        self.assertEqual(row["manifest_quality_status"], "not_assessed")
        self.assertEqual(row["quality_tier"], linked_report.CALENDAR_ONLY)

    def test_manifest_parse_failure_and_session_failure_are_excluded(self):
        day = date(2024, 1, 4)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()
            csv_path = data_dir / production_csv_filename(day)
            csv_path.write_text(
                "wrong,open,high,low,close,volume\n"
                "2024-01-04 00:00:00,2000,2001,1999,2000.5,1\n",
                encoding="utf-8",
            )

            with patch("builtins.print"):
                _, rows = self.create_report(day, day, data_dir, reports_dir)

        row = rows[0]
        self.assertEqual(row["session_status"], "failed")
        self.assertEqual(row["manifest_file_status"], "parse_failed")
        self.assertEqual(row["manifest_quality_status"], "invalid")
        self.assertEqual(row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_date_coverage_mismatch_is_rejected(self):
        requested_days = [date(2024, 1, 1), date(2024, 1, 2)]
        rows = [{"date": "2024-01-01"}]

        with self.assertRaisesRegex(ValueError, "coverage"):
            linked_report.validate_linked_rows_cover_requested_dates(rows, requested_days)

    def test_duplicate_date_is_rejected(self):
        requested_days = [date(2024, 1, 1), date(2024, 1, 2)]
        rows = [{"date": "2024-01-01"}, {"date": "2024-01-01"}]

        with self.assertRaisesRegex(ValueError, "duplicate"):
            linked_report.validate_linked_rows_cover_requested_dates(rows, requested_days)

    def test_comparable_count_disagreement_is_flagged_and_excluded(self):
        day = date(2024, 1, 2)
        _, manifest_row, session_row, source_identity = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
        )
        session_row["total_csv_rows"] = "999"

        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity,
            source_read_failed=False,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
        )

        self.assertEqual(linked_row["linkage_status"], linked_report.CONTRADICTION)
        self.assertIn(linked_report.ROW_COUNT_MISMATCH, linked_row["linkage_reasons"])
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_source_filename_mismatch_is_flagged(self):
        day = date(2024, 1, 2)
        _, manifest_row, session_row, source_identity = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
        )
        manifest_row["source_filename"] = "wrong.csv"

        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity,
            source_read_failed=False,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
        )

        self.assertIn(linked_report.SOURCE_FILENAME_MISMATCH, linked_row["linkage_reasons"])
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_checksum_and_size_mismatch_are_flagged(self):
        day = date(2024, 1, 2)
        _, manifest_row, session_row, source_identity = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
        )
        manifest_row["source_file_size_bytes"] = "1"
        manifest_row["source_checksum"] = "not-the-real-checksum"

        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity,
            source_read_failed=False,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
        )

        self.assertIn(linked_report.SOURCE_SIZE_MISMATCH, linked_row["linkage_reasons"])
        self.assertIn(linked_report.SOURCE_CHECKSUM_MISMATCH, linked_row["linkage_reasons"])
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_source_mutation_during_processing_is_flagged(self):
        day = date(2024, 1, 2)
        initial_rows = make_active_rows(day, time(0, 0), time(0, 2))
        changed_rows = make_active_rows(day, time(0, 0), time(0, 3))

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()
            csv_path = write_daily_csv(data_dir, day, initial_rows)
            initial_bytes = csv_path.read_bytes()
            changed_path = write_daily_csv(Path(temp_root) / "changed", day, changed_rows)
            changed_bytes = changed_path.read_bytes()

            with patch(
                "linked_observation_report.read_source_bytes",
                side_effect=[initial_bytes, changed_bytes],
            ):
                _, rows = self.create_report(day, day, data_dir, reports_dir)

        row = rows[0]
        self.assertEqual(row["linkage_status"], linked_report.SOURCE_CHANGED)
        self.assertIn(linked_report.SOURCE_IDENTITY_CHANGED, row["linkage_reasons"])
        self.assertEqual(row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_source_deletion_after_initial_byte_capture_is_flagged(self):
        day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()
            csv_path = write_daily_csv(
                data_dir,
                day,
                make_active_rows(day, time(0, 0), time(0, 2)),
            )
            initial_bytes = csv_path.read_bytes()

            with patch(
                "linked_observation_report.read_source_bytes",
                side_effect=[initial_bytes, OSError("source disappeared")],
            ):
                _, rows = self.create_report(day, day, data_dir, reports_dir)

        row = rows[0]
        self.assertEqual(row["linkage_status"], linked_report.SOURCE_CHANGED)
        self.assertIn(linked_report.SOURCE_IDENTITY_CHANGED, row["linkage_reasons"])
        self.assertEqual(row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_same_size_source_replacement_with_different_bytes_is_flagged(self):
        day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()
            csv_path = write_daily_csv(
                data_dir,
                day,
                make_active_rows(day, time(0, 0), time(0, 2)),
            )
            initial_bytes = csv_path.read_bytes()
            changed_bytes = initial_bytes.replace(b"2000.000", b"2000.001", 1)

            self.assertEqual(len(initial_bytes), len(changed_bytes))
            self.assertNotEqual(initial_bytes, changed_bytes)

            with patch(
                "linked_observation_report.read_source_bytes",
                side_effect=[initial_bytes, changed_bytes],
            ):
                _, rows = self.create_report(day, day, data_dir, reports_dir)

        row = rows[0]
        self.assertEqual(row["linkage_status"], linked_report.SOURCE_CHANGED)
        self.assertIn(linked_report.SOURCE_IDENTITY_CHANGED, row["linkage_reasons"])
        self.assertEqual(row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_session_definition_checksum_is_deterministic(self):
        first_checksum = linked_report.calculate_session_definition_checksum()
        second_checksum = linked_report.calculate_session_definition_checksum()

        self.assertEqual(first_checksum, second_checksum)
        self.assertEqual(len(first_checksum), 64)

    def test_rule_and_run_identity_fields_are_present(self):
        day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()

            write_daily_csv(data_dir, day, make_active_rows(day, time(0, 0), time(0, 0)))
            _, rows = self.create_report(day, day, data_dir, reports_dir)

        row = rows[0]
        self.assertEqual(row["linked_schema_version"], linked_report.LINKED_SCHEMA_VERSION)
        self.assertEqual(row["manifest_schema_version"], data_quality.MANIFEST_SCHEMA_VERSION)
        self.assertEqual(row["validation_rule_version"], data_quality.VALIDATION_RULE_VERSION)
        self.assertEqual(
            row["active_filter_rule_identity"],
            linked_report.ACTIVE_FILTER_RULE_IDENTITY,
        )
        self.assertEqual(len(row["session_definition_checksum"]), 64)
        self.assertEqual(row["software_revision"], "testrev")

    def test_duplicate_or_colliding_session_prefixes_are_rejected(self):
        definitions = [
            SessionDefinition("A B", "UTC", time(0, 0), time(1, 0), "#000000"),
            SessionDefinition("A_B", "UTC", time(1, 0), time(2, 0), "#111111"),
            SessionDefinition("New York", "UTC", time(2, 0), time(3, 0), "#222222"),
        ]

        with patch(
            "linked_observation_report.load_session_definitions",
            return_value=definitions,
        ):
            with self.assertRaisesRegex(ValueError, "colliding prefixes"):
                linked_report.validate_session_configuration(date(2024, 1, 1))

    def test_existing_session_calculation_values_are_preserved(self):
        day = date(2024, 1, 2)

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root) / "data_raw"
            reports_dir = Path(temp_root) / "reports"
            data_dir.mkdir()

            csv_path = write_daily_csv(
                data_dir,
                day,
                make_active_rows(day, time(0, 0), time(0, 0)),
            )
            raw_bytes = csv_path.read_bytes()
            session_row = session_report.process_raw_bytes_for_day(
                day,
                linked_report.expected_session_report_columns(),
                raw_bytes,
            ).row
            _, rows = self.create_report(day, day, data_dir, reports_dir)

        linked_row = rows[0]
        for column in linked_report.session_calculation_columns():
            self.assertEqual(linked_row[column], session_row[column])

    def test_existing_v010_and_v011_schemas_remain_unchanged(self):
        self.assertEqual(
            session_report.build_report_columns(date(2024, 1, 1)),
            linked_report.expected_session_report_columns(),
        )
        self.assertEqual(
            data_manifest.MANIFEST_COLUMNS,
            [
                "manifest_schema_version",
                "validation_rule_version",
                "date",
                "weekday",
                "provider",
                "instrument",
                "quote_side",
                "timeframe",
                "source_filename",
                *data_quality.ASSESSMENT_COLUMNS,
            ],
        )

    def test_source_contract_mismatches_are_flagged(self):
        day = date(2024, 1, 2)
        _, manifest_row, session_row, source_identity = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
        )
        manifest_row["provider"] = "Other"
        manifest_row["instrument"] = "EURUSD"
        manifest_row["quote_side"] = "ASK"
        manifest_row["timeframe"] = "5min"

        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity,
            source_read_failed=False,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
        )

        self.assertIn(linked_report.PROVIDER_MISMATCH, linked_row["linkage_reasons"])
        self.assertIn(linked_report.INSTRUMENT_MISMATCH, linked_row["linkage_reasons"])
        self.assertIn(linked_report.QUOTE_SIDE_MISMATCH, linked_row["linkage_reasons"])
        self.assertIn(linked_report.TIMEFRAME_MISMATCH, linked_row["linkage_reasons"])
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_session_values_with_manifest_failure_are_flagged(self):
        day = date(2024, 1, 2)
        _, manifest_row, session_row, source_identity = self.build_linked_row_from_rows(
            day,
            make_active_rows(day, time(0, 0), time(0, 2)),
        )
        manifest_row["file_status"] = "parse_failed"
        manifest_row["quality_status"] = "invalid"

        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity,
            source_read_failed=False,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
        )

        self.assertIn(
            linked_report.SESSION_VALUES_WITH_MANIFEST_FAILURE,
            linked_row["linkage_reasons"],
        )
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_manifest_processed_session_failed_is_flagged(self):
        day = date(2024, 1, 2)
        rows = make_active_rows(day, time(0, 0), time(0, 1))
        rows[0]["open"] = "not-a-number"

        with patch("builtins.print"):
            linked_row, _, _, _ = self.build_linked_row_from_rows(day, rows)

        self.assertEqual(linked_row["manifest_file_status"], "processed")
        self.assertEqual(linked_row["session_status"], "failed")
        self.assertIn(
            linked_report.MANIFEST_PROCESSED_SESSION_FAILED,
            linked_row["linkage_reasons"],
        )
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)

    def test_unavailable_checksum_is_flagged(self):
        day = date(2024, 1, 2)
        session_columns = linked_report.expected_session_report_columns()
        manifest_row = linked_report.build_manifest_row_from_assessment(
            day,
            data_quality.parse_failed_assessment(None, data_quality.READ_ERROR).fields,
        )
        session_row = session_report.empty_report_row(day, session_columns, "failed")

        linked_row = linked_report.build_linked_row(
            day,
            manifest_row,
            session_row,
            source_identity=None,
            source_read_failed=True,
            source_changed=False,
            session_definition_checksum="session-checksum",
            software_revision="testrev",
        )

        self.assertEqual(linked_row["linkage_status"], linked_report.SOURCE_UNAVAILABLE)
        self.assertIn(
            linked_report.SOURCE_CHECKSUM_UNAVAILABLE,
            linked_row["linkage_reasons"],
        )
        self.assertEqual(linked_row["quality_tier"], linked_report.EXCLUDED_UNUSABLE)


if __name__ == "__main__":
    unittest.main()
