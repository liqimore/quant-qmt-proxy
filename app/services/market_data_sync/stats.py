from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HistoryDownloadStats:
    symbols_total: int = 0
    pairs_downloaded: int = 0
    pairs_skipped: int = 0
    pairs_failed: int = 0

    @property
    def pairs_total(self) -> int:
        return self.pairs_downloaded + self.pairs_skipped + self.pairs_failed


@dataclass
class InstrumentSyncStats:
    instrument_count: int = 0
    skipped: bool = False


@dataclass
class DailySyncStats:
    run_date: str = ""
    instrument: InstrumentSyncStats = field(default_factory=InstrumentSyncStats)
    history: HistoryDownloadStats = field(default_factory=HistoryDownloadStats)
