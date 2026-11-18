venv:
	uv venv

install:
	uv sync

install_dev:
	uv sync --group dev

update_dependency:
ifdef PACKAGE
	uv lock --upgrade-package $(PACKAGE)
else
	uv lock --upgrade
endif
	uv sync

test:
	uv run pytest --disable-warnings

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

typecheck:
	uv run ty check

check:
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test

# --- run -------------------------------------------------------------------
run:
	uv run granian --interface asgi --factory --host 0.0.0.0 --port 8002 --access-log --access-log-fmt '%(addr)s %(method)s %(path)s %(status)d %(dt_ms).1fms' bootstrap.application.kitchen_application:create_kitchen_application

refresh_ingredients:
	uv run python -m bootstrap.application.jobs.refresh_ingredients

clean:
	rm -rf dist src/*.egg-info

build:
	rm -rf dist src/*.egg-info
	uv build

docker_build:
	docker build -f devops/docker/Dockerfile -t kitchen-atelier:local .
