
# FROM python:3.13.7-alpine3.19
# FROM python:3.13.7-bookworm
# FROM ubuntu:jammy-20240227
# FROM python:3.13.9-slim
FROM debian:bookworm-slim


# Set bash as default shell
# as per https://github.com/moby/moby/issues/7281
SHELL ["/bin/bash", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && apt-get install -y bash sudo xz-utils

WORKDIR /app

COPY ./src/machineconfig/setup_linux /app/setup_linux
RUN chmod +x /app/setup_linux/*

ENV package_manager="nala"
RUN /app/setup_linux/apps.sh


# # =================== INSTALL DOCKER SO WE RUN DATABASES IN CONTAINERS ===================
# RUN chmod +x $HOME/code/machineconfig/src/machineconfig/jobs/python_custom_installers/scripts/linux/docker.sh
# RUN bash     $HOME/code/machineconfig/src/machineconfig/jobs/python_custom_installers/scripts/linux/docker.sh

RUN nala install -y redis-tools
# this gives redis-cli, which is needed to talk to the redis-server that is running in the docker container.
# same for pgsq, when the server runs, we will need the client to talk to it.
RUN nala install -y postgresql-client

# RUN cd $HOME && \
#     mkdir code && \
#     cd $HOME/code && \
#     git clone https://github.com/thisismygitrepo/crocodile.git --depth 4 && \
#     git clone https://github.com/thisismygitrepo/machineconfig --depth 4 && \
#     cd $HOME/code/machineconfig && \
    # /root/.local/bin/uv pip install -e . && \


WORKDIR /root/code/machineconfig
COPY . .
COPY ./src/machineconfig/settings/shells/ipy/profiles/default/startup/playext.py /root/.ipython/profile_default/startup/playext.py

RUN /root/.local/bin/uv sync --no-dev
RUN /root/.local/bin/uv run --no-dev --project $HOME/code/machineconfig python -m fire machineconfig.profile.create main
RUN /root/.local/bin/uv run --no-dev --project $HOME/code/machineconfig install essentials


RUN touch /root/.bash_history
# McFly complains about missing history file
RUN rm -rfd /root/tmp_results
# This directory is full of tmp installers files. (200MB)
# RUN apt-get clean && \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/apt/archives/* /var/log/* /usr/share/doc /usr/share/man /usr/share/info /usr/share/locale

RUN /root/.local/bin/uv clean && \
    rm -rfd /root/.cache/pip && \
    rm -rfd /app
# This saves 200MB


WORKDIR /root
CMD ["/usr/bin/bash"]
# python image defaults to python as the command
