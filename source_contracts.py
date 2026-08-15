"""Side-aware source identity helpers for XAU/USD provenance outputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


PROVIDER = "Dukascopy"
INSTRUMENT = "XAUUSD"
TIMEFRAME = "1min"
BID = "BID"
ASK = "ASK"
SUPPORTED_QUOTE_SIDES = (BID, ASK)


class SourceContractError(ValueError):
    """Raised when a source contract or side-aware path is ambiguous."""


@dataclass(frozen=True)
class SourceContract:
    """Immutable source identity for one side-specific provenance run."""

    provider: str = PROVIDER
    instrument: str = INSTRUMENT
    quote_side: str = BID
    timeframe: str = TIMEFRAME

    def __post_init__(self) -> None:
        for field_name in ("provider", "instrument", "timeframe"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise SourceContractError(f"{field_name} must be a non-empty string.")

        object.__setattr__(self, "quote_side", validate_quote_side(self.quote_side))


def validate_quote_side(quote_side: str) -> str:
    """Return a supported quote side, rejecting ambiguous values."""
    if quote_side not in SUPPORTED_QUOTE_SIDES:
        allowed = ", ".join(SUPPORTED_QUOTE_SIDES)
        raise SourceContractError(f"quote_side must be one of: {allowed}.")

    return quote_side


def source_contract_for_side(quote_side: str = BID) -> SourceContract:
    """Build the default XAUUSD source contract for one quote side."""
    return SourceContract(quote_side=quote_side)


DEFAULT_SOURCE_CONTRACT = SourceContract()


def build_raw_csv_filename(day: date, contract: SourceContract = DEFAULT_SOURCE_CONTRACT) -> str:
    """Build the side-aware raw CSV basename for one requested day."""
    return (
        f"{contract.instrument}_{day:%Y-%m-%d}_"
        f"{contract.timeframe}_{contract.quote_side}_UTC.csv"
    )


def build_report_filename(
    report_stem: str,
    start_day: date,
    end_day: date,
    contract: SourceContract = DEFAULT_SOURCE_CONTRACT,
    *,
    legacy_side_omitted: bool = True,
) -> str:
    """Build a report basename, preserving legacy BID-only side-omitted names."""
    if legacy_side_omitted:
        if contract.quote_side != BID:
            raise SourceContractError(
                "Legacy side-omitted report names are BID-only; use side-specific "
                "naming for ASK."
            )
        side_label = ""
    else:
        side_label = f"_{contract.quote_side}"

    return (
        f"{report_stem}{side_label}_{start_day:%Y-%m-%d}"
        f"_to_{end_day:%Y-%m-%d}.csv"
    )
