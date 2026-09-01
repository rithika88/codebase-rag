import os
import shutil
from git import Repo


BASE_DIR = "temp_repositories"


def clone_repository(github_url: str, repository_id: str) -> str:
    os.makedirs(BASE_DIR, exist_ok=True)

    repo_path = os.path.join(BASE_DIR, repository_id)

    # Remove existing copy if it exists
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    Repo.clone_from(github_url, repo_path)

    return repo_path