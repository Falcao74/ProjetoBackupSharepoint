from typing import Dict, List
from io import BytesIO

# Comentários em Português do Brasil
# Cliente Graph mock para testes: replica assinaturas usadas pelo runner,
# sem realizar chamadas reais ao Microsoft Graph.


class RespostaMock:
    """Objeto mínimo com atributo .raw compatível com requests.Response.raw."""

    def __init__(self, dados: bytes):
        self.raw = BytesIO(dados)


def resolver_sites(token: str, sites_cfg: List[str]) -> List[Dict]:
    """Retorna uma lista com um site mock, ignorando token e sites_cfg."""
    return [{"id": "site-mock", "name": "SiteMock"}]


def listar_drives_do_site(site_id: str, token: str) -> List[Dict]:
    """Retorna uma lista com um drive mock para o site informado."""
    return [{"id": "drive-mock", "name": "DriveMock"}]


def obter_id_raiz_do_drive(drive_id: str, token: str) -> str:
    """Retorna ID raiz mock do drive."""
    return "root-mock"


def listar_filhos_paginado(drive_id: str, item_id: str, token: str):
    """Gera itens mock: uma pasta 'docs' contendo um arquivo 'relatorio.txt'."""
    if item_id == "root-mock":
        yield {"id": "folder-docs", "name": "docs", "folder": {"childCount": 1}}
    elif item_id == "folder-docs":
        yield {"id": "file-1", "name": "relatorio.txt"}


def baixar_stream_conteudo_item(drive_id: str, item_id: str, token: str) -> RespostaMock:
    """Retorna stream de bytes estático para o arquivo mock."""
    conteudo = b"Conteudo de teste do relatorio."
    return RespostaMock(conteudo)