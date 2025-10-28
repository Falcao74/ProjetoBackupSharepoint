from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from .config import ConfigAplicativo
from .auth import obter_token
from . import graph
from .storage.base import BackendArmazenamento

# Comentários em Português do Brasil
# Este módulo orquestra o processo de backup, mantendo estado e separando responsabilidades.


def carregar_estado_anterior(diretorio_estado: Path) -> Dict:
    """Carrega o manifesto e informações do snapshot anterior do diretório de estado local."""
    caminho_manifesto = diretorio_estado / "latest_manifest.json"
    caminho_snapshot = diretorio_estado / "latest_snapshot.txt"
    manifesto_anterior: Dict = {}
    base_snapshot_anterior: str | None = None
    if caminho_manifesto.exists():
        try:
            manifesto_anterior = __import__("json").loads(caminho_manifesto.read_text(encoding="utf-8"))
        except Exception:
            manifesto_anterior = {}
    if caminho_snapshot.exists():
        base_snapshot_anterior = caminho_snapshot.read_text(encoding="utf-8").strip()
    return {"manifesto": manifesto_anterior, "base_snapshot": base_snapshot_anterior}


def salvar_estado_atual(diretorio_estado: Path, manifesto: Dict, base_snapshot: str) -> None:
    """Salva manifesto atual e base de snapshot no diretório de estado local."""
    diretorio_estado.mkdir(parents=True, exist_ok=True)
    (diretorio_estado / "latest_manifest.json").write_text(
        __import__("json").dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (diretorio_estado / "latest_snapshot.txt").write_text(base_snapshot, encoding="utf-8")


def executar_backup(cfg: ConfigAplicativo, armazenamento: BackendArmazenamento) -> None:
    """Executa o processo de backup completo, criando snapshot e movendo apagados."""
    # Autenticação
    token = obter_token(cfg.tenant_id, cfg.client_id, cfg.client_secret)

    # Datas e bases
    hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base_snapshot = armazenamento.obter_base_snapshot(hoje)
    base_apagados = armazenamento.obter_base_apagados(hoje)

    # Estado anterior
    dir_estado = Path("state")
    estado_anterior = carregar_estado_anterior(dir_estado)
    manifesto_anterior: Dict = estado_anterior.get("manifesto", {})
    base_snapshot_anterior: str | None = estado_anterior.get("base_snapshot")

    # Resolver sites e iniciar manifesto
    sites = graph.resolver_sites(token, cfg.sites)
    manifesto: Dict[str, Dict] = {}

    for site in sites:
        id_site = site.get("id")
        nome_site = site.get("name") or site.get("displayName") or id_site

        drives = graph.listar_drives_do_site(id_site, token)
        for d in drives:
            id_drive = d.get("id")
            nome_drive = d.get("name") or id_drive

            id_raiz = graph.obter_id_raiz_do_drive(id_drive, token)

            for entrada in graph.listar_filhos_paginado(id_drive, id_raiz, token):
                # Processa recursivamente pastas e arquivos
                pilha = [(entrada, Path(""))]
                while pilha:
                    atual, rel = pilha.pop()
                    nome = atual.get("name")
                    eh_pasta = atual.get("folder") is not None
                    id_item = atual.get("id")

                    rel_atual = rel / nome
                    rel_completo = Path(nome_site) / nome_drive / rel_atual

                    if eh_pasta:
                        # Em backends locais podemos garantir diretório; nos demais é no-op
                        armazenamento.garantir_diretorio(base_snapshot, str(rel_completo))
                        # Empilha filhos da pasta
                        for filho in graph.listar_filhos_paginado(id_drive, id_item, token):
                            pilha.append((filho, rel_atual))
                    else:
                        # Download e gravação do arquivo
                        resp = graph.baixar_stream_conteudo_item(id_drive, id_item, token)
                        armazenamento.escrever_stream(base_snapshot, str(rel_completo).replace("\\", "/"), resp.raw)
                        manifesto[id_item] = {
                            "path": str(rel_completo).replace("\\", "/"),
                            "driveId": id_drive,
                            "siteId": id_site,
                            "name": nome,
                        }

    # Detecta itens apagados comparando IDs do manifesto anterior com o atual
    ids_anteriores = set(manifesto_anterior.keys())
    ids_novos = set(manifesto.keys())
    ids_apagados = ids_anteriores - ids_novos

    if base_snapshot_anterior:
        for id_item in ids_apagados:
            info = manifesto_anterior.get(id_item)
            if not info:
                continue
            caminho_rel = info.get("path")
            if caminho_rel:
                try:
                    armazenamento.copiar(base_snapshot_anterior, caminho_rel, base_apagados)
                except Exception:
                    # Não interromper se falhar a cópia de algum item
                    pass

    # Salva estado atual
    salvar_estado_atual(dir_estado, manifesto, base_snapshot)