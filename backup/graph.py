from typing import Dict, List, Optional
import requests

# Comentários em Português do Brasil
# Este módulo encapsula chamadas ao Microsoft Graph para SharePoint.

GRAPH_URL_BASE = "https://graph.microsoft.com/v1.0"


def graph_obter_json(url: str, token: str, params: Optional[Dict] = None) -> Dict:
    """Chamada GET ao Graph retornando JSON; lança erro em status inválido."""
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()


def graph_obter_stream(url: str, token: str) -> requests.Response:
    """Chamada GET ao Graph com stream para download de conteúdo binário."""
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, stream=True)
    r.raise_for_status()
    return r


def resolver_sites(token: str, sites_cfg: List[str]) -> List[Dict]:
    """Resolve sites a partir de IDs ou resource paths; se vazio, usa root."""
    resolved: List[Dict] = []
    if sites_cfg:
        for s in sites_cfg:
            site = graph_obter_json(f"{GRAPH_URL_BASE}/sites/{s}", token)
            resolved.append(site)
    else:
        site = graph_obter_json(f"{GRAPH_URL_BASE}/sites/root", token)
        resolved.append(site)
    return resolved


def listar_drives_do_site(site_id: str, token: str) -> List[Dict]:
    """Lista drives (bibliotecas) de um site SharePoint."""
    data = graph_obter_json(f"{GRAPH_URL_BASE}/sites/{site_id}/drives", token)
    return data.get("value", [])


def listar_filhos_paginado(drive_id: str, item_id: str, token: str):
    """Itera itens filhos de um item via paginação do Graph."""
    next_url = f"{GRAPH_URL_BASE}/drives/{drive_id}/items/{item_id}/children"
    while next_url:
        data = graph_obter_json(next_url, token)
        for entry in data.get("value", []):
            yield entry
        next_url = data.get("@odata.nextLink")


def obter_id_raiz_do_drive(drive_id: str, token: str) -> str:
    """Obtém o ID do item raiz de um drive."""
    root = graph_obter_json(f"{GRAPH_URL_BASE}/drives/{drive_id}/root", token)
    return root.get("id")


def baixar_stream_conteudo_item(drive_id: str, item_id: str, token: str) -> requests.Response:
    """Obtém stream de conteúdo do item para download."""
    content_url = f"{GRAPH_URL_BASE}/drives/{drive_id}/items/{item_id}/content"
    return graph_obter_stream(content_url, token)