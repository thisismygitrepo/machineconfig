
# FROM python:3.13.7-alpine3.19
# FROM python:3.13.7-bookworm
# FROM ubuntu:jammy-20240227
# FROM python:3.13.9-slim
FROM debian:bookworm-slim


# Set bash as default shell
# as per https://github.com/moby/moby/issues/7281
SHELL ["/bin/bash", "-c"]
ENV SHELL=/bin/bash
RUN apt-get update && apt-get install -y bash sudo xz-utils curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh


WORKDIR /root/code/machineconfig
COPY . .

RUN /root/.local/bin/uv sync --no-dev
RUN /root/.local/bin/uv run --no-dev --project $HOME/code/machineconfig devops install --group ESSENTIAL_SYSTEM
RUN /root/.local/bin/uv run --no-dev --project $HOME/code/machineconfig devops install --group ESSENTIAL
RUN /root/.local/bin/uv run --no-dev --project $HOME/code/machineconfig devops config public --method symlink --which all
RUN /root/.local/bin/uv run --no-dev --project $HOME/code/machineconfig devops config shell reference

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
