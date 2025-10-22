
import time
import heapq
import threading
from concurrent import futures
from typing import Optional
import grpc
import taskqueue_pb2 as pb
import taskqueue_pb2_grpc as pb_grpc


class PriorityQueue:
    # Stronger aging: every second of waiting reduces the effective expected_ms by this many ms.
    _AGING_MS_PER_SEC = 25.0

    def __init__(self):
        self._heap = []
        self._lock = threading.Lock()
        self._counter = 0

    def _tier_rank(self, tier):
        return 0 if tier == pb.Task.PAID else 1

    def _priority_key(self, task: pb.Task, counter: int, now: Optional[float] = None):
        if now is None:
            now = time.time()
        enqueued_at = task.enqueued_at_unix or int(now)
        wait_seconds = max(0.0, now - enqueued_at)
        aged_expected = max(0.0, task.expected_ms - wait_seconds * self._AGING_MS_PER_SEC)
        return (self._tier_rank(task.tier), aged_expected, enqueued_at, counter)

    def push(self, task: pb.Task):
        with self._lock:
            self._counter += 1
            # key = (self._tier_rank(task.tier), task.expected_ms, task.enqueued_at_unix, self._counter)
            # heapq.heappush(self._heap, (key, task))
            counter = self._counter
            now = time.time()
            key = self._priority_key(task, counter, now)
            heapq.heappush(self._heap, (key, counter, task))

    def pop(self):
        with self._lock:
            if not self._heap:
                return None
            # _, task = heapq.heappop(self._heap)
            now = time.time()
            refreshed = [
                (self._priority_key(task, counter, now), counter, task)
                for _, counter, task in self._heap
            ]
            heapq.heapify(refreshed)
            self._heap = refreshed
            _, _, task = heapq.heappop(self._heap)
            return task

    def size(self):
        with self._lock:
            return len(self._heap)


class DistributorService(pb_grpc.DistributorServicer):
    def __init__(self):
        self.q = PriorityQueue()

    # client task submit here
    def Enqueue(self, request: pb.Task, context):
        if request.enqueued_at_unix == 0:
            request.enqueued_at_unix = int(time.time())
        self.q.push(request)
        return pb.EnqueueReply(ok=True, msg=f"queued: {request.id} (size={self.q.size()})")

    # agents task pull next
    def RequestTask(self, request: pb.AgentInfo, context):
        task = self.q.pop()
        if task is None:
            return pb.Task(id="", user_id="", tier=pb.Task.FREE, expected_ms=0, enqueued_at_unix=0)
        return task

    def ReportDone(self, request: pb.TaskDone, context):
        print(f"[DONE] agent={request.agent_id} task={request.task_id} notes={request.notes}")
        return pb.Empty()


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_DistributorServicer_to_server(DistributorService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Distributor listening on 0.0.0.0:{port}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()