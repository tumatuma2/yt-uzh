.PHONY: run

# Replace with the command that starts the project in a Docker container,
# e.g. `docker compose up`. It must work from a clean checkout.
run:
	docker compose -f compose.yaml up -d --no-recreate my-container
	docker compose exec my-container make indocker_run

.PHONY: indocker_run_on_fedlex_sample indocker_run
indocker_run_on_fedlex_sample:
	cd src && uv run run_on_fedlex_sample.py $(if $(SEED),--seed $(SEED))
indocker_run:
	cd src && uv run -m work_on_dataset --test

### Diagrams

DOT_FILES := $(wildcard docs/*.dot)
SVG_FILES := $(DOT_FILES:.dot=.svg)

.PHONY: diagrams

diagrams: $(SVG_FILES)

docs/%.svg: docs/%.dot
	dot -Tsvg $< -o $@
