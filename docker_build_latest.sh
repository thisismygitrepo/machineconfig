#!/bin/bash
#=======================================================================
# 🐳 DOCKER BUILD SCRIPT FOR SLIM IMAGE 🚀
#=======================================================================
# Run this file with: (sudo) bash docker_build_latest.sh
# Before that, you might need to start dockerd with: sudo dockerd # Use `which dockerd` to find the path
# set -e

IMAGE_NAME="alim-slim"
DATE=$(date +%y-%m)

echo """#=======================================================================
🚀 STARTING DOCKER BUILD | Building image ${IMAGE_NAME}:${DATE}
#=======================================================================
"""

#-----------------------------------------------------------------------
# 🧹 CLEANUP | Removing old docker images
#-----------------------------------------------------------------------
echo """#=======================================================================
🧹 CLEANUP | Removing old docker images
#=======================================================================
"""
docker rmi "statistician/$IMAGE_NAME:latest" --force
docker rmi "statistician/$IMAGE_NAME:$DATE" --force

#-----------------------------------------------------------------------
# 🏗️ BUILD | Creating new docker image
#-----------------------------------------------------------------------
echo """#=======================================================================
🏗️ BUILD | Creating new docker image
#=======================================================================
"""
docker build --no-cache --file ./Dockerfile --progress=plain -t "statistician/$IMAGE_NAME:latest" .
# building with no cache since docker is unaware of changes in code due to dynamic code like curl URL | bash etc.

#-----------------------------------------------------------------------
# 📝 STATUS | Showing current images
#-----------------------------------------------------------------------
echo """#=======================================================================
📝 STATUS | Current docker images
#=======================================================================
"""
docker images

#-----------------------------------------------------------------------
# 📤 REGISTRY | Push to docker registry
#-----------------------------------------------------------------------
echo """#=======================================================================
📤 REGISTRY | Push to docker registry
#=======================================================================
"""
read -p "❓ Do you want to push to the registry? (y/n): " answer
if [[ "$answer" =~ ^[Yy]$ ]] ; then
    echo """    ✅ PUSHING IMAGES | Uploading to docker registry
    """
    docker push "statistician/$IMAGE_NAME:latest"
    docker tag "statistician/$IMAGE_NAME:latest" "statistician/$IMAGE_NAME:$DATE"
    docker push "statistician/$IMAGE_NAME:$DATE"
else
    echo """    ❌ PUSH ABORTED | Registry upload canceled
    """
fi

echo """#=======================================================================
✨ FINISHED | Try it out using: docker run --rm -it statistician/$IMAGE_NAME:latest
#=======================================================================
"""

# 🧰 HELPFUL CLEANUP COMMANDS:
# Use this to clean instances: docker ps --all -q | xargs docker rm
# delete images: docker rmi -f $(docker images -q)
# docker ps --all -q | xargs docker rm; docker rmi -f $(docker images -q)
# docker run --rm -it statistician/alim-slim:latest /bin/bash hollywood
