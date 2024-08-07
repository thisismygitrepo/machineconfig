
# Run this file with: (sudo) bash docker_build_latest.sh
# Before that, you might need to start dockerd with: sudo dockerd # Use `which dockerd` to find the path
# set -e

IMAGE_NAME="alim-slim"
# IMAGE_NAME="alim-full"
DATE=$(date +%y-%m)
echo $DATE

docker build --no-cache --file ./Dockerfile --progress=plain -t $IMAGE_NAME:latest .
# building with no cache since docker is unaware of changes in clode due to dynamic code like curl URL | bash etc.

docker tag $IMAGE_NAME:latest "statistician/$IMAGE_NAME:$DATE"
# docker login --username statistician --password <password>
docker push "statistician/$IMAGE_NAME:$DATE"

docker tag $IMAGE_NAME:latest "statistician/$IMAGE_NAME:latest"
docker push "statistician/$IMAGE_NAME:latest"

echo "try it out using: docker run -it $IMAGE_NAME:latest"
# Use this to clean space: docker ps --all -q | xargs docker rm
# docker run --rm -it alim-slim:latest /bin/bash hollywood
