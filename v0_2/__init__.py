from v0_2.version import __version__, __status__

__all__ = ["MAA", "__version__", "__status__"]

# Deferred import to avoid circular dependency:
# core.agent -> v0_2.core.model_router -> v0_2.__init__ -> v0_2.core.maa -> v0_2.core.registry -> core.agent
def __getattr__(name):
    if name == "MAA":
        from v0_2.core.maa import MAA
        return MAA
    raise AttributeError(f"module 'v0_2' has no attribute {name!r}")