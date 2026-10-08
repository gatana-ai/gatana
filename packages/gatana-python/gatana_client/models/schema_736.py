from enum import Enum


class Schema736(str, Enum):
    AZURE_OPENAI = "azure-openai"
    BEDROCK = "bedrock"
    OPENAI_COMPATIBLE = "openai-compatible"

    def __str__(self) -> str:
        return str(self.value)
