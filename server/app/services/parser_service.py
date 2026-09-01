import os


# --------------------------------------------------
# Files that are useful for codebase understanding
# --------------------------------------------------

ALLOWED_EXTENSIONS = {
    # Python
    ".py",

    # JavaScript / TypeScript
    ".js",
    ".jsx",
    ".ts",
    ".tsx",

    # Java / JVM
    ".java",
    ".kt",
    ".kts",

    # C / C++
    ".c",
    ".cpp",
    ".h",
    ".hpp",

    # Other programming languages
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",

    # Web
    ".html",
    ".css",
    ".scss",

    # Database
    ".sql",

    # Documentation
    ".md",

    # Configuration
    ".yaml",
    ".yml",
    ".json",

    # Shell
    ".sh",
}


# --------------------------------------------------
# Useful files without normal extensions
# --------------------------------------------------

ALLOWED_FILENAMES = {
    "README",
    "README.txt",
    "README.md",
    "Dockerfile",
    "Makefile",
    "LICENSE",
}


# --------------------------------------------------
# Directories that should NEVER be indexed
# --------------------------------------------------

IGNORED_DIRECTORIES = {
    ".git",
    ".github",

    # JavaScript
    "node_modules",

    # Python
    "venv",
    ".venv",
    "__pycache__",

    # IDE
    ".idea",
    ".vscode",

    # Build output
    "dist",
    "build",
    "coverage",
    "target",

    # Python packaging
    ".pytest_cache",
    ".mypy_cache",

    # Other common generated directories
    "vendor",
    "bin",
    "obj",
}


# --------------------------------------------------
# Files that should NEVER be indexed
# --------------------------------------------------

IGNORED_FILES = {
    # Dependency lock files
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",

    # Python dependency files
    "poetry.lock",

    # OS files
    ".DS_Store",

    # Minified / generated files
    "robots.txt",
}


# --------------------------------------------------
# Check whether a file is useful
# --------------------------------------------------

def is_allowed_file(filename: str) -> bool:
    """
    Determine whether a file should be indexed.
    """

    # Explicitly ignored files
    if filename in IGNORED_FILES:
        return False

    # Explicitly allowed filenames
    if filename in ALLOWED_FILENAMES:
        return True

    # Check extension
    extension = os.path.splitext(filename)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# --------------------------------------------------
# Find source files
# --------------------------------------------------

def get_source_files(repo_path: str):
    """
    Find useful source and documentation files
    inside a repository.
    """

    source_files = []

    for root, directories, files in os.walk(repo_path):

        # Remove ignored directories from traversal
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in files:

            # Ignore unwanted files
            if not is_allowed_file(filename):
                continue

            file_path = os.path.join(
                root,
                filename
            )

            source_files.append(file_path)

    return source_files


# --------------------------------------------------
# Chunk source files
# --------------------------------------------------

def chunk_code(
    file_path: str,
    repo_path: str,
    chunk_size: int = 100
):
    """
    Read a source file and divide it into
    approximately `chunk_size` line chunks.
    """

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            lines = file.readlines()

    except Exception as e:

        print(
            f"Could not read {file_path}: {e}"
        )

        return []

    chunks = []

    # Convert absolute path into repository-relative path
    relative_path = os.path.relpath(
        file_path,
        repo_path
    )

    # Create chunks
    for start in range(
        0,
        len(lines),
        chunk_size
    ):

        end = min(
            start + chunk_size,
            len(lines)
        )

        content = "".join(
            lines[start:end]
        )

        # Ignore completely empty chunks
        if not content.strip():
            continue

        chunks.append({
            "file_path": relative_path,
            "content": content,
            "start_line": start + 1,
            "end_line": end
        })

    return chunks