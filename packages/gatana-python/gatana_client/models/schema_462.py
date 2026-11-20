from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema462")


@_attrs_define
class Schema462:
    """
    Attributes:
        kubernetes (bool): A Kubernetes cluster is configured for executable (npx, uvx) and hosted servers, sandboxes,
            server volumes and Code Mode worker pods
        object_storage (bool): Hosted server code can be stored in a bucket (FUNCTIONS_STORAGE_BUCKET) or the database
        shared_object_storage (bool): Server pods can download stored files. False for database storage
        storage_class (bool): A storage class for server volumes is configured (WORKLOAD_STORAGE_CLASS_NAME)
        tailscale_image (bool): A Tailscale sidecar image is configured (WORKLOAD_TAILSCALE_IMAGE)
        email (bool): An email provider is configured for invitations and notices (EMAIL_PROVIDER)
        embeddings (bool): The embedding service passed its health check (EMBEDDING_SERVICE_URL). Without it, searches
            of compressed results use keywords only
        code_mode_worker (bool): Code Mode can use a worker URL or start worker pods in Kubernetes
    """

    kubernetes: bool
    object_storage: bool
    shared_object_storage: bool
    storage_class: bool
    tailscale_image: bool
    email: bool
    embeddings: bool
    code_mode_worker: bool

    def to_dict(self) -> dict[str, Any]:
        kubernetes = self.kubernetes

        object_storage = self.object_storage

        shared_object_storage = self.shared_object_storage

        storage_class = self.storage_class

        tailscale_image = self.tailscale_image

        email = self.email

        embeddings = self.embeddings

        code_mode_worker = self.code_mode_worker

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kubernetes": kubernetes,
                "objectStorage": object_storage,
                "sharedObjectStorage": shared_object_storage,
                "storageClass": storage_class,
                "tailscaleImage": tailscale_image,
                "email": email,
                "embeddings": embeddings,
                "codeModeWorker": code_mode_worker,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kubernetes = d.pop("kubernetes")

        object_storage = d.pop("objectStorage")

        shared_object_storage = d.pop("sharedObjectStorage")

        storage_class = d.pop("storageClass")

        tailscale_image = d.pop("tailscaleImage")

        email = d.pop("email")

        embeddings = d.pop("embeddings")

        code_mode_worker = d.pop("codeModeWorker")

        schema_462 = cls(
            kubernetes=kubernetes,
            object_storage=object_storage,
            shared_object_storage=shared_object_storage,
            storage_class=storage_class,
            tailscale_image=tailscale_image,
            email=email,
            embeddings=embeddings,
            code_mode_worker=code_mode_worker,
        )

        return schema_462
