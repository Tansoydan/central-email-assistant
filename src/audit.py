import os
import json


def ensure_runs_dir() -> None:
    os.makedirs("runs", exist_ok=True)


def log_jsonl(path: str, event: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
