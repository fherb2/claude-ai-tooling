# Extensible dev container base for VS Code with the Claude Code extension.
#
# Carries a C toolchain, the distribution Python as a stable base for tooling,
# and Poetry plus uv. Interpreters for individual projects are not baked in;
# they are fetched on demand. See README.md for the reasoning.
#
# Meant to be derived from: adding JupyterLab or a vendor SDK is a matter of
# appending to this file, or of a second Dockerfile with FROM.

FROM ubuntu:24.04

# Account name and home path. devcontainer.json passes the values of the machine
# that builds the image, so every absolute path inside matches the one outside.
# The defaults apply when the image is built without those arguments.
ARG USERNAME=dev
ARG USER_HOME=/home/dev

ENV DEBIAN_FRONTEND=noninteractive

# Ubuntu 24.04 already ships an "ubuntu" account on UID/GID 1000. Rename it
# rather than adding a second account, so UID 1000 stays free of conflicts and
# the UID alignment done by the editor has nothing left to do in the usual case.
RUN set -eux; \
    if [ "$USERNAME" != "ubuntu" ]; then \
        groupmod -n "$USERNAME" ubuntu; \
        usermod -l "$USERNAME" -d "$USER_HOME" -m ubuntu; \
    else \
        usermod -d "$USER_HOME" -m ubuntu; \
    fi

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        pipx \
        python3 \
        python3-venv \
        sudo; \
    rm -rf /var/lib/apt/lists/*

# Passwordless sudo. Conventional for dev containers and needed to install a
# missing library while debugging. It also means packet filter rules set inside
# the container can be undone from inside it, which is why the network boundary
# belongs on the host. README.md, section "Netzgrenze", says how.
RUN set -eux; \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/$USERNAME"; \
    chmod 0440 "/etc/sudoers.d/$USERNAME"

COPY files/bashrc-snippets.sh /etc/devcontainer/bashrc-snippets.sh

USER $USERNAME
ENV HOME=$USER_HOME
WORKDIR $USER_HOME

# Poetry and uv each get their own environment through pipx, so neither of them
# sits in an environment a project uses.
ENV PATH="$USER_HOME/.local/bin:$PATH"
RUN set -eux; \
    pipx install poetry; \
    pipx install uv

RUN echo '. /etc/devcontainer/bashrc-snippets.sh' >> "$USER_HOME/.bashrc"
