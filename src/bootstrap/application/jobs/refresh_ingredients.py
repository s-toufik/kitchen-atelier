import asyncio
import sys

from bootstrap.configuration.settings import ProcessSettings
from bootstrap.container.kitchen_container import KitchenContainer

ROLE: str = "kitchen-atelier-refresh"


async def _run() -> int:
    container = KitchenContainer(ProcessSettings.for_role(ROLE))
    await container.boot()
    try:
        changed = await container.refresh_ingredient_catalog.handle()
        container.logging.info(f"Ingredient catalog refresh complete: {changed} changed")
        return 0
    except Exception:
        container.logging.exception("Ingredient catalog refresh failed")
        return 1
    finally:
        await container.stop()


def main() -> None:
    sys.exit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
