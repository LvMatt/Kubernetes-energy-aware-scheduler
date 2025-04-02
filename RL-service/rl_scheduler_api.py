from fastapi import FastAPI
import torch
from stable_baselines3 import DQN
import numpy as np
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Load the trained RL model
MODEL_PATH = "RL-service/dqn_kubernetes"
model = DQN.load(MODEL_PATH)

class Node(BaseModel):
    id: str
    cpu_usage: float

class ScheduleRequest(BaseModel):
    nodes: list[Node]

@app.post("/schedule")
def schedule_pod(request: ScheduleRequest):
    # Convert CPU usage values to a fixed-size array (default to 0 if fewer nodes)
    node_count = 5  # Must match training setup
    node_features = np.zeros(node_count, dtype=np.float32)  # Default: 0 latency for missing nodes

    # Fill in CPU usage data (assuming lower CPU usage ~ lower latency)
    for i, node in enumerate(request.nodes):
        if i < node_count:
            node_features[i] = node.cpu_usage

    # Predict action using the trained RL model
    action, _ = model.predict(node_features)

    # Get the scheduled node ID
    selected_node = request.nodes[action].id if action < len(request.nodes) else request.nodes[0].id

    return {"scheduled_node": selected_node}

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "RL Scheduler API is running"}