from pathlib import Path


def mkdirs(path: Path) -> Path:
    path.mkdir(exist_ok=True, parents=True)
    return path
