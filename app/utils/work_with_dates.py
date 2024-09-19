from datetime import datetime

from fastapi import HTTPException, status
from loguru import logger


@logger.catch(reraise=True)
def parse_like_datetime(datetime_string: str):
    """
    Parses a string into datetime using formats:
    `DD.MM.YYYY HH:MM` | `YYYY.MM.DD HH:MM` |
    `DD-MM-YYYY HH:MM` | `YYYY-MM-DD HH:MM`
    """
    datetime_formats = tuple(
        date_format + " %H:%M" for date_format in (
            "%d.%m.%Y", "%Y.%m.%d", "%d-%m-%Y", "%Y-%m-%d")
    )
    for datetime_format in datetime_formats:
        try:
            return datetime.strptime(datetime_string, datetime_format)

        except ValueError:
            pass
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Cannot parse datetime format «{datetime_string}». "
                "Please, use one of this examples: "
                f"{' | '.join(datetime_formats)}"))
