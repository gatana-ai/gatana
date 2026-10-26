from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.siem_gcs_target_input import SiemGcsTargetInput
    from ..models.siem_https_target_input import SiemHttpsTargetInput
    from ..models.siem_s3_target_input import SiemS3TargetInput


T = TypeVar("T", bound="UpdateSiemDestinationInput")


@_attrs_define
class UpdateSiemDestinationInput:
    """
    Attributes:
        name (str | Unset):
        url (str | Unset): HTTPS delivery URL; required for HTTPS, ignored for buckets. Must resolve to a public address
        target (SiemGcsTargetInput | SiemHttpsTargetInput | SiemS3TargetInput | Unset):
        auth_header_name (str | Unset):
        auth_header_value (str | Unset):
        export_audit_logs (bool | Unset):
        export_credential_audit_logs (bool | Unset):
        is_enabled (bool | Unset):
        remove_auth_header (bool | Unset):
        reactivate (bool | Unset):
    """

    name: str | Unset = UNSET
    url: str | Unset = UNSET
    target: SiemGcsTargetInput | SiemHttpsTargetInput | SiemS3TargetInput | Unset = UNSET
    auth_header_name: str | Unset = UNSET
    auth_header_value: str | Unset = UNSET
    export_audit_logs: bool | Unset = UNSET
    export_credential_audit_logs: bool | Unset = UNSET
    is_enabled: bool | Unset = UNSET
    remove_auth_header: bool | Unset = UNSET
    reactivate: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.siem_https_target_input import SiemHttpsTargetInput
        from ..models.siem_s3_target_input import SiemS3TargetInput

        name = self.name

        url = self.url

        target: dict[str, Any] | Unset
        if isinstance(self.target, Unset):
            target = UNSET
        elif isinstance(self.target, SiemHttpsTargetInput):
            target = self.target.to_dict()
        elif isinstance(self.target, SiemS3TargetInput):
            target = self.target.to_dict()
        else:
            target = self.target.to_dict()

        auth_header_name = self.auth_header_name

        auth_header_value = self.auth_header_value

        export_audit_logs = self.export_audit_logs

        export_credential_audit_logs = self.export_credential_audit_logs

        is_enabled = self.is_enabled

        remove_auth_header = self.remove_auth_header

        reactivate = self.reactivate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url
        if target is not UNSET:
            field_dict["target"] = target
        if auth_header_name is not UNSET:
            field_dict["authHeaderName"] = auth_header_name
        if auth_header_value is not UNSET:
            field_dict["authHeaderValue"] = auth_header_value
        if export_audit_logs is not UNSET:
            field_dict["exportAuditLogs"] = export_audit_logs
        if export_credential_audit_logs is not UNSET:
            field_dict["exportCredentialAuditLogs"] = export_credential_audit_logs
        if is_enabled is not UNSET:
            field_dict["isEnabled"] = is_enabled
        if remove_auth_header is not UNSET:
            field_dict["removeAuthHeader"] = remove_auth_header
        if reactivate is not UNSET:
            field_dict["reactivate"] = reactivate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.siem_gcs_target_input import SiemGcsTargetInput
        from ..models.siem_https_target_input import SiemHttpsTargetInput
        from ..models.siem_s3_target_input import SiemS3TargetInput

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        def _parse_target(data: object) -> SiemGcsTargetInput | SiemHttpsTargetInput | SiemS3TargetInput | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema276_type_0 = SiemHttpsTargetInput.from_dict(data)

                return componentsschemas_schema276_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema276_type_1 = SiemS3TargetInput.from_dict(data)

                return componentsschemas_schema276_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_schema276_type_2 = SiemGcsTargetInput.from_dict(data)

            return componentsschemas_schema276_type_2

        target = _parse_target(d.pop("target", UNSET))

        auth_header_name = d.pop("authHeaderName", UNSET)

        auth_header_value = d.pop("authHeaderValue", UNSET)

        export_audit_logs = d.pop("exportAuditLogs", UNSET)

        export_credential_audit_logs = d.pop("exportCredentialAuditLogs", UNSET)

        is_enabled = d.pop("isEnabled", UNSET)

        remove_auth_header = d.pop("removeAuthHeader", UNSET)

        reactivate = d.pop("reactivate", UNSET)

        update_siem_destination_input = cls(
            name=name,
            url=url,
            target=target,
            auth_header_name=auth_header_name,
            auth_header_value=auth_header_value,
            export_audit_logs=export_audit_logs,
            export_credential_audit_logs=export_credential_audit_logs,
            is_enabled=is_enabled,
            remove_auth_header=remove_auth_header,
            reactivate=reactivate,
        )

        update_siem_destination_input.additional_properties = d
        return update_siem_destination_input

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
