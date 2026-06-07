"""Unit tests for YFinanceExtractor."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

from ingestion_context.infrastructure.yfinance_extractor import YFinanceExtractor


def _make_ohlcv_df(rows: list[tuple]) -> pd.DataFrame:
    """Build a DataFrame that looks like yfinance .history() output."""
    idx = pd.DatetimeIndex(
        [pd.Timestamp(r[0]) for r in rows], name="Date"
    )
    return pd.DataFrame(
        [
            {
                "Open": r[1],
                "High": r[2],
                "Low": r[3],
                "Close": r[4],
                "Volume": r[5],
            }
            for r in rows
        ],
        index=idx,
    )


class TestYFinanceExtractor:
    """Tests that exercise the extractor's data-normalisation logic.

    yfinance network calls are mocked so these run offline.
    """

    @pytest.mark.asyncio
    async def test_returns_records_with_expected_columns(self):
        fake_df = _make_ohlcv_df([
            ("2024-06-01", 100.0, 105.0, 99.0, 103.0, 5_000_000),
            ("2024-06-02", 103.0, 108.0, 101.0, 107.0, 6_000_000),
        ])

        with patch("ingestion_context.infrastructure.yfinance_extractor.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = fake_df
            mock_yf.Ticker.return_value = mock_ticker

            extractor = YFinanceExtractor()
            result = await extractor.fetch("AAPL", period="1mo")

        assert len(result["records"]) == 2
        assert result["columns"] == ["date", "Open", "High", "Low", "Close", "Volume"]
        assert result["next_cursor"] is None

    @pytest.mark.asyncio
    async def test_record_values_are_correct(self):
        fake_df = _make_ohlcv_df([
            ("2024-01-15", 150.0, 155.0, 148.0, 152.0, 10_000_000),
        ])

        with patch("ingestion_context.infrastructure.yfinance_extractor.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = fake_df
            mock_yf.Ticker.return_value = mock_ticker

            extractor = YFinanceExtractor()
            result = await extractor.fetch("AAPL")

        rec = result["records"][0]
        assert rec["date"] == "2024-01-15"
        assert rec["Open"] == 150.0
        assert rec["High"] == 155.0
        assert rec["Low"] == 148.0
        assert rec["Close"] == 152.0
        assert rec["Volume"] == 10_000_000

    @pytest.mark.asyncio
    async def test_empty_dataframe_returns_empty_records(self):
        with patch("ingestion_context.infrastructure.yfinance_extractor.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = pd.DataFrame()
            mock_yf.Ticker.return_value = mock_ticker

            extractor = YFinanceExtractor()
            result = await extractor.fetch("INVALID_TICKER")

        assert result["records"] == []
        assert result["columns"] == []

    @pytest.mark.asyncio
    async def test_passes_start_end_to_yfinance(self):
        fake_df = _make_ohlcv_df([
            ("2024-03-01", 1.0, 2.0, 0.5, 1.5, 100),
        ])

        with patch("ingestion_context.infrastructure.yfinance_extractor.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = fake_df
            mock_yf.Ticker.return_value = mock_ticker

            extractor = YFinanceExtractor()
            await extractor.fetch("MSFT", start="2024-01-01", end="2024-06-01")

            mock_ticker.history.assert_called_once_with(
                start="2024-01-01", end="2024-06-01", auto_adjust=True
            )

    @pytest.mark.asyncio
    async def test_uses_period_when_no_dates(self):
        fake_df = _make_ohlcv_df([
            ("2024-03-01", 1.0, 2.0, 0.5, 1.5, 100),
        ])

        with patch("ingestion_context.infrastructure.yfinance_extractor.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = fake_df
            mock_yf.Ticker.return_value = mock_ticker

            extractor = YFinanceExtractor()
            await extractor.fetch("TSLA", period="5y")

            mock_ticker.history.assert_called_once_with(
                period="5y", auto_adjust=True
            )

    @pytest.mark.asyncio
    async def test_defaults_to_1y_period(self):
        fake_df = _make_ohlcv_df([
            ("2024-03-01", 1.0, 2.0, 0.5, 1.5, 100),
        ])

        with patch("ingestion_context.infrastructure.yfinance_extractor.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = fake_df
            mock_yf.Ticker.return_value = mock_ticker

            extractor = YFinanceExtractor()
            await extractor.fetch("GOOG")

            mock_ticker.history.assert_called_once_with(
                period="1y", auto_adjust=True
            )

    @pytest.mark.asyncio
    async def test_volume_is_int(self):
        fake_df = _make_ohlcv_df([
            ("2024-01-01", 50.0, 55.0, 48.0, 53.0, 1_234_567),
        ])

        with patch("ingestion_context.infrastructure.yfinance_extractor.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = fake_df
            mock_yf.Ticker.return_value = mock_ticker

            extractor = YFinanceExtractor()
            result = await extractor.fetch("SPY")

        assert isinstance(result["records"][0]["Volume"], int)

    @pytest.mark.asyncio
    async def test_multiple_rows_sorted_chronologically(self):
        fake_df = _make_ohlcv_df([
            ("2024-01-01", 1.0, 2.0, 0.5, 1.5, 100),
            ("2024-01-02", 2.0, 3.0, 1.0, 2.5, 200),
            ("2024-01-03", 3.0, 4.0, 2.0, 3.5, 300),
        ])

        with patch("ingestion_context.infrastructure.yfinance_extractor.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = fake_df
            mock_yf.Ticker.return_value = mock_ticker

            extractor = YFinanceExtractor()
            result = await extractor.fetch("QQQ")

        dates = [r["date"] for r in result["records"]]
        assert dates == ["2024-01-01", "2024-01-02", "2024-01-03"]
