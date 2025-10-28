"""Ponto de entrada do aplicativo.

Mantém comentários em Português do Brasil e aplica SOLID delegando responsabilidades
para módulos de configuração, autenticação, Graph e armazenamento.
"""

from pathlib import Path
from getpass import getpass

from backup.config import carregar_configuracao
from backup.runner import executar_backup
from backup.storage.local import ArmazenamentoLocal
from backup.storage.s3 import ArmazenamentoS3
from backup.storage.azure_blob import ArmazenamentoAzureBlob


def selecionar_armazenamento(cfg) -> object:
    """Seleciona o backend de armazenamento conforme configuração."""
    if cfg.backup_backend == "local":
        return ArmazenamentoLocal(cfg.backup_dir)
    elif cfg.backup_backend == "s3":
        return ArmazenamentoS3(
            nome_bucket=cfg.s3.bucket_name or "",
            regiao=cfg.s3.region_name,
            chave_acesso_id=cfg.s3.aws_access_key_id,
            chave_secreta=cfg.s3.aws_secret_access_key,
        )
    elif cfg.backup_backend == "azure_blob":
        return ArmazenamentoAzureBlob(
            connection_string=cfg.azure_blob.connection_string or "",
            container_name=cfg.azure_blob.container_name or "",
        )
    else:
        raise ValueError(f"Backend desconhecido: {cfg.backup_backend}")


def _escrever_toml_interativo(caminho: Path) -> None:
    """Solicita dados ao usuário e grava arquivo TOML de credenciais."""
    print("Configuração inicial não encontrada. Vamos configurar suas credenciais.")

    tenant_id = input("Tenant ID (Azure AD): ").strip()
    client_id = input("Client ID (App Registration): ").strip()
    client_secret = getpass("Client Secret (não será exibido): ").strip()

    print("\nSelecione o backend de armazenamento:")
    print("  1) local (filesystem)")
    print("  2) s3 (Amazon S3)")
    print("  3) azure_blob (Azure Blob Storage)")
    opc = input("Digite 1, 2 ou 3: ").strip()
    if opc == "1":
        backend = "local"
    elif opc == "2":
        backend = "s3"
    elif opc == "3":
        backend = "azure_blob"
    else:
        backend = "local"

    backup_dir = "backups"
    s3_section = ""
    az_section = ""

    if backend == "local":
        backup_dir = input("Diretório para backups locais (default 'backups'): ").strip() or "backups"
    elif backend == "s3":
        bucket = input("S3 Bucket name: ").strip()
        region = input("S3 Region (ex.: us-east-1): ").strip()
        akid = input("AWS Access Key ID: ").strip()
        asec = getpass("AWS Secret Access Key (não será exibido): ").strip()
        s3_section = (
            "\n[s3]\n"
            f"bucket_name = \"{bucket}\"\n"
            f"region_name = \"{region}\"\n"
            f"aws_access_key_id = \"{akid}\"\n"
            f"aws_secret_access_key = \"{asec}\"\n"
        )
    elif backend == "azure_blob":
        conn = getpass("Azure Blob connection string (não será exibido): ").strip()
        cont = input("Azure Blob container name: ").strip()
        az_section = (
            "\n[azure_blob]\n"
            f"connection_string = \"{conn}\"\n"
            f"container_name = \"{cont}\"\n"
        )

    sites_raw = input(
        "Sites do SharePoint (opcional, separados por vírgula, ex.: contoso.sharepoint.com:/sites/Finance): "
    ).strip()
    sites_list = [s.strip() for s in sites_raw.split(",") if s.strip()] if sites_raw else []
    sites_toml = ", ".join([f'"{s}"' for s in sites_list])

    conteudo = (
        f'tenant_id = "{tenant_id}"\n'
        f'client_id = "{client_id}"\n'
        f'client_secret = "{client_secret}"\n'
        f'backup_backend = "{backend}"\n'
        f'backup_dir = "{backup_dir}"\n'
        f'snapshot_diario = true\n'
        + (f"sites = [{sites_toml}]\n" if sites_list else "")
        + s3_section
        + az_section
    )

    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    print(f"Credenciais salvas em: {caminho}")


def main():
    caminho_interativo = Path("credenciais/credentials.toml")

    try:
        if caminho_interativo.exists():
            cfg = carregar_configuracao(caminho_interativo)
        else:
            cfg = carregar_configuracao()
    except FileNotFoundError:
        _escrever_toml_interativo(caminho_interativo)
        cfg = carregar_configuracao(caminho_interativo)

    try:
        armazenamento = selecionar_armazenamento(cfg)
    except Exception as e:
        print(f"Erro ao configurar armazenamento: {e}")
        resp = input("Deseja reconfigurar as credenciais? (s/n): ").strip().lower()
        if resp in {"s", "sim", "y", "yes"}:
            _escrever_toml_interativo(caminho_interativo)
            cfg = carregar_configuracao(caminho_interativo)
            armazenamento = selecionar_armazenamento(cfg)
        else:
            raise

    try:
        executar_backup(cfg, armazenamento)
    except Exception as e:
        print(f"Erro durante a execução do backup: {e}")
        resp = input("Deseja reconfigurar e tentar novamente? (s/n): ").strip().lower()
        if resp in {"s", "sim", "y", "yes"}:
            _escrever_toml_interativo(caminho_interativo)
            cfg = carregar_configuracao(caminho_interativo)
            armazenamento = selecionar_armazenamento(cfg)
            executar_backup(cfg, armazenamento)
        else:
            raise


if __name__ == "__main__":
    main()