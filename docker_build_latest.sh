#!/bin/bash
# 🐳 Docker Build Script for Slim Image 🚀
# Run this file with: (sudo) bash docker_build_latest.sh
# Before that, you might need to start dockerd with: sudo dockerd # Use `which dockerd` to find the path
# set -e

IMAGE_NAME="alim-slim"
DATE=$(date +%y-%m)
echo $DATE

# 🧹 Cleanup old images
docker rmi "statistician/$IMAGE_NAME:latest" --force
docker rmi "statistician/$IMAGE_NAME:$DATE" --force

# 🏗️ Build new image
docker build --no-cache --file ./Dockerfile --progress=plain -t "statistician/$IMAGE_NAME:latest" .
# building with no cache since docker is unaware of changes in clode due to dynamic code like curl URL | bash etc.

# 📝 Show current images
docker images

# 📤 Push to registry prompt
read -p "Do you want to push to the registry? (y/n): " answer
if [[ "$answer" =~ ^[Yy]$ ]] ; then
    docker push "statistician/$IMAGE_NAME:latest"
    docker tag "statistician/$IMAGE_NAME:latest" "statistician/$IMAGE_NAME:$DATE"
    docker push "statistician/$IMAGE_NAME:$DATE"
else
    echo "Push to registry aborted."
fi

echo "✨ try it out using: docker run --rm -it statistician/$IMAGE_NAME:latest"

# 🧰 Helpful cleanup commands:
# Use this to clean instances: docker ps --all -q | xargs docker rm
# delete images: docker rmi -f $(docker images -q)
# docker ps --all -q | xargs docker rm; docker rmi -f $(docker images -q)
# docker run --rm -it statistician/alim-slim:latest /bin/bash hollywood
