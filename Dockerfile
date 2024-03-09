
# TODO: use a non-bloated os like alpine and remove the venv
# FROM python:3.11.7-alpine3.19
FROM python:3.11-slim
# FROM python:3.11.7-bookworm
# FROM ubuntu:jammy-20240227

# Set bash as default shell
# as per https://github.com/moby/moby/issues/7281
SHELL ["/bin/bash", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && apt-get install -y bash sudo xz-utils

WORKDIR /app

COPY ./src/machineconfig/setup_linux /app/setup_linux
RUN chmod +x /app/setup_linux/*

ENV package_manager="apt"
RUN /app/setup_linux/apps.sh
RUN /app/setup_linux/apps_dev.sh
RUN /app/setup_linux/ve.sh
# ENV CROCODILE_EXRA="full"
RUN /app/setup_linux/repos.sh
RUN /app/setup_linux/symlinks.sh
RUN /app/setup_linux/devapps.sh

RUN touch /root/.bash_history  # McFly complains about missing history file


CMD ["/bin/bash"]
