import os
import subprocess
import sys

# Exclude by path segment name, anywhere in the tree
EXCLUDED_NAMES = {"venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", "node_modules", "dist"}

MAX_DEPTH = 5


def repo_root_from_git():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out if out else None
    except Exception:
        return None


def script_parent():
    # Parent of this file (…/scripts) → project root one level up
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def resolve_root(cli_path: str | None) -> str:
    if cli_path:
        return os.path.abspath(cli_path)
    git_root = repo_root_from_git()
    return git_root or script_parent()


def is_excluded(path: str) -> bool:
    # Exclude if ANY segment matches a name in EXCLUDED_NAMES
    return any(seg in EXCLUDED_NAMES for seg in path.replace("\\", "/").split("/"))


def generate_tree(path: str, prefix: str = "", depth: int = 0, max_depth: int = MAX_DEPTH):
    if depth > max_depth:
        return []

    try:
        entries = sorted(os.listdir(path), key=str.lower)
    except Exception as e:
        return [f"{prefix}⚠️ [Error reading {path}]: {e}"]

    # Filter entries that are excluded (by segment) before recursing
    entries = [e for e in entries if not is_excluded(e)]

    tree = []
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        tree.append(f"{prefix}{connector}{entry}")
        if os.path.isdir(full_path) and not is_excluded(full_path):
            extension = "    " if i == len(entries) - 1 else "│   "
            tree.extend(generate_tree(full_path, prefix + extension, depth + 1, max_depth))
    return tree


if __name__ == "__main__":
    # Optional: python scripts/generate_tree.py [START_PATH] [MAX_DEPTH]
    start_path = sys.argv[1] if len(sys.argv) > 1 else None
    if len(sys.argv) > 2:
        try:
            MAX_DEPTH = int(sys.argv[2])
        except ValueError:
            pass

    root = resolve_root(start_path)
    tree_lines = [os.path.basename(root) or root] + generate_tree(root)
    out_path = os.path.join(root, "tree.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tree_lines))
    print(f"✅ Directory tree written to {out_path}")
