from pathlib import Path
from typing import Optional

from .base import BackendArmazenamento

# Comentários em Português do Brasil
# Implementação de backend local em sistema de arquivos.


class ArmazenamentoLocal(BackendArmazenamento):
    def __init__(self, diretorio_raiz: str):
        # Diretório raiz para backups locais
        self.raiz = Path(diretorio_raiz)

    def obter_base_snapshot(self, data_str: str) -> str:
        return str(self.raiz / "snapshots" / data_str)

    def obter_base_apagados(self, data_str: str) -> str:
        return str(self.raiz / "deleted" / data_str)

    def garantir_diretorio(self, base: str, diretorio_relativo: Optional[str] = None) -> None:
        p = Path(base)
        if diretorio_relativo:
            p = p / diretorio_relativo
        p.mkdir(parents=True, exist_ok=True)

    def escrever_stream(self, base: str, caminho_relativo: str, stream) -> None:
        alvo = Path(base) / caminho_relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        with open(alvo, "wb") as f:
            # Copia em blocos para evitar carregar tudo em memória
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)

    def copiar(self, base_origem: str, caminho_relativo: str, base_destino: str) -> None:
        origem = Path(base_origem) / caminho_relativo
        destino = Path(base_destino) / caminho_relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        if origem.exists():
            with open(origem, "rb") as s, open(destino, "wb") as d:
                while True:
                    chunk = s.read(1024 * 1024)
                    if not chunk:
                        break
                    d.write(chunk)