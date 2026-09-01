import os


ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".md",
    ".sql",
    ".sh",
}

# Files without extensions that are useful for understanding a project
ALLOWED_FILENAMES = {
    "README",
    "README.txt",
    "README.md",
    "Dockerfile",
    "Makefile",
    "LICENSE",
    ".gitignore",
}


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "coverage",
    "target",
}


def is_allowed_file(filename: str) -> bool:
    """
    Check whether a file should be processed.
    """

    if filename in ALLOWED_FILENAMES:
        return True

    extension = os.path.splitext(filename)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def get_source_files(repo_path: str):
    """
    Find useful source/documentation files in a repository.
    """

    source_files = []

    for root, directories, files in os.walk(repo_path):

        # Prevent traversal into ignored directories
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in files:

            if is_allowed_file(filename):

                file_path = os.path.join(
                    root,
                    filename
                )

                source_files.append(file_path)

    return source_files


def chunk_code(
    file_path: str,
    repo_path: str,
    chunk_size: int = 100
):
    """
    Read a file and split it into chunks.

    Each chunk contains approximately
    `chunk_size` lines.
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

        print(f"Could not read {file_path}: {e}")

        return []

    chunks = []

    relative_path = os.path.relpath(
        file_path,
        repo_path
    )

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

        chunks.append({
            "file_path": relative_path,
            "content": content,
            "start_line": start + 1,
            "end_line": end
        })

    return chunks