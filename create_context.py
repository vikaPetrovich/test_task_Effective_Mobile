from pathlib import Path

# Скрипт создаёт txt-файл с контекстом проекта:
# 1. дерево папок и файлов
# 2. содержимое важных текстовых файлов
#
# Запускать из корня проекта:
# python create_project_context.py

OUTPUT_FILE = "project_context.txt"

EXCLUDED_DIRS = {
    "venv",
    ".venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
}

EXCLUDED_FILES = {
    "project_context.txt",
    ".env",
    ".env.local",
    ".env.prod",
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".txt",
    ".md",
    ".toml",
    ".ini",
    ".yml",
    ".yaml",
    ".json",
    ".env.example",
}

MAX_FILE_SIZE = 80_000  # чтобы случайно не положить огромный файл


def should_skip_path(path: Path) -> bool:
    parts = set(path.parts)

    if parts & EXCLUDED_DIRS:
        return True

    if path.name in EXCLUDED_FILES:
        return True

    return False


def is_allowed_file(path: Path) -> bool:
    if path.name == ".env.example":
        return True

    return path.suffix in ALLOWED_EXTENSIONS


def build_tree(root: Path) -> str:
    lines = []

    for path in sorted(root.rglob("*")):
        if should_skip_path(path):
            continue

        relative = path.relative_to(root)
        depth = len(relative.parts) - 1
        indent = "  " * depth

        if path.is_dir():
            lines.append(f"{indent}{path.name}/")
        else:
            lines.append(f"{indent}{path.name}")

    return "\n".join(lines)


def collect_file_contents(root: Path) -> str:
    blocks = []

    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue

        if should_skip_path(path):
            continue

        if not is_allowed_file(path):
            continue

        if path.stat().st_size > MAX_FILE_SIZE:
            continue

        relative = path.relative_to(root)

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="cp1251")
            except UnicodeDecodeError:
                continue

        blocks.append(
            f"\n\n{'=' * 80}\n"
            f"FILE: {relative}\n"
            f"{'=' * 80}\n\n"
            f"{content}"
        )

    return "".join(blocks)


def main() -> None:
    root = Path.cwd()
    output_path = root / OUTPUT_FILE

    tree = build_tree(root)
    contents = collect_file_contents(root)

    result = (
        f"PROJECT CONTEXT\n"
        f"Root: {root}\n\n"
        f"{'=' * 80}\n"
        f"PROJECT TREE\n"
        f"{'=' * 80}\n\n"
        f"{tree}\n"
        f"{contents}\n"
    )

    output_path.write_text(result, encoding="utf-8")

    print(f"Context file created: {output_path}")


if __name__ == "__main__":
    main()
