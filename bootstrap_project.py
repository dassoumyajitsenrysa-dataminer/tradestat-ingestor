from pathlib import Path

PROJECT_NAME = "tradestat_ingestor"

STRUCTURE = [
    "src/tradestat_ingestor/config",
    "src/tradestat_ingestor/core",
    "src/tradestat_ingestor/tasks",
    "src/tradestat_ingestor/storage",
    "src/tradestat_ingestor/db",
    "src/tradestat_ingestor/utils",
    "scripts",
    "tests",
    "data/raw",
]

FILES = {
    "src/tradestat_ingestor/__init__.py": "",
    "src/tradestat_ingestor/config/__init__.py": "",
    "src/tradestat_ingestor/config/settings.py": "",
    "src/tradestat_ingestor/core/__init__.py": "",
    "src/tradestat_ingestor/tasks/__init__.py": "",
    "src/tradestat_ingestor/storage/__init__.py": "",
    "src/tradestat_ingestor/db/__init__.py": "",
    "src/tradestat_ingestor/utils/__init__.py": "",
    "scripts/__init__.py": "",
    ".env.example": "",
    "README.md": "# tradestat_ingestor\n",
    ".gitignore": "data/\n.env\n__pycache__/\n",
}

def create_structure():
    for folder in STRUCTURE:
        Path(folder).mkdir(parents=True, exist_ok=True)

    for file, content in FILES.items():
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

if __name__ == "__main__":
    create_structure()
    print("✅ Project structure created successfully")
