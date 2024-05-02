
# Define the image name
$IMAGE_NAME = "alim-slim"
$FULL_NAME = ($IMAGE_NAME + ":latest")

# Build the Docker image
docker build --no-cache --file ./Dockerfile -t $FULL_NAME .

# Get the current date
$DATE = Get-Date -Format "yy-MM"
Write-Output $DATE

# Tag and push the Docker image with the date
docker tag $IMAGE_NAME:latest "statistician/$IMAGE_NAME:$DATE"
docker push "statistician/$IMAGE_NAME:$DATE"

# Tag and push the Docker image with the 'latest' tag
docker tag $IMAGE_NAME:latest "statistician/$IMAGE_NAME:latest"
docker push "statistician/$IMAGE_NAME:latest"

# Output the command to run the Docker image
Write-Output "try it out using: docker run -it $IMAGE_NAME:latest"
