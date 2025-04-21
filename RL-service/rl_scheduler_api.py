from fastapi import FastAPI
import torch
from stable_baselines3 import DQN
import numpy as np
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Load the trained RL model
# MODEL_PATH_PREVIOUS = "RL-service/dqn_kubernetes"
MODEL_PATH = "dqn_kubernetes.zip"
model = DQN.load(MODEL_PATH)

# Match the middleware's JSON format
class CPU(BaseModel):
    used_percent: float

class NodeData(BaseModel):
    node: str
    cpu: CPU

@app.post("/schedule")
def schedule_from_middleware(nodes: list[NodeData]):
    # Get CPU usage from each node
    print("Received nodes data:", nodes)
    cpu_usages = [node.cpu.used_percent / 100.0 for node in nodes]  # normalize to [0, 1]

    # Pad or truncate to 5 elements (model was trained on 3)
    state = np.zeros(3, dtype=np.float32)
    for i in range(min(3, len(cpu_usages))):
        state[i] = cpu_usages[i]

    # Predict the action
    action, _ = model.predict(state)

    # Safety: If action index is out of bounds, default to first node
    chosen_node = nodes[action].node if action < len(nodes) else nodes[0].node

    return {"scheduled_node": chosen_node}

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "RL Scheduler API is running"}