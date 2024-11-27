import docker
import os
from pathlib import Path
from typing import Optional


class DockerManager:
    """Manages Docker container with embedded agent."""

    def __init__(
        self, image_name: str = "minagent:latest", api_key: Optional[str] = None
    ):
        self.client = docker.from_env()
        self.image_name = image_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    def build_image(self) -> None:
        """Build the Docker image with agent code."""
        project_root = Path(__file__).parent.parent

        try:
            self.client.images.build(
                path=str(project_root),
                tag=self.image_name,
                dockerfile=str(project_root / "docker" / "Dockerfile"),
            )
        except Exception as e:
            raise Exception(f"Failed to build Docker image: {e}")

    def start_container(self) -> None:
        """Start the Docker container."""
        try:
            self.container = self.client.containers.run(
                self.image_name,
                command="python -u /app/agent.py",  # -u for unbuffered output
                environment={"OPENAI_API_KEY": self.api_key} if self.api_key else None,
                detach=True,
                tty=True,
                remove=True,
            )
        except Exception as e:
            raise Exception(f"Failed to start container: {e}")

    def stop_container(self) -> None:
        """Stop the Docker container."""
        if self.container:
            try:
                self.container.stop()
                self.container = None
            except Exception as e:
                raise Exception(f"Failed to stop container: {e}")

    def cleanup(self) -> None:
        """Clean up Docker resources."""
        self.stop_container()
        try:
            self.client.images.remove(self.image_name, force=True)
        except Exception as e:
            raise Exception(f"Failed to cleanup Docker resources: {e}")
