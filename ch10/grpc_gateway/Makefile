.PHONY: proto
proto:
	@poetry run python -m grpc_tools.protoc \
    -I ./proto \
    --python_out=. \
    --grpc_python_out=. \
    ./proto/grpcserver.proto


.PHONY: run-app
run-app:
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: run-grpc-srv
run-grpc-srv:
	@poetry run python grpcserver.py
