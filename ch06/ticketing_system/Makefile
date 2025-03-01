.PHONY: run-server
run-server:
	@uvicorn app.main:app --reload

.PHONY: test
test:
	@pytest -vv .

.PHONY: migrate.up
migrate.up:
	@alembic upgrade head

.PHONY: migrate.down
migrate.down:
	@alembic downgrade -1
