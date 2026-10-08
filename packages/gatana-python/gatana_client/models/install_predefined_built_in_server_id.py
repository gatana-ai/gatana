from enum import Enum


class InstallPredefinedBuiltInServerId(str, Enum):
    ARTIFACTS = "artifacts"
    CODEMODE = "codemode"
    COMPRESSION = "compression"
    FETCH = "fetch"
    GATANA_API = "gatana-api"
    GATANA_DEBUG = "gatana-debug"
    SKILLS = "skills"

    def __str__(self) -> str:
        return str(self.value)
