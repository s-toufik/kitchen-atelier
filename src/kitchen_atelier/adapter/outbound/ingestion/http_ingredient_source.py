import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import httpx
from pycraftcore.application_configuration.model.connector import ApiConnector
from pycraftcore.file_handler.adapter.handler import Handler
from pycraftcore.logger.port import Logger

from kitchen_atelier.adapter.outbound.ingestion.ciqual_row_mapper import CiqualRowMapper
from kitchen_atelier.domain.ingredient.ingredient import Ingredient

_SUPPORTED_EXTENSIONS: tuple[str, ...] = ("csv", "xlsx", "xls", "parquet")
_TEXT_EXTENSIONS: tuple[str, ...] = ("csv",)
_TEXT_ENCODINGS: tuple[str, ...] = ("utf-8-sig", "cp1252")

_CONTENT_TYPE_EXTENSIONS: dict[str, str] = {
    "text/csv": "csv",
    "application/csv": "csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-excel": "xls",
    "application/x-parquet": "parquet",
    "application/vnd.apache.parquet": "parquet",
}
_MAGIC_SIGNATURES: tuple[tuple[bytes, str], ...] = (
    (b"PAR1", "parquet"),
    (b"PK\x03\x04", "xlsx"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "xls"),
)
_DEFAULT_EXTENSION: str = "csv"


class IngestionFormatError(Exception):
    pass


class HttpIngredientSource:
    def __init__(
        self,
        connector: ApiConnector,
        logger: Logger,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._connector = connector
        self._logger = logger
        self._transport = transport

    async def fetch_all(self) -> list[Ingredient]:
        if not self._connector.base_url.strip():
            self._logger.warning("Ingredient dataset URL is not configured; skipping fetch")
            return []

        async with httpx.AsyncClient(
            timeout=self._connector.timeout,
            follow_redirects=True,
            transport=self._transport,
        ) as client:
            response = await client.get(self._connector.base_url)
            response.raise_for_status()

        extension = detect_extension(
            str(response.url), response.headers.get("content-type"), response.content
        )
        content = response.content
        if extension in _TEXT_EXTENSIONS:
            content = _decode_to_utf8(content)

        fetched_at = datetime.now(UTC)
        with tempfile.NamedTemporaryFile(suffix=f".{extension}") as temp_file:
            temp_file.write(content)
            temp_file.flush()
            rows = Handler(temp_file.name).read()

        if not isinstance(rows, list):
            raise IngestionFormatError(
                f"expected a list of rows from a .{extension} dataset, got {type(rows).__name__}"
            )
        if not rows:
            return []

        mapper = CiqualRowMapper(rows[0].keys())
        ingredients: list[Ingredient] = []
        for row in rows:
            ingredient = mapper.map_row(row, fetched_at)
            if ingredient is not None:
                ingredients.append(ingredient)
        return ingredients


def detect_extension(url: str, content_type: str | None, content: bytes) -> str:
    suffix = Path(urlparse(url).path).suffix.lstrip(".").lower()
    if suffix in _SUPPORTED_EXTENSIONS:
        return suffix

    mapped = _CONTENT_TYPE_EXTENSIONS.get((content_type or "").split(";")[0].strip().lower())
    if mapped is not None:
        return mapped

    for signature, extension in _MAGIC_SIGNATURES:
        if content.startswith(signature):
            return extension

    return _DEFAULT_EXTENSION


def _decode_to_utf8(content: bytes) -> bytes:
    for encoding in _TEXT_ENCODINGS:
        try:
            return content.decode(encoding).encode("utf-8")
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace").encode("utf-8")
