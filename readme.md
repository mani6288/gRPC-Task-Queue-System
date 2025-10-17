**Developed by Muhammad Rehman**
**Email mani.rehman1010@gmail.com**

**Task given by Martin Teller**

A minimal distributed task queue built using **Python gRPC**, featuring:
- One **Distributor (Server)** managing a priority queue  
- Two **Agents (Workers)** fetching and executing tasks  
- A simple **Client** enqueuing demo jobs  


**Steps to set up:**
1. python3 -m venv .venv
2. source .venv/bin/activate
3. pip install grpcio grpcio-tools
4. python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. taskqueue.proto

Once you install the taskqueue.proto you should see
taskqueue_pb2.py
taskqueue_pb2_grpc.py

**Run the gRPC:**

1. Open a terminal and run source .venv/bin/activate 
and then run python3 distributor.py
2. Open a terminal and run source .venv/bin/activate and run python3 agent.py --id agent-a
3. Open a third terminal run source .venv/bin/activate and run python3 agent.py --id agent-b
4. Open fourth 3. Open a third terminal run run source .venv/bin/activate and run python3 client_enqueue.py