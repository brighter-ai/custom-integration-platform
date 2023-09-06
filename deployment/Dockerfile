FROM python:3.10.10 as base

RUN apt update && apt install --no-install-recommends -y ffmpeg


COPY /deployment/requirements.txt /root/requirements.txt
RUN python3.10 -m pip install -r /root/requirements.txt

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
FROM base as development

ARG DEV_USER
ARG DEV_USER_ID
ARG DEV_USER_GID
ARG DEV_PASSWORD

RUN apt update && apt install -y --no-install-recommends apt-utils \
    openssh-server \
    openssl \
    nano \
    vim \
    sudo \
    less \
    git-lfs

RUN if [ ! -z "$DEV_USER" ] ;  then PW=`openssl passwd -1 ${DEV_PASSWORD}`; useradd -m -l ${DEV_USER} -u ${DEV_USER_ID} -p  ${PW} -s /bin/bash; \
    mkdir -p /var/run/sshd; \
    sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config; \
    adduser $DEV_USER sudo; \
    usermod -aG tty $DEV_USER; \
    chmod 777 -R /root/ /tmp; \
    fi

ENV PYTHONPATH "/home/${DEV_USER}/custom_integration_platform/"
WORKDIR "/home/${DEV_USER}/custom_integration_platform/"
CMD service ssh start && bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

FROM base as intermediate

COPY /src /root/custom_integration_platform/src/
RUN chmod 777 -R /root/

# cleanup
RUN apt update \
    && apt purge -y \
    && apt autoremove -y --purge \
    && apt autoclean -y \
    && apt purge -y \
    && apt clean all \
    && find /var/lib/apt/lists -type f -delete \
    && find /var/cache -type f -delete \
    && find /var/log -type f -delete \
    && find /tmp -type f -delete \
    && rm -rf /root/.cache \
    && rm -rf /root/go \
    && rm -fr /usr/share/man/* \
    && rm -fr /usr/share/doc/* \
    && rm -fr /usr/share/icons/* \
    && rm -fr /usr/share/pocketsphinx/*

ENV PYTHONUNBUFFERED=1 \
PYTHONPATH=/root/custom_integration_platform

WORKDIR /root/custom_integration_platform

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

FROM intermediate as testing

ENV PYTHONPATH="${PYTHONPATH}:/root/custom_integration_platform/example/mp4_data_converter"

COPY /tests /root/custom_integration_platform/tests/
COPY /example /root/custom_integration_platform/example/
RUN chmod 777 -R /root/

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

FROM intermediate as production

ENTRYPOINT ["python3.10", "src/main.py"]
