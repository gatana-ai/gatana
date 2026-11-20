from enum import Enum


class Schema1188(str, Enum):
    GCS = "gcs"
    HTTPS = "https"
    S3 = "s3"

    def __str__(self) -> str:
        return str(self.value)
