# docker/Dockerfile
FROM python:3.9-slim

WORKDIR /home

# Copy files from docker directory
COPY docker/requirements.txt /home/requirements.txt
COPY docker/entrypoint.sh /home/entrypoint.sh

# Fix permissions and install requirements
RUN chmod +x /home/entrypoint.sh && \
    pip install --no-cache-dir -r /home/requirements.txt

# Create a non-root user and setup directories
RUN useradd -m -r -s /bin/bash agent_user && \
    mkdir -p /app && \
    chown -R agent_user:agent_user /app /home

USER agent_user

# Set the entrypoint with full path
ENTRYPOINT ["/home/entrypoint.sh"]
CMD ["/bin/bash"]