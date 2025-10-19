
# FROM python:3.13.7-alpine3.19
# FROM python:3.13.7-bookworm
# FROM ubuntu:jammy-20240227
# FROM python:3.13.9-slim
FROM debian:bookworm-slim


# Set bash as default shell
SHELL ["/bin/bash", "-lc"]
# ENV SHELL=/bin/bash
RUN apt-get update && apt-get install -y bash sudo xz-utils unzip curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
WORKDIR /app
COPY . /app
RUN /root/.local/bin/uv tool install --python 3.14 --editable .
# RUN /root/.local/bin/uv tool install --python 3.14 machineconfig>=6.57

RUN /root/.local/bin/devops install --group ESSENTIAL_SYSTEM
RUN /root/.local/bin/devops install --group ESSENTIAL
RUN /root/.local/bin/devops config public --method symlink --which all
RUN /root/.local/bin/devops config shell

RUN touch /root/.bash_history
# McFly complains about missing history file
RUN rm -rfd /root/tmp_results
# This directory is full of tmp installers files. (200MB)
# RUN apt-get clean && \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/apt/archives/* /var/log/* /usr/share/doc /usr/share/man /usr/share/info /usr/share/locale

RUN /root/.local/bin/uv clean && \
    rm -rfd /root/.cache/pip && \
    npm cache clean --force

WORKDIR /root
CMD ["/usr/bin/bash"]
# python image defaults to python as the command
