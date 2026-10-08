from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema191")


@_attrs_define
class Schema191:
    """
    Attributes:
        client_auth_method (Literal['client_secret_basic'] | Literal['client_secret_post'] | Literal['none'] | str):
            Client authentication method used at the token endpoint
        client_id (str | Unset):
        client_secret (str | Unset):
        scopes (str | Unset):
    """

    client_auth_method: Literal["client_secret_basic"] | Literal["client_secret_post"] | Literal["none"] | str
    client_id: str | Unset = UNSET
    client_secret: str | Unset = UNSET
    scopes: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_auth_method: Literal["client_secret_basic"] | Literal["client_secret_post"] | Literal["none"] | str
        client_auth_method = self.client_auth_method

        client_id = self.client_id

        client_secret = self.client_secret

        scopes = self.scopes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "clientAuthMethod": client_auth_method,
            }
        )
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if client_secret is not UNSET:
            field_dict["clientSecret"] = client_secret
        if scopes is not UNSET:
            field_dict["scopes"] = scopes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_client_auth_method(
            data: object,
        ) -> Literal["client_secret_basic"] | Literal["client_secret_post"] | Literal["none"] | str:
            componentsschemas_schema145_type_0 = cast(Literal["client_secret_basic"], data)
            if componentsschemas_schema145_type_0 != "client_secret_basic":
                raise ValueError(
                    f"/components/schemas/__schema145_type_0 must match const 'client_secret_basic', got '{componentsschemas_schema145_type_0}'"
                )
            return componentsschemas_schema145_type_0
            componentsschemas_schema145_type_1 = cast(Literal["client_secret_post"], data)
            if componentsschemas_schema145_type_1 != "client_secret_post":
                raise ValueError(
                    f"/components/schemas/__schema145_type_1 must match const 'client_secret_post', got '{componentsschemas_schema145_type_1}'"
                )
            return componentsschemas_schema145_type_1
            componentsschemas_schema145_type_2 = cast(Literal["none"], data)
            if componentsschemas_schema145_type_2 != "none":
                raise ValueError(
                    f"/components/schemas/__schema145_type_2 must match const 'none', got '{componentsschemas_schema145_type_2}'"
                )
            return componentsschemas_schema145_type_2
            return cast(Literal["client_secret_basic"] | Literal["client_secret_post"] | Literal["none"] | str, data)

        client_auth_method = _parse_client_auth_method(d.pop("clientAuthMethod"))

        client_id = d.pop("clientId", UNSET)

        client_secret = d.pop("clientSecret", UNSET)

        scopes = d.pop("scopes", UNSET)

        schema_191 = cls(
            client_auth_method=client_auth_method,
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
        )

        schema_191.additional_properties = d
        return schema_191

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
