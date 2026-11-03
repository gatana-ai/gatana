from enum import Enum


class Schema450(str, Enum):
    NO_CODE_MODE_WORKER = "no-code-mode-worker"
    NO_KUBERNETES = "no-kubernetes"
    NO_OBJECT_STORAGE = "no-object-storage"
    NO_SHARED_OBJECT_STORAGE = "no-shared-object-storage"
    NO_STORAGE_CLASS = "no-storage-class"
    NO_TAILSCALE_IMAGE = "no-tailscale-image"

    def __str__(self) -> str:
        return str(self.value)
