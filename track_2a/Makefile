.PHONY: run run_on_fedlex_sample

# Replace with the command that starts the project in a Docker container,
# e.g. `docker compose up`. It must work from a clean checkout.
run:
	@echo "make run is not implemented yet — edit this Makefile"; exit 1

run_on_fedlex_sample:
    cd src && uv run run_on_fedlex_sample.py $(if $(SEED),--seed $(SEED))
