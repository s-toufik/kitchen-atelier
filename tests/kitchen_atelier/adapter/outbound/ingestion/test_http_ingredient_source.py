import logging

import httpx
import pytest
from openpyxl import Workbook
from pycraftcore.application_configuration.enum.connector_type import ConnectorType
from pycraftcore.application_configuration.model.connector import ApiConnector
from pycraftcore.authentication.model.auth_type import AuthType
from pycraftcore.authentication.model.no_auth import NoAuth

from kitchen_atelier.adapter.outbound.ingestion.http_ingredient_source import (
    HttpIngredientSource,
    detect_extension,
)

HEADER: tuple[str, ...] = (
    "alim_code",
    "alim_nom_fr",
    "Energie, Règlement UE N° 1169/2011 (kcal/100 g)",
    "Protéines, N x 6.25 (g/100 g)",
    "Glucides (g/100 g)",
    "Lipides (g/100 g)",
)


def _connector(base_url: str) -> ApiConnector:
    return ApiConnector(
        name="ciqual",
        type=ConnectorType.api,
        auth=NoAuth(type=AuthType.none),
        base_url=base_url,
        timeout=5,
        retry=0,
    )


def _transport(content: bytes, content_type: str, *, url: str = "https://example.test/dataset") -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content, headers={"content-type": content_type}, request=request)

    return httpx.MockTransport(handler)


class TestDetectExtension:
    def test_prefers_the_url_suffix(self) -> None:
        assert detect_extension("https://host/file.xlsx", None, b"") == "xlsx"

    def test_falls_back_to_content_type(self) -> None:
        assert detect_extension("https://host/r/abc", "application/vnd.ms-excel", b"") == "xls"

    def test_falls_back_to_magic_bytes(self) -> None:
        assert detect_extension("https://host/r/abc", None, b"PAR1rest-of-file") == "parquet"
        assert detect_extension("https://host/r/abc", None, b"PK\x03\x04rest-of-file") == "xlsx"

    def test_defaults_to_csv(self) -> None:
        assert detect_extension("https://host/r/abc", None, b"alim_code;alim_nom_fr") == "csv"


async def test_fetches_and_maps_a_csv_dataset_in_cp1252() -> None:
    csv_text = ";".join(HEADER) + "\n" + "20000;Pâtes, cuites;131;5,0;25,0;1,1"
    transport = _transport(csv_text.encode("cp1252"), "text/csv")
    source = HttpIngredientSource(
        _connector("https://example.test/dataset.csv"), logging.getLogger(__name__), transport=transport
    )

    ingredients = await source.fetch_all()

    assert len(ingredients) == 1
    assert ingredients[0].identity.name == "Pâtes, cuites"
    assert ingredients[0].nutrition.energy.regulation_1169_kcal == 131


async def test_fetches_and_maps_an_xlsx_dataset() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(list(HEADER))
    sheet.append(["20000", "Pâtes, cuites", 131, 5.0, 25.0, 1.1])
    from io import BytesIO

    buffer = BytesIO()
    workbook.save(buffer)

    transport = _transport(
        buffer.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        url="https://example.test/r/some-resource-id",
    )
    source = HttpIngredientSource(
        _connector("https://example.test/r/some-resource-id"),
        logging.getLogger(__name__),
        transport=transport,
    )

    ingredients = await source.fetch_all()

    assert len(ingredients) == 1
    assert ingredients[0].identity.ciqual_code == "20000"
    assert ingredients[0].nutrition.energy.regulation_1169_kcal == 131


async def test_skips_the_fetch_when_no_url_is_configured() -> None:
    source = HttpIngredientSource(_connector(""), logging.getLogger(__name__))

    assert await source.fetch_all() == []


async def test_returns_nothing_for_a_header_only_dataset() -> None:
    csv_text = ";".join(HEADER)
    transport = _transport(csv_text.encode("utf-8"), "text/csv")
    source = HttpIngredientSource(
        _connector("https://example.test/dataset.csv"), logging.getLogger(__name__), transport=transport
    )

    assert await source.fetch_all() == []


def _routed_transport(routes: dict[str, httpx.Response]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        response = routes[str(request.url)]
        response.request = request
        return response

    return httpx.MockTransport(handler)


async def test_falls_back_when_the_primary_dataset_is_unreachable() -> None:
    csv_text = ";".join(HEADER) + "\n" + "20000;Pâtes, cuites;131;5,0;25,0;1,1"
    transport = _routed_transport(
        {
            "https://example.test/primary.csv": httpx.Response(503),
            "https://example.test/fallback.csv": httpx.Response(
                200, content=csv_text.encode("utf-8"), headers={"content-type": "text/csv"}
            ),
        }
    )
    source = HttpIngredientSource(
        _connector("https://example.test/primary.csv"),
        logging.getLogger(__name__),
        fallback_connector=_connector("https://example.test/fallback.csv"),
        transport=transport,
    )

    ingredients = await source.fetch_all()

    assert len(ingredients) == 1
    assert ingredients[0].identity.name == "Pâtes, cuites"


async def test_raises_when_the_primary_fails_and_no_fallback_is_configured() -> None:
    transport = _routed_transport({"https://example.test/primary.csv": httpx.Response(503)})
    source = HttpIngredientSource(
        _connector("https://example.test/primary.csv"), logging.getLogger(__name__), transport=transport
    )

    with pytest.raises(httpx.HTTPStatusError):
        await source.fetch_all()


async def test_does_not_try_the_fallback_when_the_primary_is_simply_unconfigured() -> None:
    source = HttpIngredientSource(
        _connector(""),
        logging.getLogger(__name__),
        fallback_connector=_connector("https://example.test/fallback.csv"),
        transport=_routed_transport({}),
    )

    assert await source.fetch_all() == []
