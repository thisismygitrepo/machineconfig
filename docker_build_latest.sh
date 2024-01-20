
docker build -t alim:latest .

DATE=$(date +%y-%m)
echo $DATE

docker tag alim:latest "statistician/alim-slim:$DATE"

# docker login --username statistician --password <password>
docker push "statistician/alim-slim:$DATE"
