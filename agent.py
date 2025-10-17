import time
import argparse

import grpc

import taskqueue_pb2 as pb
import taskqueue_pb2_grpc as pb_grpc


def process(task: pb.Task):
    ms = max(task.expected_ms, 100)
    time.sleep(ms / 1000.0)


def run(agent_id: str, host: str = "localhost", port: int = 50051, poll_ms: int = 500):
    chan = grpc.insecure_channel(f"{host}:{port}")
    stub = pb_grpc.DistributorStub(chan)
    info = pb.AgentInfo(agent_id=agent_id)

    print(f"Agent {agent_id} ready against {host}:{port}")
    while True:
        task = stub.RequestTask(info)
        if not task.id:
            time.sleep(poll_ms / 1000.0)
            continue
        t0 = time.time()
        print(f"[{agent_id}] claimed task={task.id} tier={pb.Task.Tier.Name(task.tier)} expected_ms={task.expected_ms}")
        process(task)
        dt = int((time.time() - t0) * 1000)
        stub.ReportDone(pb.TaskDone(task_id=task.id, agent_id=agent_id, notes=f"took {dt}ms"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=50051)
    ap.add_argument("--poll-ms", type=int, default=500)
    args = ap.parse_args()
    run(args.id, args.host, args.port, args.poll_ms)
