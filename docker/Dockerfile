# docker/Dockerfile
FROM python:3.9-slim

# Create system directories first
RUN mkdir -p /home/agent /opt/scripts

# Copy files to appropriate locations
COPY docker/requirements.txt /opt/scripts/requirements.txt
COPY docker/entrypoint.sh /opt/scripts/entrypoint.sh

# Fix permissions and install requirements
RUN chmod +x /opt/scripts/entrypoint.sh && \
    pip install --no-cache-dir -r /opt/scripts/requirements.txt && \
    chmod 755 /opt/scripts && \
    chmod 755 /opt/scripts/entrypoint.sh && \
    chown -R root:root /opt/scripts

# Create a non-root user and setup directories
RUN useradd -m -r -s /bin/bash agent && \
    chown -R agent:agent /home/agent

WORKDIR /home/agent

USER agent

ENTRYPOINT ["/opt/scripts/entrypoint.sh"]
CMD ["/bin/bash"]