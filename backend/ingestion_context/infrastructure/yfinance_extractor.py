"""Yahoo Finance extractor using yfinance.

Fetches OHLCV data for a given ticker symbol and returns it in the
canonical dict format expected by RecordTransformer.
"""

import logging

import yfinance as yf

logger = logging.getLogger(__name__)


class YFinanceExtractor:
    """Pulls historical daily OHLCV data from Yahoo Finance."""

    DEFAULT_PERIOD = "1y"  # fallback when no explicit dates given

    async def fetch(
        self,
        ticker: str,
        start: str | None = None,
        end: str | None = None,
        period: str | None = None,
    ) -> dict:
        """Fetch historical data for *ticker*.

        Parameters
        ----------
        ticker : str
            Yahoo Finance symbol, e.g. "AAPL", "MSFT", "BTC-USD".
        start / end : str | None
            ISO date strings.  When both are supplied they override *period*.
        period : str | None
            yfinance period string ("1mo", "3mo", "1y", "5y", "max").
            Ignored when start/end are given.

        Returns
        -------
        dict with keys ``records``, ``columns``, ``next_cursor`` (always None).
        """
        logger.info("Fetching Yahoo Finance data for %s", ticker)

        try:
            tk = yf.Ticker(ticker)

            if start and end:
                df = tk.history(start=start, end=end, auto_adjust=True)
            else:
                df = tk.history(period=period or self.DEFAULT_PERIOD, auto_adjust=True)
        except Exception:
            logger.exception("yfinance fetch failed for ticker %s", ticker)
            return {"records": [], "columns": [], "next_cursor": None}

        if df.empty:
            logger.warning("No data returned for ticker %s", ticker)
            return {"records": [], "columns": [], "next_cursor": None}

        # Normalise the DataFrame into a list[dict]
        records: list[dict] = []
        columns = ["date", "Open", "High", "Low", "Close", "Volume"]

        for idx, row in df.iterrows():
            record = {
                "date": idx.strftime("%Y-%m-%d"),
                "Open": float(row["Open"]),
                "High": float(row["High"]),
                "Low": float(row["Low"]),
                "Close": float(row["Close"]),
                "Volume": int(row["Volume"]),
            }
            records.append(record)

        logger.info("Fetched %d records for %s", len(records), ticker)
        return {
            "records": records,
            "columns": columns,
            "next_cursor": None,  # yfinance returns all at once
        }
