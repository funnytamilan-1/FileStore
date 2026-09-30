def __getattr__(name):
    if name in {"Database","MongoDB"}:
        from .database import Database
        return Database
    raise AttributeError(name)
__all__=["Database","MongoDB"]
