import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

from v0_2 import MAA

print("--- Testing MAA Phase 1 Upgrades ---")
maa = MAA()
print("Version:", maa.version)
print("Status:", maa.status())
print("Agents with tools:", list(maa.registry._agents.keys()))

# Check tool injection
for agent_name, agent_obj in maa.registry._agents.items():
    assert agent_obj.tool_registry is not None, f"Agent {agent_name} missing tool_registry"
print("✅ Universal tool access verified for all 8 agents.")

print("--- Testing RunState ---")
from v0_2.core.run_state import RunState
state = RunState(objective="Test objective")
state.add_step(1, "Researcher", "Search topic", "prompt", "result output")
state.record_message("Researcher", "ALL", "Done research", "result")
saved_path = state.save()
print(f"Saved state to: {saved_path}")

loaded = RunState.load(state.run_id)
assert loaded is not None
assert loaded.objective == "Test objective"
assert len(loaded.steps) == 1
print("✅ Persistent RunState save/load verified.")

print("\n🎉 Phase 1 All Structural Checks PASSED!")

