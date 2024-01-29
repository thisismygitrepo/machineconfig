
set -e

IMAGE_NAME="alim-databricks"
docker build --no-cache --file=./Dockerfile_databricks --progress=plain -t $IMAGE_NAME:latest .
# building with no cache since docker is unaware of changes in clode due to dynamic code like curl URL | bash etc.

DATE=$(date +%y-%m)
echo $DATE

docker tag $IMAGE_NAME:latest "statistician/$IMAGE_NAME:$DATE"

# docker login --username statistician --password <password>
docker push "statistician/$IMAGE_NAME:$DATE"

# try it out: docker run -it $IMAGE_NAME:latest
