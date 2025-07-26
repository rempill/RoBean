import time

_cache={
    "beans":None,
    "last_updated":0.0
}

cache_duration=60*60 #1 hour

def get_cached_beans():
    if _cache["beans"] and (time.time()-_cache["last_updated"]) < cache_duration:
        return _cache["beans"]
    return None

def set_cached_beans(beans):
    _cache["beans"] = beans
    _cache["last_updated"] = time.time()

def get_last_updated():
    return _cache["last_updated"]