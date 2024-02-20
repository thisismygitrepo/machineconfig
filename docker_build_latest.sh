
# set -e

IMAGE_NAME="alim-slim"
docker build --no-cache --file ./Dockerfile --progress=plain -t $IMAGE_NAME:latest .
# building with no cache since docker is unaware of changes in clode due to dynamic code like curl URL | bash etc.

DATE=$(date +%y-%m)
echo $DATE

docker tag $IMAGE_NAME:latest "statistician/$IMAGE_NAME:$DATE"

# docker login --username statistician --password <password>
docker push "statistician/$IMAGE_NAME:$DATE"

echo "try it out using: docker run -it $IMAGE_NAME:latest"
# Use this to clean space: docker ps --all -q | xargs docker rm
