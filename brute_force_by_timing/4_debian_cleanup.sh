GIT_REPO_PATH="$(git rev-parse --show-toplevel)"

docker-compose down

sudo apt-get purge -y docker.io docker-compose
sudo apt-get autoremove -y

cd /
rm -rf "$GIT_REPO_PATH"
