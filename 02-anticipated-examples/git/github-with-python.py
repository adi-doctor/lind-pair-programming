import os
from git import Repo

repo_dir = "/tmp/admin-sync-repo"
ssh_url = "git@github.com:adi-doctor/lind-pair-programming.git"

# Explicitly specify the SSH key path
ssh_cmd = 'ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=accept-new'

# Clone repository over SSH
repo = Repo.clone_from(
    ssh_url,
    repo_dir,
    env={"GIT_SSH_COMMAND": ssh_cmd}
)

# Perform administrative file synchronization (e.g., standardizing .github/workflows)
workflow_file = os.path.join(repo_dir, ".github", "workflows", "ci.yml")
os.makedirs(os.path.dirname(workflow_file), exist_ok=True)
with open(workflow_file, "w") as f:
    f.write("name: Standard CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n")

# Commit and push changes back over SSH
repo.git.add(A=True)
repo.index.commit("chore: update central CI workflow across fleet")
origin = repo.remote(name="origin")
origin.push()