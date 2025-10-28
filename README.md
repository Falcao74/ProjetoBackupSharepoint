<div align="center">

# 🚀 Backup de SharePoint (Microsoft Graph)

<br/>

<!-- Substitua USER/REPO abaixo pelo seu repositório GitHub -->
<img alt="Build" src="https://github.com/Falcao74/ProjetoBackupSharepoint/actions/workflows/ci.yml/badge.svg" />

<img alt="Microsoft" src="https://img.shields.io/badge/Microsoft%20365-Graph-blue?logo=microsoft" />
<img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" />
<img alt="MSAL" src="https://img.shields.io/badge/Auth-MSAL-green" />
<img alt="Requests" src="https://img.shields.io/badge/HTTP-requests-000000?logo=python" />
<img alt="Boto3" src="https://img.shields.io/badge/AWS-boto3-ff9900?logo=amazonaws&logoColor=white" />
<img alt="Azure Blob" src="https://img.shields.io/badge/Azure-Blob%20Storage-0078D4?logo=microsoftazure&logoColor=white" />
<img alt="Windows" src="https://img.shields.io/badge/Windows-PowerShell-00A4EF?logo=windows&logoColor=white" />

<br/>

Aplicativo simples e direto para fazer backup diário de arquivos do SharePoint usando o Microsoft Graph. Ideal para ambientes on‑premise, com suporte a armazenamento Local, S3 e Azure Blob. Comentários e nomes em Português do Brasil, seguindo princípios SOLID. 🧩

</div>

---

> English version: see `README.en.md`.

## 🧭 Sumário
- 🎯 Visão Geral
- 🌟 Recursos
- 🧱 Arquitetura
- ✅ Pré‑requisitos
- 📦 Instalação
- 🔐 Configuração (TOML e variáveis de ambiente)
- ▶️ Execução
- 🧪 Testes (Mock e Fallback de Ambiente)
- 🗂️ Estrutura de Saída
- 🔄 Como Funciona (passo a passo)
- ⏰ Agendamento (Windows Task Scheduler)
- 🛡️ Segurança de Credenciais
- 🧰 Troubleshooting
- 🗺️ Roadmap
- 🤝 Contribuição

---

## 🎯 Visão Geral
Este projeto realiza um snapshot diário dos arquivos dos sites do SharePoint de um tenant Microsoft 365 e detecta arquivos apagados desde o último snapshot. Você escolhe o backend de armazenamento: local (filesystem), Amazon S3 ou Azure Blob.

---

## 🌟 Recursos
- 🗓️ Snapshot completo diário em `snapshots/YYYY-MM-DD`.
- 🧹 Detecção de removidos e cópia para `deleted/YYYY-MM-DD`.
- 🏷️ Suporte a múltiplos sites (IDs ou resource paths).
- 🔐 Autenticação via MSAL usando permissões de aplicativo.
- 🛠️ Código modular: `config`, `auth`, `graph`, `storage`, `runner`.
- 🧪 Testes mock sem tocar na API real (Graph simulado).

---

## 🧱 Arquitetura
- **Módulos**
  - `backup/config.py`: carrega configuração (TOML ou variáveis de ambiente).
  - `backup/auth.py`: obtém token (`obter_token`).
  - `backup/graph.py`: integra com Microsoft Graph (SharePoint).
  - `backup/graph_mock.py`: cliente mock do Graph para testes.
  - `backup/storage/…`: backends Local, S3 e Azure Blob.
  - `backup/runner.py`: orquestra o backup diário.
  - `app.py`: ponto de entrada.
- **Princípios SOLID**
  - Responsabilidade única e inversão de dependência no backend de armazenamento.
  - Open/Closed: novos backends podem ser adicionados sem alterar o runner.

---

## ✅ Pré‑requisitos
- Python 3.11+.
- App Registration no Azure AD com permissões de aplicativo:
  - `Sites.Read.All`
  - `Files.Read.All`
  - Consentimento do administrador.

---

## 📦 Instalação
No diretório do projeto:
```
env\Scripts\pip.exe install -r requirements.txt
```

---

## 🔐 Configuração
### Opção A: arquivo TOML
1. Copie `credentials.example.toml` para `credentials.toml`.
2. Preencha:
   - `tenant_id`, `client_id`, `client_secret`.
   - `backup_backend`: `local` | `s3` | `azure_blob`.
   - Para `local`: `backup_dir` (ex.: `backups`).
   - Para `s3`: `[s3]` com `bucket_name`, `region_name`, `aws_access_key_id`, `aws_secret_access_key`.
   - Para `azure_blob`: `[azure_blob]` com `connection_string`, `container_name`.
   - Opcional: `sites` (IDs ou resource paths: `contoso.sharepoint.com:/sites/Finance`).

