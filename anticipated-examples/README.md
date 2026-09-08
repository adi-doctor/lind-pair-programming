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