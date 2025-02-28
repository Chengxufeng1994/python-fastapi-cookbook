.PHONY: test
test:
	@pytest

.PHONY: test-e2e
test-e2e:
	@pytest -m integration -vv

.PHONY: collect-only
collect-only:
	@pytest --co

.PHONY: coverage
coverage:
	@pytest --cov protoapp tests

.PHONY: run-server
run-server:
	@python run_server.py

.PHONY: locust
locust:
	@locust --headless --users 10 --spawn-rate 1
