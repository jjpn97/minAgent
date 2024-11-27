import docker
import os
from pathlib import Path


class DockerManager:
    """Manages Docker container with embedded agent."""

    def __init__(self, image_name: str = "minagent:latest", api_key: str | None = None):
        self.client = docker.from_env()
        self.image_name = image_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.containers = []

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    def image_exists(self) -> bool:
        """Check if the Docker image already exists."""
        try:
            self.client.images.get(self.image_name)
            return True
        except Exception:
            return False

    def build_image(self, force: bool = False) -> None:
        """Build the Docker image with agent code if it doesn't exist or force is True."""
        if not force and self.image_exists():
            print(f"Image {self.image_name} already exists. Skipping build.")
            return

        project_root = Path(__file__).parent.parent

        try:
            self.client.images.build(
                path=str(project_root),
                tag=self.image_name,
                dockerfile=str(project_root / "docker" / "Dockerfile"),
            )
        except Exception as e:
            raise Exception(f"Failed to build Docker image: {e}")

    def start_container(self, name: str | None = None) -> None:
        """Start the Docker container."""
        try:
            self.container = self.client.containers.run(
                image=self.image_name, detach=True, stdin_open=True, name=name
            )
        except Exception as e:
            raise Exception(f"Failed to start container: {e}")

    def stop_and_remove_container(self, name: str) -> None:
        """Stop the Docker container."""
        for i, container in enumerate(self.containers):
            if container.name == name:
                container.stop()
                container.remove()
                self.containers.pop(i)
                break
        print(f"Container {name} not found.")

    def stop_and_remove_all_containers(self) -> None:
        """Stop and remove all running containers."""
        for container in self.containers:
            container.stop()
            container.remove()
        self.containers = []
