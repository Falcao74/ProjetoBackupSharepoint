import boto3
from botocore.client import Config as BotoConfig

from .base import BackendArmazenamento

# Comentários em Português do Brasil
# Implementação de backend para Amazon S3 usando boto3.


class ArmazenamentoS3(BackendArmazenamento):
    def __init__(self, nome_bucket: str, regiao: str | None = None,
                 chave_acesso_id: str | None = None, chave_secreta: str | None = None):
        # Cliente S3 com configuração opcional de região e credenciais explícitas
        self.bucket = nome_bucket
        self.client = boto3.client(
            "s3",
            region_name=regiao,
            aws_access_key_id=chave_acesso_id,
            aws_secret_access_key=chave_secreta,
            config=BotoConfig(s3={"addressing_style": "path"}),
        )

    def obter_base_snapshot(self, data_str: str) -> str:
        # Em S3 utilizamos prefixos de chave
        return f"snapshots/{data_str}"

    def obter_base_apagados(self, data_str: str) -> str:
        return f"deleted/{data_str}"

    def escrever_stream(self, base: str, caminho_relativo: str, stream) -> None:
        chave = f"{base}/{caminho_relativo}".replace("\\", "/")
        # upload_fileobj aceita stream file-like; requests Response.raw é file-like
        self.client.upload_fileobj(stream, self.bucket, chave)

    def copiar(self, base_origem: str, caminho_relativo: str, base_destino: str) -> None:
        chave_origem = f"{base_origem}/{caminho_relativo}".replace("\\", "/")
        chave_destino = f"{base_destino}/{caminho_relativo}".replace("\\", "/")
        fonte = {"Bucket": self.bucket, "Key": chave_origem}
        try:
            self.client.copy_object(Bucket=self.bucket, CopySource=fonte, Key=chave_destino)
        except Exception:
            # Se não existir ou falhar, não interrompe o fluxo
            pass