import time
import uuid
import random
import grpc
import taskqueue_pb2 as pb
import taskqueue_pb2_grpc as pb_grpc

def submit_tasks(n=10, host="localhost", port=50051):
    chan = grpc.insecure_channel(f"{host}:{port}")
    stub = pb_grpc.DistributorStub(chan)
    now = int(time.time())
    for i in range(n):
        tier = pb.Task.PAID if random.random() < 0.5 else pb.Task.FREE
        expected_ms = random.choice([200, 300, 400, 800, 1200])
        enq = now - random.randint(0, 30)
        task = pb.Task(
            id=str(uuid.uuid4())[:8],
            user_id=f"u{i}",
            tier=tier,
            expected_ms=expected_ms,
            enqueued_at_unix=enq,
        )
        resp = stub.Enqueue(task)
        print(resp.msg)

if __name__ == "__main__":
    submit_tasks()