> Importante: `credentials.toml` é privado e já está em `.gitignore`. Não faça commit.

### Opção B: variáveis de ambiente (sem arquivo)
Defina no Windows (PowerShell):
```
$env:TENANT_ID = "seu-tenant"
$env:CLIENT_ID = "seu-client-id"
$env:CLIENT_SECRET = "seu-secret"
$env:BACKUP_BACKEND = "local"  # ou s3 / azure_blob
$env:BACKUP_DIR = "backups"
$env:SNAPSHOT_DIARIO = "true"   # ou false
$env:SITES = "contoso.sharepoint.com:/sites/Finance,contoso.sharepoint.com:/sites/TI"

# S3
$env:S3_BUCKET_NAME = "seu-bucket"
$env:S3_REGION_NAME = "us-east-1"
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "..."

# Azure Blob
$env:AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=..."
$env:AZURE_CONTAINER_NAME = "seu-container"
```
O carregador tenta `credentials.toml`; se não existir, usa variáveis de ambiente.

---

## ▶️ Execução
```
env\Scripts\python.exe app.py
```

---

## 🧪 Testes (Mock)
- Teste do fluxo de backup com Graph simulado:
```
env\Scripts\python.exe -m unittest tests.test_mock_backup
```
- Teste de fallback de variáveis de ambiente (sem `credentials.toml`):
```
env\Scripts\python.exe -m unittest tests.test_config_env_fallback
```

---

## 🗂️ Estrutura de Saída
- Local:
  - `backups/snapshots/YYYY-MM-DD/<Site>/<Drive>/...`
  - `backups/deleted/YYYY-MM-DD/...`
- S3/Azure Blob: mesmos prefixos no bucket/container.
- Estado local: `state/latest_manifest.json` e `state/latest_snapshot.txt`.

---

## 🔄 Como Funciona (passo a passo)
1. Carrega configuração (arquivo ou env).
2. Obtém token via MSAL (`obter_token`).
3. Resolve sites e bibliotecas (drives) do SharePoint.
4. Percorre pastas/arquivos via Graph, baixa conteúdo em stream.
5. Escreve arquivos no backend selecionado e monta manifesto.
6. Compara manifesto atual vs anterior para detectar removidos.
7. Copia removidos para `deleted/YYYY-MM-DD`.
8. Salva estado para próxima execução.

---

## ⏰ Agendamento (Windows Task Scheduler)
- Abra Agendador de Tarefas e crie uma tarefa diária.
- Ação: `Program/script` = `c:\...\env\Scripts\python.exe`
- Argumentos: `c:\...\app.py`
- Condições: habilite conforme sua política.

---

## ⚙️ Executar via GitHub Actions (alternativa)

Este repositório inclui um workflow agendado (`.github/workflows/backup.yml`) que roda diariamente às 03:00 UTC e pode ser acionado manualmente.

### Segredos necessários (Settings → Secrets and variables → Actions)
- `TENANT_ID` (Azure AD)
- `CLIENT_ID` (App Registration)
- `CLIENT_SECRET`
- Para S3: `S3_BUCKET_NAME`, `S3_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Para Azure Blob: `AZURE_CONNECTION_STRING`, `AZURE_CONTAINER_NAME`
- Opcional: `SITES` (lista separada por vírgulas)

### Como usar
- No `backup.yml`, o backend padrão está como `s3`. Ajuste `BACKUP_BACKEND` para `azure_blob` se preferir.
- Acesse a aba `Actions` no GitHub para:
  - Ver o agendamento diário às 03:00 UTC.
  - Rodar manualmente via botão "Run workflow" (`workflow_dispatch`).
- Importante: não use `local` como backend no Actions; runners são efêmeros.

---

## 🛡️ Segurança de Credenciais
- Nunca faça commit de `credentials.toml`.
- Prefira variáveis de ambiente ou um vault (Azure Key Vault, etc.).
- Revogue/rotacione `client_secret` periodicamente.

---

## 🧰 Troubleshooting
- Erro de autenticação (MSAL): verifique `tenant_id`, `client_id`, `client_secret` e consentimentos.
- Lista de sites vazia: confirme os resource paths ou IDs.
- Permissões insuficientes: garanta `Sites.Read.All` e `Files.Read.All` como Application e admin consent.
- Tempo de execução longo: limite `sites` ou execute em horários de menor uso.

---

## 🗺️ Roadmap
- Logs estruturados com níveis e telemetria.
- Filtros por biblioteca/document library.
- Retentativas e controle de taxa.
- Compressão de snapshots locais.

---

## 🤝 Contribuição
- Issues, dúvidas e melhorias são bem‑vindas.
- Padronize nomes em pt‑BR e mantenha o estilo existente.