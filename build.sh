
f upgrade
git commit -am "new release"
git push
. ./jobs/shell/docker_build_and_publish.sh slim
. ./jobs/shell/docker_build_and_publish.sh ai

