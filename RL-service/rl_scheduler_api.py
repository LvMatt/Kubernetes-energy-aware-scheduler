from fastapi import FastAPI
import torch
from stable_baselines3 import DQN
import numpy as np
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Load the trained RL model
""" MODEL_MEMORY_PATH = "dqn_kubernetes_memory.zip"
model_memory = DQN.load(MODEL_MEMORY_PATH) """
MODEL_ENERGY_PATH = "dqn_kubernetes_energy.zip"
model_energy = DQN.load(MODEL_ENERGY_PATH)

print("Model loaded successfully")

# Match the middleware's JSON format
class CPU(BaseModel):
    used_percent: float
""" class Memory(BaseModel):
    used_bytes: float """

class Memory(BaseModel):
    used_percent: float

class ActivePods(BaseModel):
    active_pods: int
class NodeData(BaseModel):
    node: str
    cpu: CPU
    memory: Memory
    activePods: ActivePods

@app.post("/schedule")
def schedule_from_middleware(nodes: list[NodeData]):
    print("Received nodes data:", nodes)
    nodes.sort(key=lambda node: node.node)
    print("Received sorted nodes data:", nodes)
    #Memory only usage prediction
    #memory_only_usages = [node.memory.used_bytes  for node in nodes]
    #print("memory_only_usages", memory_only_usages)
    #Energy usage prediction
    memory_usages = [node.memory.used_percent / 100.0 for node in nodes]
    active_pods = [node.activePods.active_pods for node in nodes]
    state = active_pods + memory_usages
    
    #print("memory_usages", memory_only_usages)
    # Pad or truncate to 5 elements (model was trained on 3)
    """ state = np.zeros(3, dtype=np.float32)
    for i in range(min(3, len(memory_only_usages))):
        state[i] = memory_only_usages[i]
    action, _ = model_memory.predict(state) """

    #state = memory_only_usages
    #print("state--Memory Only", state)
    #action, _ = model_memory.predict(state)


    print("state", state)

    state_np = np.array(state, dtype=np.float32)
    action, _ = model_energy.predict(state_np)

    # Memory usage prediction

    chosen_node = nodes[action].node if action < len(nodes) else nodes[0].node
    print("Chosen node:", chosen_node)
    return {"scheduled_node": chosen_node}

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "RL Scheduler API is running"}