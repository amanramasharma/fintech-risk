import shutil
from pathlib import Path
import boto3
from .interface import ModelRef, ModelRegistry


class S3ModelRegistry(ModelRegistry):
    def __init__(self, bucket: str, prefix: str = "model-registry"):
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self.s3 = boto3.client("s3")

    def _key(self, ref: ModelRef, filename: str) -> str:
        return f"{self.prefix}/{ref.name}/{ref.version}/{filename}"

    def save(self, ref: ModelRef, artifacts_dir: Path) -> None:
        for p in artifacts_dir.iterdir():
            if p.is_file():
                self.s3.upload_file(
                    str(p),
                    self.bucket,
                    self._key(ref, p.name),)

    def load(self, ref: ModelRef, dest_dir: Path) -> Path:
        dest_dir.mkdir(parents=True, exist_ok=True)

        resp = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=f"{self.prefix}/{ref.name}/{ref.version}/",)

        if "Contents" not in resp:
            raise FileNotFoundError(f"model not found: {ref}")

        for obj in resp["Contents"]:
            key = obj["Key"]
            name = key.split("/")[-1]
            out = dest_dir / name
            self.s3.download_file(self.bucket, key, str(out))

        return dest_dir