from github import Github
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
    commits = repo.get_commits(since=since_datetime)
    return commits

def get_prs(repo_name: str, since_datetime):
    repo = GIT_CLIENT.get_repo(repo_name)
    prs = repo.get_pulls(state='all', sort='created', direction='desc')
    recent_prs = [pr for pr in prs if pr.created_at >= since_datetime]
    return recent_prs

def get_last_release(repo_name: str):
    repo = GIT_CLIENT.get_repo(repo_name)
    releases = repo.get_releases()
    if releases.totalCount == 0:
        return None
    return releases[0]

def get_last_x_commits(repo_name: str, x: int = 5):
    repo = GIT_CLIENT.get_repo(repo_name)
    commits = repo.get_commits()
    return commits[:x]