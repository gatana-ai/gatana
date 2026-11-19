from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.email_preset import EmailPreset
from ..models.schema_665 import Schema665
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_imap_connection_output import EmailImapConnectionOutput
    from ..models.email_jmap_connection_output import EmailJmapConnectionOutput


T = TypeVar("T", bound="EmailTransportConfigOutput")


@_attrs_define
class EmailTransportConfigOutput:
    """
    Attributes:
        type_ (Literal['email']): Transport type discriminator, always "email"
        access (Schema665): What the tools may do. "read" reads mail and attachments. "organize" also flags, moves and
            trashes messages and writes drafts. "send" also sends mail
        connection (EmailImapConnectionOutput | EmailJmapConnectionOutput): Mailbox connection settings. The protocol
            cannot change after server creation
        preset (EmailPreset | None | Unset):
    """

    type_: Literal["email"]
    access: Schema665
    connection: EmailImapConnectionOutput | EmailJmapConnectionOutput
    preset: EmailPreset | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.email_imap_connection_output import EmailImapConnectionOutput

        type_ = self.type_

        access = self.access.value

        connection: dict[str, Any]
        if isinstance(self.connection, EmailImapConnectionOutput):
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

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "access": access,
                "connection": connection,
            }
        )
        if preset is not UNSET:
            field_dict["preset"] = preset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_imap_connection_output import EmailImapConnectionOutput
        from ..models.email_jmap_connection_output import EmailJmapConnectionOutput

        d = dict(src_dict)
        type_ = cast(Literal["email"], d.pop("type"))
        if type_ != "email":
            raise ValueError(f"type must match const 'email', got '{type_}'")

        access = Schema665(d.pop("access"))

        def _parse_connection(data: object) -> EmailImapConnectionOutput | EmailJmapConnectionOutput:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema666_type_0 = EmailImapConnectionOutput.from_dict(data)

                return componentsschemas_schema666_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_schema666_type_1 = EmailJmapConnectionOutput.from_dict(data)

            return componentsschemas_schema666_type_1

        connection = _parse_connection(d.pop("connection"))

        def _parse_preset(data: object) -> EmailPreset | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_schema664_type_0 = EmailPreset(data)

                return componentsschemas_schema664_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EmailPreset | None | Unset, data)

        preset = _parse_preset(d.pop("preset", UNSET))

        email_transport_config_output = cls(
            type_=type_,
            access=access,
            connection=connection,
            preset=preset,
        )

        return email_transport_config_output
