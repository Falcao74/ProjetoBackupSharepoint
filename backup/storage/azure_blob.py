from azure.storage.blob import BlobServiceClient

from .base import BackendArmazenamento

# Comentários em Português do Brasil
# Implementação de backend para Azure Blob Storage usando connection string.


class ArmazenamentoAzureBlob(BackendArmazenamento):
    def __init__(self, connection_string: str, container_name: str):
        self.servico = BlobServiceClient.from_connection_string(connection_string)
        self.container = self.servico.get_container_client(container_name)
        # Garante existência do container (não lança se já existir)
        try:
            self.container.create_container()
        except Exception:
            pass

    def obter_base_snapshot(self, data_str: str) -> str:
        return f"snapshots/{data_str}"

    def obter_base_apagados(self, data_str: str) -> str:
        return f"deleted/{data_str}"

    def escrever_stream(self, base: str, caminho_relativo: str, stream) -> None:
        nome_blob = f"{base}/{caminho_relativo}".replace("\\", "/")
        blob = self.container.get_blob_client(nome_blob)
        blob.upload_blob(data=stream, overwrite=True)

    def copiar(self, base_origem: str, caminho_relativo: str, base_destino: str) -> None:
        blob_origem = f"{base_origem}/{caminho_relativo}".replace("\\", "/")
        blob_destino = f"{base_destino}/{caminho_relativo}".replace("\\", "/")
        src_blob = self.container.get_blob_client(blob_origem)
        dst_blob = self.container.get_blob_client(blob_destino)
        try:
            # Sem URL pública/SAS, usamos download e reupload como fallback
            dados = src_blob.download_blob().readall()
            dst_blob.upload_blob(dados, overwrite=True)
        except Exception:
            # Se não existir ou falhar, não interrompe o fluxo
            pass