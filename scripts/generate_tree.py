import os

# Folders to exclude from tree
EXCLUDED_DIRS = {
    "venv",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "media",
    "dist",
    "app/components/node_modules",
    "app/components/dist",
}


def generate_tree(path=".", prefix="", depth=0, max_depth=3):
    if depth > max_depth:
        return []

    try:
        entries = sorted(
            [e for e in os.listdir(path) if e not in EXCLUDED_DIRS],
            key=lambda s: s.lower(),
        )
    except Exception as e:
        return [f"{prefix}⚠️ [Error reading {path}]: {e}"]

    tree = []
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        tree.append(f"{prefix}{connector}{entry}")
        if os.path.isdir(full_path):
            extension = "    " if i == len(entries) - 1 else "│   "
            tree.extend(
                generate_tree(full_path, prefix + extension, depth + 1, max_depth)
            )
    return tree


if __name__ == "__main__":
    tree_lines = generate_tree(".")
    tree_string = "\n".join(tree_lines)
    with open("tree.txt", "w", encoding="utf-8") as f:
        f.write(tree_string)
    print("✅ Directory tree written to tree.txt")
