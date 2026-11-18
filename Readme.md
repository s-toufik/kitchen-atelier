# kitchen-atelier

The backend behind the homelab's recipe and nutrition studio: versioned recipes in MongoDB, and a French ingredient/macro catalog in PostgreSQL kept fresh by a scheduled job against ANSES's CIQUAL table. The kitchen agent (agent-runtime / agent-toolbox) reads the same data through its own scoped MCP tools, so it can reason about past meals and ingredients.

```text
                         ┌────────────────────────────────────────────────┐
  homelab-ui kitchen ───►│  kitchen-atelier   /v1/recipes · /v1/ingredients│
  page (REST)            │                                                │
                         │  recipes/versions ──► MongoDB `kitchen`         │
                         │  ingredients ────────► PostgreSQL `homelab`.`kitchen` schema
                         │  refresh job ────────► ANSES CIQUAL (any file) │
                         └────────────────────────────────────────────────┘
```

## Run it

Requirements: Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --group dev
cp .env.example .env      # fill in the Postgres/Mongo connections and the CIQUAL dataset URL
make run
```

| | Endpoint |
|---|---|
| Recipes | `GET/POST /v1/recipes`, `GET /v1/recipes/{id}/versions`, `GET/POST /v1/recipes/{id}/versions/{n}` |
| Ingredients | `GET /v1/ingredients?q=...` |
| Health | `GET /actuator/health` (also `/health/liveness`, `/health/readiness`) |
| Version | `GET /actuator/info` |

Refresh the ingredient catalog by hand with `make refresh_ingredients`; in the homelab it runs as a weekly CronJob (CIQUAL's dataset changes rarely).

## Design

- **Versioning.** Saving a recipe never edits a version in place: it always appends the next one as an immutable snapshot (title, ingredients, steps, macros — everything). Selecting an older version just renders that snapshot; editing resumes from a draft of the latest one. `SaveRecipeVersion` refuses a save whose `based_on_version` is no longer the recipe's latest (`StaleVersion`, HTTP 409) rather than silently overwriting history.
- **Units.** European only: g, kg, ml, cl, L, càs (tablespoon, 15 ml), càc (teaspoon, 5 ml), pincée (pinch), pièce (piece). See `domain/recipe/unit.py`.
- **Ingredients.** There is no live CIQUAL API — ANSES publishes the table as a bulk file, in whatever format it happens to be in at the time (XLS, XLSX, CSV, Parquet have all been seen across its official and mirror sources). `adapter/outbound/ingestion/http_ingredient_source.py` downloads it and detects its format from the URL, the response's content type or its magic bytes, then hands it to `pycraftcore`'s `file_handler` to get plain rows regardless of the underlying format; `ciqual_row_mapper.py` maps those rows to the domain model by column name, so the two concerns — "what file is this" and "what does a CIQUAL row mean" — never depend on each other. `RefreshIngredientCatalog` diffs the result against what's stored so an unchanged weekly run is a no-op. A recipe's ingredient lines carry their own macros (denormalized at save time), so a later catalog refresh never changes an already-saved recipe's nutrition numbers.
- **Postgres schema placement.** The ingredient catalog lives in a `kitchen` schema inside the shared `homelab` database, not a database of its own — the homelab's shared `postgres-mcp` only ever connects to `homelab`, so this is what makes the catalog reachable by the kitchen agent's MCP tools.

## Working on it

Hexagonal layout, same shape as `agent-runtime` / `agent-toolbox`: `domain` has no framework dependencies at all (enforced by `tests/architecture`), `application` holds the ports and use cases, `adapter` holds everything that talks to Postgres, MongoDB and the CIQUAL ingestion pipeline, and `bootstrap` wires it all into a FastAPI app via `pycraftcore`'s configuration/DI conventions.

```bash
make check   # lint + typecheck + test
```
