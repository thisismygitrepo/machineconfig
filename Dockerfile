
FROM python:3.11-slim
# TODO: use a non-bloated os like alpine and remove the venv

RUN apt-get update && apt-get install -y sudo  # sudo is needed for the setup_linux script
RUN apt-get install -y xz-utils  # nix needs this to untar the ball

WORKDIR /app

COPY ./src/machineconfig/setup_linux /app/setup_linux
RUN chmod +x /app/setup_linux/*
ENV package_manager="apt"
RUN /bin/bash /app/setup_linux/apps.sh
RUN /bin/bash /app/setup_linux/apps_dev.sh
RUN /bin/bash /app/setup_linux/ve.sh
# ENV CROCODILE_EXRA="full"
RUN /bin/bash /app/setup_linux/repos.sh
RUN /bin/bash /app/setup_linux/symlinks.sh
RUN /bin/bash /app/setup_linux/devapps.sh


# CMD ["/bin/bash"]
