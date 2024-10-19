# container_manager.py
from abc import ABC, abstractmethod
from typing import List


class ContainerManager(ABC):
    @abstractmethod
    def verify_image(self):
        pass

    @abstractmethod
    def init_container(self):
        pass

    @abstractmethod
    def install_libraries(self, libraries: List[str]):
        pass

    @abstractmethod
    def run_code(self, code: str) -> str:
        pass

    @abstractmethod
    def cleanup(self):
        pass
