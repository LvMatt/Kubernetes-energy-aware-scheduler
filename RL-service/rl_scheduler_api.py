from fastapi import FastAPI
import torch
from stable_baselines3 import DQN
import numpy as np
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Load the trained RL model
# MODEL_PATH_PREVIOUS = "RL-service/dqn_kubernetes"
MODEL_CPU_PATH = "dqn_kubernetes_cpu.zip"
MODEL_ENERGY_PATH = "dqn_kubernetes_energy.zip"
model_cpu = DQN.load(MODEL_CPU_PATH)
model_energy = DQN.load(MODEL_ENERGY_PATH)


# Match the middleware's JSON format
class CPU(BaseModel):
    used_percent: float

class Memory(BaseModel):
    used_percent: float
class NodeData(BaseModel):
    node: str
    cpu: CPU
    memory: Memory

@app.post("/schedule")
def schedule_from_middleware(nodes: list[NodeData]):
    # Get CPU usage from each node
    print("Received nodes data:", nodes)
    cpu_usages = [node.cpu.used_percent / 100.0 for node in nodes]  # normalize to [0, 1]
    ram_usages = [node.memory.used_percent / 100.0 for node in nodes]  # normalize to [0, 1]
    print("ram_usages", ram_usages)
    # Pad or truncate to 5 elements (model was trained on 3)
    state = np.zeros(3, dtype=np.float32)
    for i in range(min(3, len(ram_usages))):
        state[i] = ram_usages[i]

    # Predict the action
    action, _ = model_cpu.predict(state)

    # Safety: If action index is out of bounds, default to first node
    chosen_node = nodes[action].node if action < len(nodes) else nodes[0].node
    print("Chosen node:", chosen_node)
    return {"scheduled_node": chosen_node}

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "RL Scheduler API is running"}