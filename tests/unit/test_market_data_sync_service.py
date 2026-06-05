from __future__ import annotations

from app.config import MarketDataSyncConfig, Settings, XTQuantConfig, XTQuantMode
from app.services.instrument_repository import InstrumentRepository
from app.services.market_data_sync.service import MarketDataSyncService
from tests.unit.market_data_sync_helpers import make_repository


class RecordingInstrumentPhase:
    def __init__(self, repository: InstrumentRepository | None = None):
        self.calls: list[str] = []
        self._repository = repository

    def run(self, run_date: str) -> None:
        self.calls.append(run_date)
        if self._repository is not None:
            self._repository.set_instruments_done(run_date)


class RecordingHistoryPhase:
    def __init__(self):
        self.calls: list[tuple[str, list[str]]] = []

    def run(self, run_date: str, symbols: list[str]) -> None:
        self.calls.append((run_date, symbols))


def build_settings() -> Settings:
    return Settings(
        xtquant=XTQuantConfig(mode=XTQuantMode.DEV),
        market_data_sync=MarketDataSyncConfig(enabled=True, symbols_override=["000001.SZ"]),
    )


def test_run_daily_skips_when_completed(tmp_path):
    repo = make_repository(tmp_path)
    from datetime import date

    run_date = date.today().isoformat()
    repo.mark_run_running(run_date)
    repo.mark_run_completed(run_date)

    instrument = RecordingInstrumentPhase()
    history = RecordingHistoryPhase()
    service = MarketDataSyncService(build_settings(), repo, instrument, history)
    service.run_daily_if_needed()
    assert instrument.calls == []
    assert history.calls == []


def test_run_daily_phase_order(tmp_path):
    repo = make_repository(tmp_path)
    from datetime import date

    run_date = date.today().isoformat()

    instrument = RecordingInstrumentPhase(repository=repo)
    history = RecordingHistoryPhase()
    service = MarketDataSyncService(build_settings(), repo, instrument, history)
    service.run_daily_if_needed()

    assert instrument.calls == [run_date]
    assert history.calls == [(run_date, ["000001.SZ"])]
    assert repo.get_run_status(run_date) == "completed"
