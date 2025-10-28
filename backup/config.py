from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict
import os

# Comentários em Português do Brasil
# Este módulo lida com carregamento de configuração a partir de TOML.

# Compat: tomllib (3.11+) ou tomli
try:
    import tomllib  # type: ignore
    def carregar_toml_bytes(data: bytes) -> Dict:
        return tomllib.loads(data.decode("utf-8"))
except Exception:
    import tomli  # type: ignore
    def carregar_toml_bytes(data: bytes) -> Dict:
        return tomli.loads(data.decode("utf-8"))


@dataclass
class ConfigS3:
    bucket_name: Optional[str] = None
    region_name: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None


@dataclass
class ConfigAzureBlob:
    connection_string: Optional[str] = None
    container_name: Optional[str] = None


@dataclass
class ConfigAplicativo:
    # Configurações do Microsoft Graph
    tenant_id: str
    client_id: str
    client_secret: str

    # Parâmetros de backup
    backup_backend: str = "local"  # valores: local | s3 | azure_blob
    backup_dir: str = "backups"
    snapshot_diario: bool = True
    sites: List[str] = field(default_factory=list)

    # Backends externos
    s3: ConfigS3 = field(default_factory=ConfigS3)
    azure_blob: ConfigAzureBlob = field(default_factory=ConfigAzureBlob)


def carregar_configuracao(path: Path = Path("credentials.toml")) -> ConfigAplicativo:
    """Carrega e valida a configuração a partir de arquivo TOML ou variáveis de ambiente.

    O arquivo real de credenciais deve ser 'credentials.toml'; um exemplo està disponível
    em 'credentials.example.toml'. Se o arquivo não existir, tenta carregar de variáveis
    de ambiente (TENANT_ID, CLIENT_ID, CLIENT_SECRET, etc.).
    """
    def _carregar_de_env() -> Dict:
        tenant_id = os.environ.get("TENANT_ID")
        client_id = os.environ.get("CLIENT_ID")
        client_secret = os.environ.get("CLIENT_SECRET")

        backup_backend = os.environ.get("BACKUP_BACKEND", "local")
        backup_dir = os.environ.get("BACKUP_DIR", "backups")
        snap_env = (os.environ.get("SNAPSHOT_DIARIO", "true") or "true").strip().lower()
        snapshot_diario = snap_env not in {"false", "0", "no", "n"}

        sites_raw = (os.environ.get("SITES") or "").strip()
        sites = [s.strip() for s in sites_raw.split(",") if s.strip()] if sites_raw else []

        s3 = {
            "bucket_name": os.environ.get("S3_BUCKET_NAME"),
            "region_name": os.environ.get("S3_REGION_NAME"),
            "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        }

        azure_blob = {
            "connection_string": os.environ.get("AZURE_CONNECTION_STRING"),
            "container_name": os.environ.get("AZURE_CONTAINER_NAME"),
        }

        return {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "client_secret": client_secret,
            "backup_backend": backup_backend,
            "backup_dir": backup_dir,
            "snapshot_diario": snapshot_diario,
            "sites": sites,
            "s3": s3,
            "azure_blob": azure_blob,
        }

    if path.exists():
        data = carregar_toml_bytes(path.read_bytes())
    else:
        data = _carregar_de_env()

    # Campos obrigatórios
    for req in ["tenant_id", "client_id", "client_secret"]:
        if not data.get(req):
            raise FileNotFoundError("'credentials.toml' não encontrado e variáveis de ambiente necessárias ausentes")

    # Defaults e construção
    backup_backend = data.get("backup_backend", "local")
    backup_dir = data.get("backup_dir", "backups")
    snapshot_diario = bool(data.get("snapshot_diario", True))
    sites = data.get("sites", []) or []

    s3cfg = ConfigS3(**data.get("s3", {}))
    azcfg = ConfigAzureBlob(**data.get("azure_blob", {}))

    return ConfigAplicativo(
        tenant_id=data["tenant_id"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        backup_backend=backup_backend,
        backup_dir=backup_dir,
        snapshot_diario=snapshot_diario,
        sites=sites,
        s3=s3cfg,
        azure_blob=azcfg,
    )