from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.email_preset import EmailPreset
from ..models.schema_123 import Schema123
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_imap_connection import EmailImapConnection
    from ..models.email_jmap_connection import EmailJmapConnection


T = TypeVar("T", bound="EmailTransportConfig")


@_attrs_define
class EmailTransportConfig:
    """
    Attributes:
        type_ (Literal['email']): Transport type discriminator, always "email"
        connection (EmailImapConnection | EmailJmapConnection): Mailbox connection settings. The protocol cannot change
            after server creation
        preset (EmailPreset | None | Unset):
        access (Schema123 | Unset): What the tools may do. "read" reads mail and attachments. "organize" also flags,
            moves and trashes messages and writes drafts. "send" also sends mail
    """

    type_: Literal["email"]
    connection: EmailImapConnection | EmailJmapConnection
    preset: EmailPreset | None | Unset = UNSET
    access: Schema123 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.email_imap_connection import EmailImapConnection

        type_ = self.type_

        connection: dict[str, Any]
        if isinstance(self.connection, EmailImapConnection):
            connection = self.connection.to_dict()
        else:
            connection = self.connection.to_dict()

        preset: None | str | Unset
        if isinstance(self.preset, Unset):
            preset = UNSET
        elif isinstance(self.preset, EmailPreset):
            preset = self.preset.value
        else:
            preset = self.preset

        access: str | Unset = UNSET
        if not isinstance(self.access, Unset):
            access = self.access.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "connection": connection,
            }
        )
        if preset is not UNSET:
            field_dict["preset"] = preset
        if access is not UNSET:
            field_dict["access"] = access

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_imap_connection import EmailImapConnection
        from ..models.email_jmap_connection import EmailJmapConnection

        d = dict(src_dict)
        type_ = cast(Literal["email"], d.pop("type"))
        if type_ != "email":
            raise ValueError(f"type must match const 'email', got '{type_}'")

        def _parse_connection(data: object) -> EmailImapConnection | EmailJmapConnection:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema124_type_0 = EmailImapConnection.from_dict(data)

                return componentsschemas_schema124_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_schema124_type_1 = EmailJmapConnection.from_dict(data)

            return componentsschemas_schema124_type_1

        connection = _parse_connection(d.pop("connection"))

        def _parse_preset(data: object) -> EmailPreset | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_schema122_type_0 = EmailPreset(data)

                return componentsschemas_schema122_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EmailPreset | None | Unset, data)

        preset = _parse_preset(d.pop("preset", UNSET))

        _access = d.pop("access", UNSET)
        access: Schema123 | Unset
        if isinstance(_access, Unset):
            access = UNSET
        else:
            access = Schema123(_access)

        email_transport_config = cls(
            type_=type_,
            connection=connection,
            preset=preset,
            access=access,
        )

        email_transport_config.additional_properties = d
        return email_transport_config

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
