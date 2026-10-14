# Reproducible quality-gate image: ROS 2 Jazzy plus every dependency the
# Companion packages declare. The repository itself is mounted at run time.
FROM ros:jazzy-ros-base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY ros2_ws/src /tmp/deps/src
COPY requirements-dev.txt /tmp/deps/requirements-dev.txt

RUN apt-get update \
    && rosdep update --rosdistro jazzy \
    && rosdep install --from-paths /tmp/deps/src --ignore-src -r -y \
    && apt-get install -y --no-install-recommends python3-pip \
    && pip3 install --break-system-packages --no-cache-dir -r /tmp/deps/requirements-dev.txt \
    && rm -rf /var/lib/apt/lists/* /tmp/deps

WORKDIR /ws
