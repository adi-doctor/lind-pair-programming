Lind Pair Programming Interview

SSH keys let you push and pull securely without entering credentials repeatedly.

1. ssh-keygen -t ed25519 -C "your_email@example.com"
2. eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519


…or create a new repository on the command line
echo "# lind-pair-programming" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/adi-doctor/lind-pair-programming.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/adi-doctor/lind-pair-programming.git
git branch -M main
git push -u origin main



Test authentication
-------------------
ssh -T git@github.com
git remote -v
Change to SSH URL
git remote set-url origin git@github.com:USERNAME/REPO.git

(.venv) andrewhudsonmd@Andrews-Mac-Studio lind-pair-programming-interview % git remote set-url origin git@github.com:adi-doctor/https://github.com/adi-doctor/lind-pair-programming.git
(.venv) andrewhudsonmd@Andrews-Mac-Studio lind-pair-programming-interview % git push -u origin main
fatal: protocol 'git@github.com:adi-doctor/https' is not supported
(.venv) andrewhudsonmd@Andrews-Mac-Studio lind-pair-programming-interview % git remote set-url origin git@github.com:adi-doctor/lind-pair-programming.git                              
(.venv) andrewhudsonmd@Andrews-Mac-Studio lind-pair-programming-interview % git push -u origin main 