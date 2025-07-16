FROM ros:humble

# Set up locales
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install development tools
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and copy workspace
WORKDIR /ros2_ws

# Final setup
ENTRYPOINT ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && bash"]
