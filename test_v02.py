from v0_2 import MAA

maa = MAA()

print("Version:", maa.version)
print("Status:", maa.status())
print("\nAgents:", maa.list_agents())
print("Tools:", maa.tools.list_tools())

print("\n✅ Structure is cleaner.")