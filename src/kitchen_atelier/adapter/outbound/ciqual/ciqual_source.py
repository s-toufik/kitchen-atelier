from datetime import UTC, datetime

import httpx
from pycraftcore.application_configuration.model.connector import ApiConnector
from pycraftcore.logger.port import Logger

from kitchen_atelier.adapter.outbound.ciqual.ciqual_parser import parse_ciqual_csv
from kitchen_atelier.domain.ingredient.ingredient import Ingredient

_ENCODINGS: tuple[str, ...] = ("utf-8-sig", "cp1252")


class CiqualSource:
    def __init__(self, connector: ApiConnector, logger: Logger) -> None:
        self._connector = connector
        self._logger = logger

    async def fetch_all(self) -> list[Ingredient]:
        if not self._connector.base_url.strip():
            self._logger.warning("CIQUAL dataset URL is not configured; skipping fetch")
            return []

        async with httpx.AsyncClient(timeout=self._connector.timeout) as client:
            response = await client.get(self._connector.base_url)
            response.raise_for_status()

        return parse_ciqual_csv(_decode(response.content), datetime.now(UTC))


def _decode(content: bytes) -> str:
    for encoding in _ENCODINGS:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")
