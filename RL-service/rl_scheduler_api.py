from fastapi import FastAPI
import torch
from stable_baselines3 import DQN
import numpy as np
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Load the trained RL model
# MODEL_PATH_PREVIOUS = "RL-service/dqn_kubernetes"
MODEL_MEMORY_PATH = "dqn_kubernetes_cpu.zip"
MODEL_ENERGY_PATH = "dqn_kubernetes_energy.zip"
model_memory = DQN.load(MODEL_MEMORY_PATH)
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
    print("Received nodes data:", nodes)
    #cpu_usages = [node.cpu.used_percent / 100.0 for node in nodes]  # normalize to [0, 1]
    memory_usages = [node.memory.used_percent / 100.0 for node in nodes]
    active_pods = [node.activePods.active_pods for node in nodes]

    print("memory_usages", memory_usages)
    # Pad or truncate to 5 elements (model was trained on 3)
    state = np.zeros(3, dtype=np.float32)
    for i in range(min(3, len(memory_usages))):
        state[i] = memory_usages[i]


    # Energy usage prediction
    """ for mem, pods in zip(memory_usages, active_pods):
        state.extend([mem, pods]) """
    
    """ state = (state + [0.0] * 6)[:6]
    state_np = np.array(state, dtype=np.float32)
    action, _ = model_memory.predict(state_np) """

    # Memory usage prediction
    action, _ = model_memory.predict(state)

    chosen_node = nodes[action].node if action < len(nodes) else nodes[0].node
    print("Chosen node:", chosen_node)
    return {"scheduled_node": chosen_node}

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "RL Scheduler API is running"}