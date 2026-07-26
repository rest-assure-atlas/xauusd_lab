import contextlib
import csv
import hashlib
import io
import os
import unittest
from datetime import date, datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import data_manifest
import data_quality
import internal_flat_zero_volume_diagnostic as diagnostic
import linked_observation_report as linked_report
from fixture_helpers import (
    make_active_rows,
    make_placeholder_rows,
    production_csv_filename,
    write_daily_csv,
)


class InternalFlatZeroVolumeDiagnosticTest(unittest.TestCase):
    def setUp(self):
        self.day = date(2024, 1, 2)

    def manifest_row_from_raw(self, data_dir: Path, day: date, rows):
        csv_path = write_daily_csv(data_dir, day, rows)
        raw_bytes = csv_path.read_bytes()
        manifest_row = data_manifest.base_manifest_row(day)
        manifest_row.update(data_quality.assess_raw_csv_bytes(raw_bytes, day).fields)
        return manifest_row, csv_path

    def linked_row(self, day: date, quality_tier=linked_report.WARNING_REVIEW):
        row = {column: "" for column in linked_report.LINKED_COLUMNS}
        row["linked_schema_version"] = linked_report.LINKED_SCHEMA_VERSION
        row["date"] = f"{day:%Y-%m-%d}"
        row["weekday"] = day.strftime("%A")
        row["source_filename"] = production_csv_filename(day)
        row["quality_tier"] = quality_tier
        row["session_status"] = "complete"
        row["daily_range"] = "10.000"
        row["tokyo_range"] = "2.000"
        row["london_range"] = "3.000"
        row["new_york_range"] = "4.000"
        row["tokyo_active_candle_count"] = "540"
        row["london_active_candle_count"] = "540"
        row["new_york_active_candle_count"] = "540"
        return row

    def write_manifest_report(self, report_path: Path, rows):
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", newline="", encoding="utf-8") as report_file:
            writer = csv.DictWriter(report_file, fieldnames=data_manifest.MANIFEST_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    def write_linked_report(self, report_path: Path, rows, fieldnames=None):
        if fieldnames is None:
            fieldnames = linked_report.LINKED_COLUMNS

        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", newline="", encoding="utf-8") as report_file:
            writer = csv.DictWriter(report_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})

    def read_rows(self, report_path: Path):
        with report_path.open("r", newline="", encoding="utf-8") as report_file:
            reader = csv.DictReader(report_file)
            return reader.fieldnames, list(reader)

    def create_diagnostic(self, manifest_rows, linked_rows, data_dir: Path, reports_dir: Path):
        manifest_path = reports_dir / "manifest.csv"
        linked_path = reports_dir / "linked.csv"
        self.write_manifest_report(manifest_path, manifest_rows)
        self.write_linked_report(linked_path, linked_rows)

        with patch("internal_flat_zero_volume_diagnostic.REPORTS_DIR", reports_dir):
            summary = diagnostic.create_internal_flat_zero_volume_diagnostic(
                manifest_path,
                linked_path,
                data_dir,
            )

        fieldnames, rows = self.read_rows(summary.output_path)
        return summary, fieldnames, rows

    def rows_with_one_internal_run(self):
        rows = make_active_rows(self.day, time(0, 0), time(0, 5))
        rows[2] = make_placeholder_rows(self.day, time(0, 2), time(0, 3))[0]
        rows[3] = make_placeholder_rows(self.day, time(0, 3), time(0, 4))[0]
        return rows

    def test_cli_reads_manifest_path_linked_report_path_and_data_directory(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, _csv_path = self.manifest_row_from_raw(
                data_dir,
                self.day,
                self.rows_with_one_internal_run(),
            )
            manifest_path = reports_dir / "manifest.csv"
            linked_path = reports_dir / "linked.csv"
            self.write_manifest_report(manifest_path, [manifest_row])
            self.write_linked_report(linked_path, [self.linked_row(self.day)])

            output = io.StringIO()
            with (
                patch("internal_flat_zero_volume_diagnostic.REPORTS_DIR", reports_dir),
                contextlib.redirect_stdout(output),
            ):
                exit_code = diagnostic.main(
                    [
                        str(manifest_path),
                        str(linked_path),
                        "--data-dir",
                        str(data_dir),
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("Internal flat zero-volume diagnostic complete.", output.getvalue())

    def test_required_manifest_schema_validation(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "manifest.csv"
            report_path.write_text("date,weekday\n2024-01-02,Tuesday\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing required columns"):
                diagnostic.read_required_csv_rows(
                    report_path,
                    diagnostic.MANIFEST_REQUIRED_COLUMNS,
                    "manifest",
                )

    def test_required_linked_report_schema_validation(self):
        with TemporaryDirectory() as temp_root:
            report_path = Path(temp_root) / "linked.csv"
            row = self.linked_row(self.day)
            fieldnames = [
                column
                for column in linked_report.LINKED_COLUMNS
                if column != "quality_tier"
            ]
            self.write_linked_report(report_path, [row], fieldnames)

            with self.assertRaisesRegex(ValueError, "missing required columns: quality_tier"):
                diagnostic.read_required_csv_rows(
                    report_path,
                    diagnostic.LINKED_REQUIRED_COLUMNS,
                    "linked report",
                )

    def test_compatible_date_coverage_is_required(self):
        manifest_rows = [
            {"date": "2024-01-02", "weekday": "Tuesday"},
            {"date": "2024-01-03", "weekday": "Wednesday"},
        ]
        linked_rows = [
            {"date": "2024-01-02", "weekday": "Tuesday"},
            {"date": "2024-01-04", "weekday": "Thursday"},
        ]

        with self.assertRaisesRegex(ValueError, "date coverage"):
            diagnostic.validate_compatible_date_coverage(manifest_rows, linked_rows)

    def test_edge_flat_zero_volume_rows_are_not_internal(self):
        raw_rows = (
            make_placeholder_rows(self.day, time(0, 0), time(0, 2))
            + make_active_rows(self.day, time(0, 2), time(0, 5))
            + make_placeholder_rows(self.day, time(0, 5), time(0, 7))
        )

        with TemporaryDirectory() as temp_root:
            data_dir = Path(temp_root)
            csv_path = write_daily_csv(data_dir, self.day, raw_rows)
            diagnostic_rows = diagnostic.read_raw_diagnostic_rows(csv_path)

        runs = diagnostic.detect_internal_flat_runs(diagnostic_rows)

        self.assertEqual(runs, [])

    def test_one_internal_run_is_detected_with_start_end_and_count(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, _csv_path = self.manifest_row_from_raw(
                data_dir,
                self.day,
                self.rows_with_one_internal_run(),
            )
            summary, _fieldnames, rows = self.create_diagnostic(
                [manifest_row],
                [self.linked_row(self.day)],
                data_dir,
                reports_dir,
            )

        self.assertEqual(summary.warning_dates, 1)
        self.assertEqual(summary.internal_flat_runs, 1)
        self.assertEqual(rows[0]["run_number"], "1")
        self.assertEqual(rows[0]["run_start_utc"], "2024-01-02 00:02:00")
        self.assertEqual(rows[0]["run_end_utc"], "2024-01-02 00:03:00")
        self.assertEqual(rows[0]["run_row_count"], "2")

    def test_multiple_internal_runs_on_one_date_are_detected(self):
        rows = make_active_rows(self.day, time(0, 0), time(0, 7))
        rows[1] = make_placeholder_rows(self.day, time(0, 1), time(0, 2))[0]
        rows[4] = make_placeholder_rows(self.day, time(0, 4), time(0, 5))[0]
        rows[5] = make_placeholder_rows(self.day, time(0, 5), time(0, 6))[0]

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, _csv_path = self.manifest_row_from_raw(data_dir, self.day, rows)
            _summary, _fieldnames, output_rows = self.create_diagnostic(
                [manifest_row],
                [self.linked_row(self.day)],
                data_dir,
                reports_dir,
            )

        self.assertEqual([row["run_number"] for row in output_rows], ["1", "2"])
        self.assertEqual([row["run_row_count"] for row in output_rows], ["1", "2"])
        self.assertEqual(output_rows[0]["run_start_utc"], "2024-01-02 00:01:00")
        self.assertEqual(output_rows[1]["run_start_utc"], "2024-01-02 00:04:00")

    def test_session_overlap_and_outside_counts_are_written(self):
        rows = (
            make_active_rows(self.day, time(7, 58), time(7, 59))
            + make_placeholder_rows(self.day, time(7, 59), time(22, 2))
            + make_active_rows(self.day, time(22, 2), time(22, 3))
        )

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, _csv_path = self.manifest_row_from_raw(data_dir, self.day, rows)
            _summary, _fieldnames, output_rows = self.create_diagnostic(
                [manifest_row],
                [self.linked_row(self.day)],
                data_dir,
                reports_dir,
            )

        self.assertEqual(output_rows[0]["tokyo_overlap_rows"], "61")
        self.assertEqual(output_rows[0]["london_overlap_rows"], "540")
        self.assertEqual(output_rows[0]["new_york_overlap_rows"], "540")
        self.assertEqual(output_rows[0]["outside_configured_session_rows"], "2")

    def test_manifest_internal_count_must_reconcile_with_detected_run_rows(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, _csv_path = self.manifest_row_from_raw(
                data_dir,
                self.day,
                self.rows_with_one_internal_run(),
            )
            manifest_row["internal_inactive_row_count"] = "999"
            manifest_path = reports_dir / "manifest.csv"
            linked_path = reports_dir / "linked.csv"
            self.write_manifest_report(manifest_path, [manifest_row])
            self.write_linked_report(linked_path, [self.linked_row(self.day)])

            with self.assertRaisesRegex(ValueError, "does not match detected"):
                diagnostic.create_internal_flat_zero_volume_diagnostic(
                    manifest_path,
                    linked_path,
                    data_dir,
                )

    def test_linked_status_and_range_context_are_preserved(self):
        linked_row = self.linked_row(self.day)
        linked_row["quality_tier"] = "warning_review"
        linked_row["session_status"] = "complete"
        linked_row["daily_range"] = "12.345"
        linked_row["tokyo_range"] = "1.111"
        linked_row["london_range"] = "2.222"
        linked_row["new_york_range"] = "3.333"

        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, _csv_path = self.manifest_row_from_raw(
                data_dir,
                self.day,
                self.rows_with_one_internal_run(),
            )
            _summary, _fieldnames, output_rows = self.create_diagnostic(
                [manifest_row],
                [linked_row],
                data_dir,
                reports_dir,
            )

        self.assertEqual(output_rows[0]["linked_quality_tier"], "warning_review")
        self.assertEqual(output_rows[0]["linked_session_status"], "complete")
        self.assertEqual(output_rows[0]["daily_range"], "12.345")
        self.assertEqual(output_rows[0]["tokyo_range"], "1.111")
        self.assertEqual(output_rows[0]["london_range"], "2.222")
        self.assertEqual(output_rows[0]["new_york_range"], "3.333")

    def test_missing_raw_file_for_warning_date_fails_clearly(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row = data_manifest.base_manifest_row(self.day)
            manifest_row.update(data_quality.blank_assessment_fields())
            manifest_row["file_status"] = "processed"
            manifest_row["quality_status"] = "warning"
            manifest_row["quality_reasons"] = data_quality.INTERNAL_FLAT_ZERO_VOLUME
            manifest_row["source_filename"] = production_csv_filename(self.day)
            manifest_row["internal_inactive_row_count"] = "1"
            manifest_path = reports_dir / "manifest.csv"
            linked_path = reports_dir / "linked.csv"
            self.write_manifest_report(manifest_path, [manifest_row])
            self.write_linked_report(linked_path, [self.linked_row(self.day)])

            with self.assertRaisesRegex(FileNotFoundError, "Raw CSV for warning date is missing"):
                diagnostic.create_internal_flat_zero_volume_diagnostic(
                    manifest_path,
                    linked_path,
                    data_dir,
                )

    def test_raw_csv_is_not_modified(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, csv_path = self.manifest_row_from_raw(
                data_dir,
                self.day,
                self.rows_with_one_internal_run(),
            )
            before_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()

            self.create_diagnostic(
                [manifest_row],
                [self.linked_row(self.day)],
                data_dir,
                reports_dir,
            )

            after_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()

        self.assertEqual(before_hash, after_hash)

    def test_output_column_order_is_deterministic(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, _csv_path = self.manifest_row_from_raw(
                data_dir,
                self.day,
                self.rows_with_one_internal_run(),
            )
            _summary, fieldnames, _rows = self.create_diagnostic(
                [manifest_row],
                [self.linked_row(self.day)],
                data_dir,
                reports_dir,
            )

        self.assertEqual(fieldnames, diagnostic.DIAGNOSTIC_COLUMNS)

    def test_no_cause_labels_are_emitted(self):
        with TemporaryDirectory() as temp_root:
            temp_root_path = Path(temp_root)
            data_dir = temp_root_path / "data_raw"
            reports_dir = temp_root_path / "reports"
            data_dir.mkdir()

            manifest_row, _csv_path = self.manifest_row_from_raw(
                data_dir,
                self.day,
                self.rows_with_one_internal_run(),
            )
            _summary, fieldnames, rows = self.create_diagnostic(
                [manifest_row],
                [self.linked_row(self.day)],
                data_dir,
                reports_dir,
            )

        emitted_text = ",".join(fieldnames + [value for row in rows for value in row.values()])
        forbidden_labels = [
            "market closure",
            "provider outage",
            "corruption",
            "harmless",
            "cause",
        ]

        for forbidden_label in forbidden_labels:
            self.assertNotIn(forbidden_label, emitted_text.lower())


if __name__ == "__main__":
    unittest.main()
