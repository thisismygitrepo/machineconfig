#!/bin/bash

# Force user to specify variant
if [ $# -eq 0 ]; then
    echo "❌ ERROR: Please specify a variant: 'slim' or 'ai'"
    echo "Usage: $0 <variant>"
    echo "Example: $0 slim"
    exit 1
fi

VARIANT=$1

# Validate variant
if [ "$VARIANT" != "slim" ] && [ "$VARIANT" != "ai" ]; then
    echo "❌ ERROR: Invalid variant '$VARIANT'. Must be 'slim' or 'ai'"
    exit 1
fi

IMAGE_NAME="machineconfig-$VARIANT"
DOCKERFILE_PATH="./jobs/dockers/Dockerfile_$VARIANT"
DATE=$(date +%y-%m)

# curl -s -I https://api.github.com/repos/jqlang/jq/releases/latest | grep -E "(status|x-ratelimit)"
#

echo """🚀 STARTING DOCKER BUILD | Building image ${IMAGE_NAME}:${DATE} """
echo """🧹 CLEANUP | Removing old docker images"""
docker rmi "statistician/$IMAGE_NAME:latest" --force
docker rmi "statistician/$IMAGE_NAME:$DATE" --force

echo """🏗️ BUILD | Creating new docker image"""
docker build --no-cache --file "$DOCKERFILE_PATH" --progress=plain -t "statistician/$IMAGE_NAME:latest" .
# building with no cache since docker is unaware of changes in code due to dynamic code like curl URL | bash etc.


echo """✨ FINISHED | Try it out using: docker run --rm -it statistician/$IMAGE_NAME:latest
🧰 HELPFUL CLEANUP COMMANDS:
Use this to clean instances: docker ps --all -q | xargs docker rm
Delete images: docker rmi -f \$(docker images -q)
docker ps --all -q | xargs docker rm; docker rmi -f \$(docker images -q)
docker run --rm -it statistician/$IMAGE_NAME:latest /bin/bash hollywood
"""

echo """📝 STATUS | Current docker images"""
docker images

echo """📤 REGISTRY | Push to docker registry"""
printf "❓ Do you want to push to the registry? (y/n): "
read answer
case "$answer" in
    [Yy]* )
        echo """    ✅ PUSHING IMAGES | Uploading to docker registry
    """
        docker push "statistician/$IMAGE_NAME:latest"
        docker tag "statistician/$IMAGE_NAME:latest" "statistician/$IMAGE_NAME:$DATE"
        docker push "statistician/$IMAGE_NAME:$DATE"
        ;;
    * )
        echo """    ❌ PUSH ABORTED | Registry upload canceled"""
        echo """    You can push later using:
    docker push statistician/$IMAGE_NAME:latest
    docker tag statistician/$IMAGE_NAME:latest statistician/$IMAGE_NAME:$DATE
    docker push statistician/$IMAGE_NAME:$DATE
    """
        ;;
esac

