
# Run this file with: (sudo) bash docker_build_latest.sh
# Before that, you might need to start dockerd with: sudo dockerd # Use `which dockerd` to find the path
# set -e

IMAGE_NAME="alim-slim"
DATE=$(date +%y-%m)
echo $DATE

docker rmi "statistician/$IMAGE_NAME:latest"
docker rmi "statistician/$IMAGE_NAME:$DATE"

docker build --no-cache --file ./Dockerfile --progress=plain -t "statistician/$IMAGE_NAME:latest" .
# docker build --file ./Dockerfile --progress=plain -t $IMAGE_NAME:latest .
# building with no cache since docker is unaware of changes in clode due to dynamic code like curl URL | bash etc.

# docker login --username statistician --password <password>
read -p "Do you want to push to the registry? (y/n): " answer
if [[ "$answer" =~ ^[Yy]$ ]] ; then
    docker push "statistician/$IMAGE_NAME:latest"
    docker tag "statistician/$IMAGE_NAME:latest" "statistician/$IMAGE_NAME:$DATE"
    docker push "statistician/$IMAGE_NAME:$DATE"
else
    echo "Push to registry aborted."
fi

echo "try it out using: docker run --rm -it statistician/$IMAGE_NAME:latest"
# Use this to clean instances: docker ps --all -q | xargs docker rm
# delete images: docker rmi -f $(docker images -q)
# docker ps --all -q | xargs docker rm; docker rmi -f $(docker images -q)
# docker run --rm -it alim-slim:latest /bin/bash hollywood
