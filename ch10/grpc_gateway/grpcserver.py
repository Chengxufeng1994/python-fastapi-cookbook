import asyncio
import logging

import grpc
from grpcserver_pb2 import MessageResponse
from grpcserver_pb2_grpc import GrpcServerServicer, add_GrpcServerServicer_to_server


class Service(GrpcServerServicer):
    def GetServerResponse(self, request, context):
        message = request.message
        logging.info(f"Received message: {message}")
        result = f"Hello I am up and running received: {message}"
        result = {
            "message": result,
            "received": True,
        }
        return MessageResponse(**result)


async def server():
    srv = grpc.aio.server()
    add_GrpcServerServicer_to_server(Service(), srv)
    srv.add_insecure_port("[::]:50051")
    logging.info("Starting server on port 50051")
    await srv.start()
    await srv.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("start grpc server")
    asyncio.run(server())
