
# FROM python:3.11.7-alpine3.19
# FROM python:3.11.7-bookworm
# FROM ubuntu:jammy-20240227
# FROM python:3.11.9-slim
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
RUN /app/setup_linux/apps_dev.sh

# RUN /app/setup_linux/ve.sh
# ENV PATH="/root/.local/bin:${PATH}"
RUN /root/.local/bin/uv venv $HOME/venvs/ve --python 3.11 --python-preference only-managed
# Warning: does not come with pip
RUN source $HOME/venvs/ve/bin/activate && \
    /root/.local/bin/uv pip install --upgrade pip

# ENV CROCODILE_EXRA="full"
# RUN /app/setup_linux/repos.sh
RUN cd $HOME && \
    mkdir code && \
    cd $HOME/code && \
    git clone https://github.com/thisismygitrepo/crocodile.git --depth 4 && \
    git clone https://github.com/thisismygitrepo/machineconfig --depth 4 && \
    cd $HOME/code/crocodile && \
    source $HOME/venvs/ve/bin/activate && \
    /root/.local/bin/uv pip install -e . && \
    cd $HOME/code/machineconfig && \
    /root/.local/bin/uv pip install -e . && \
    echo "Finished setting up repos"

RUN /app/setup_linux/symlinks.sh
RUN /app/setup_linux/devapps.sh

COPY ./src/machineconfig/settings/shells/ipy/profiles/default/startup/playext.py /root/.ipython/profile_default/startup/playext.py


RUN touch /root/.bash_history
# McFly complains about missing history file
RUN rm -rfd /root/tmp_results
# This directory is full of tmp installers files. (200MB)
# RUN apt-get clean && \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/apt/archives/* /var/log/* /usr/share/doc /usr/share/man /usr/share/info /usr/share/locale

RUN rm -rfd /root/.cache/pip && \
    rm -rfd /root/.cache/uv && \
    rm -rfd /app
# This saves 200MB


WORKDIR /root
CMD ["/usr/bin/bash"]
# python image defaults to python as the command
