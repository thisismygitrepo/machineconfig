
set -e

docker build --no-cache -t alim-slim:latest .
# building with no cache since docker is unaware of changes in clode due to dynamic code like curl URL | bash etc.

DATE=$(date +%y-%m)
echo $DATE

docker tag alim-slim:latest "statistician/alim-slim:$DATE"

# docker login --username statistician --password <password>
docker push "statistician/alim-slim:$DATE"

# try it out