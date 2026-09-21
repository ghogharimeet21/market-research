from logging import getLogger

import pandas as pd
import requests

from utils import date_to_ms, split_datetime


logger = getLogger(__name__)

BINANCE_HISTORICAL_URL = "https://api.binance.com/api/v3/klines"

COLUMNS = [
    "symbol",
    "date",
    "time",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


def get_data(
    symbol: str,
    start_date: int,
    end_date: int,
    interval: str = "1m",
) -> pd.DataFrame:

    start_ts = date_to_ms(start_date)
    end_ts = date_to_ms(end_date)

    logger.info(
        f"Starting Binance load: "
        f"symbol={symbol}, "
        f"start={start_date}, "
        f"end={end_date}, "
        f"interval={interval}"
    )

    quotes = []

    current_start = start_ts

    with requests.Session() as session:

        while current_start < end_ts:

            response = session.get(
                BINANCE_HISTORICAL_URL,
                params={
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": current_start,
                    "endTime": end_ts,
                    "limit": 1000,
                },
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict):
                raise RuntimeError(
                    f"Binance API error for {symbol}: {data}"
                )

            if not data:
                break

            for row in data:

                timestamp = row[0]

                # end_date is exclusive
                if timestamp >= end_ts:
                    break

                date_int, time_seconds = split_datetime(timestamp)

                quotes.append(
                    {
                        "symbol": symbol,
                        "date": date_int,
                        "time": time_seconds,
                        "open": float(row[1]),
                        "high": float(row[2]),
                        "low": float(row[3]),
                        "close": float(row[4]),
                        "volume": float(row[5]),
                    }
                )

            # Move to the candle after the last returned candle
            current_start = data[-1][0] + 1

    logger.info(
        f"Binance load complete: "
        f"symbol={symbol}, "
        f"start={start_date}, "
        f"end={end_date}, "
        f"rows={len(quotes)}"
    )

    return pd.DataFrame(quotes, columns=COLUMNS)