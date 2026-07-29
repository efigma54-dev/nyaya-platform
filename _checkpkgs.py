import importlib.util
for name in ["email_validator", "orjson", "rank_bm25"]:
    spec = importlib.util.find_spec(name)
    print(f"{name}: {'ok' if spec else 'MISSING'}")
