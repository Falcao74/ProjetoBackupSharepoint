from abc import ABC, abstractmethod
from typing import Optional

# Comentários em Português do Brasil
# Interface de backend de armazenamento seguindo o princípio de inversão de dependência (SOLID).


class BackendArmazenamento(ABC):
    """Define operações mínimas de um backend de armazenamento para snapshots e itens apagados."""

    @abstractmethod
    def obter_base_snapshot(self, data_str: str) -> str:
        """Retorna o caminho/base (prefixo) do snapshot para a data indicada."""
        raise NotImplementedError

    @abstractmethod
    def obter_base_apagados(self, data_str: str) -> str:
        """Retorna o caminho/base (prefixo) para armazenar itens apagados na data."""
        raise NotImplementedError

    @abstractmethod
    def escrever_stream(self, base: str, caminho_relativo: str, stream) -> None:
        """Grava um arquivo a partir de um stream binário no caminho base+relativo."""
        raise NotImplementedError

    @abstractmethod
    def copiar(self, base_origem: str, caminho_relativo: str, base_destino: str) -> None:
        """Copia um arquivo interno do backend de origem para destino mantendo o caminho relativo."""
        raise NotImplementedError

    def garantir_diretorio(self, base: str, diretorio_relativo: Optional[str] = None) -> None:
        """Alguns backends não possuem diretórios reais; no local é necessário criar."""
        # Método opcional; implementação padrão não faz nada.
        return None