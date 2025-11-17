from github import Github
from github.Commit import Commit
from main.github_tools.token import GIT_AUTH_TOKEN

GIT_CLIENT = Github(GIT_AUTH_TOKEN)

def get_last_commit(repo_name: str, branch: str = "main"):
    repo = GIT_CLIENT.get_repo(repo_name)
    branch_ref = repo.get_branch(branch)
    return branch_ref.commit

def get_repo_info(repo_name: str):
    repo = GIT_CLIENT.get_repo(repo_name)
    return {
        "name": repo.name,
        "description": repo.description,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "open_issues": repo.open_issues_count,
        "default_branch": repo.default_branch,
    }
    
def get_commits_since(repo_name: str, since_datetime):
    repo = GIT_CLIENT.get_repo(repo_name)
    if since_datetime is None:
        commits = repo.get_commits()
    else:
        commits = repo.get_commits(since=since_datetime)
    return commits

def get_prs(repo_name: str):
    repo = GIT_CLIENT.get_repo(repo_name)
    prs = repo.get_pulls(state='all', sort='created', direction='desc')
    return prs.totalCount
def get_last_release(repo_name: str):
    repo = GIT_CLIENT.get_repo(repo_name)
    releases = repo.get_releases()
    if releases.totalCount == 0:
        return None
    return releases[0]

def get_last_x_commits(repo_name: str, x: int = 5) -> list[Commit]:
    repo = GIT_CLIENT.get_repo(repo_name)
    commits = repo.get_commits()

    # PyGithub gibt die neuesten Commits zuerst zurück!
    commit_list: list[Commit] = []
    for i, commit in enumerate(commits):
        if i >= x:
            break
        commit_list.append(commit)

    return commit_list
