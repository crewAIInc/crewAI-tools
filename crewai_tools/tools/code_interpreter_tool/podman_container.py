# podman_container.py
import os
from typing import List, Optional

from podman import PodmanClient
from podman.errors import NotFound, ImageNotFound
from .container_manager import ContainerManager


class PodmanContainer(ContainerManager):
    def __init__(
        self,
        image_tag: str,
        dockerfile_path: Optional[str] = None,
        container_name: str = "code-interpreter",
    ):
        self.image_tag = image_tag
        self.dockerfile_path = dockerfile_path
        self.container_name = container_name
        self.client = PodmanClient.from_env()
        self.container = None

    def verify_image(self):
        """
        Verify if the Podman image is available. If not, build it using the provided Dockerfile.
        """
        try:
            self.client.images.get(self.image_tag)
        except ImageNotFound:
            if self.dockerfile_path and os.path.exists(self.dockerfile_path):
                image, build_logs = self.client.images.build(
                    path=self.dockerfile_path,
                    tag=self.image_tag,
                    rm=True,
                )
            else:
                raise FileNotFoundError(
                    f"Dockerfile not found at {self.dockerfile_path}"
                )

    def init_container(self):
        """
        Initialize the Podman container.
        """
        # Stop and remove existing container if it exists
        try:
            existing_container = self.client.containers.get(self.container_name)
            existing_container.stop()
            existing_container.remove()
        except NotFound:
            pass  # Container does not exist

        current_path = os.getcwd()
        volumes = {current_path: {'bind': '/workspace', 'mode': 'rw'}}

        self.container = self.client.containers.create(
            self.image_tag,
            name=self.container_name,
            tty=True,
            working_dir="/workspace",
            volumes=volumes,
        )
        self.container.start()

    def install_libraries(self, libraries: List[str]):
        """
        Install the specified libraries in the Podman container.
        """
        for library in libraries:
            exit_code, output = self.container.exec_run(f"pip install {library}")
            if exit_code != 0:
                raise Exception(
                    f"Failed to install library {library}: {output.decode('utf-8')}"
                )

    def run_code(self, code: str) -> str:
        """
        Execute the provided code in the Podman container.
        """
        cmd = f'python3 -c "{code}"'
        exit_code, output = self.container.exec_run(cmd)
        if exit_code != 0:
            return (
                f"Something went wrong while running the code: \n"
                f"{output.decode('utf-8')}"
            )
        return output.decode("utf-8")

    def cleanup(self):
        """
        Stop and remove the Podman container.
        """
        self.container.stop()
        self.container.remove()
