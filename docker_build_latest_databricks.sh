#!/bin/bash
#=======================================================================
# 🐳 DOCKER BUILD SCRIPT FOR DATABRICKS IMAGE 🚀
#=======================================================================
# set -e

IMAGE_NAME="alim-databricks"
DATE=$(date +%y-%m)

echo """
#=======================================================================
🚀 STARTING DOCKER BUILD | Building Databricks image ${IMAGE_NAME}:${DATE}
#=======================================================================
"""

#-----------------------------------------------------------------------
# 🏗️ BUILD | Creating new docker image
#-----------------------------------------------------------------------
echo """
#=======================================================================
🏗️ BUILD | Creating new docker image
#=======================================================================
"""
docker build --no-cache --file=./Dockerfile_databricks --progress=plain -t $IMAGE_NAME:latest .
# building with no cache since docker is unaware of changes in code due to dynamic code like curl URL | bash etc.

#-----------------------------------------------------------------------
# 🔖 TAG | Creating version tag
#-----------------------------------------------------------------------
echo """
#=======================================================================
🔖 TAG | Creating version tag ${DATE}
#=======================================================================
"""
docker tag $IMAGE_NAME:latest "statistician/$IMAGE_NAME:$DATE"

#-----------------------------------------------------------------------
# 📤 REGISTRY | Push to docker registry
#-----------------------------------------------------------------------
echo """
#=======================================================================
📤 REGISTRY | Pushing to docker registry
#=======================================================================
"""
# docker login --username statistician --password <password>
docker push "statistician/$IMAGE_NAME:$DATE"

echo """
#=======================================================================
✨ FINISHED | Try it out using: docker run -it ${IMAGE_NAME}:${DATE}
#=======================================================================
"""
