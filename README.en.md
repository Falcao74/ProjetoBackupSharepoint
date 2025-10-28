<div align="center">

# 🚀 SharePoint Backup (Microsoft Graph)

<br/>

<!-- Replace USER/REPO with your GitHub repository -->
<img alt="Build" src="https://github.com/Falcao74/ProjetoBackupSharepoint/actions/workflows/ci.yml/badge.svg" />

<img alt="Microsoft" src="https://img.shields.io/badge/Microsoft%20365-Graph-blue?logo=microsoft" />
<img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" />
<img alt="MSAL" src="https://img.shields.io/badge/Auth-MSAL-green" />
<img alt="Requests" src="https://img.shields.io/badge/HTTP-requests-000000?logo=python" />
<img alt="Boto3" src="https://img.shields.io/badge/AWS-boto3-ff9900?logo=amazonaws&logoColor=white" />
<img alt="Azure Blob" src="https://img.shields.io/badge/Azure-Blob%20Storage-0078D4?logo=microsoftazure&logoColor=white" />
<img alt="Windows" src="https://img.shields.io/badge/Windows-PowerShell-00A4EF?logo=windows&logoColor=white" />

<br/>

Straightforward daily backup for SharePoint files using Microsoft Graph. Suitable for on‑premise setups, supporting Local storage, S3 and Azure Blob. Code comments and identifiers are in Brazilian Portuguese, following SOLID principles. 🧩

</div>

---

## 🧭 Table of Contents
- 🎯 Overview
- 🌟 Features
- 🧱 Architecture
- ✅ Prerequisites
- 📦 Installation
- 🔐 Configuration (TOML and environment variables)
- ▶️ Run
- 🧪 Tests (Mock and Env Fallback)
- 🗂️ Output Structure
- 🔄 How It Works (step by step)
- ⏰ Scheduling (Windows Task Scheduler)
- 🛡️ Credentials Security
- 🧰 Troubleshooting
- 🗺️ Roadmap
- 🤝 Contributing

---

## 🎯 Overview
This project performs a daily snapshot of SharePoint sites files in a Microsoft 365 tenant and detects files deleted since the last snapshot. You can choose the storage backend: local filesystem, Amazon S3 or Azure Blob.

---

## 🌟 Features
- 🗓️ Full daily snapshot at `snapshots/YYYY-MM-DD`.
- 🧹 Deleted items detection copied to `deleted/YYYY-MM-DD`.
- 🏷️ Multiple sites support (IDs or resource paths).
- 🔐 MSAL authentication (application permissions).
- 🛠️ Modular code: `config`, `auth`, `graph`, `storage`, `runner`.
- 🧪 Mock tests without hitting the real API.

---

## 🧱 Architecture
- **Modules**
  - `backup/config.py`: loads configuration (TOML or env vars).
  - `backup/auth.py`: obtains token (`obter_token`).
  - `backup/graph.py`: Microsoft Graph integration (SharePoint).
  - `backup/graph_mock.py`: mock Graph client for tests.
  - `backup/storage/…`: Local, S3 and Azure Blob backends.
  - `backup/runner.py`: orchestrates the daily backup.
  - `app.py`: entry point.
- **SOLID principles**
  - Single responsibility and dependency inversion on storage backend.
  - Open/Closed: new backends can be added without changing runner.

---

## ✅ Prerequisites
- Python 3.11+.
- Azure AD App Registration with application permissions:
  - `Sites.Read.All`
  - `Files.Read.All`
  - Admin consent.

---

## 📦 Installation
In the project directory:
```
env\Scripts\pip.exe install -r requirements.txt
```

---

## 🔐 Configuration
### Option A: TOML file
1. Copy `credentials.example.toml` to `credentials.toml`.
2. Fill in:
   - `tenant_id`, `client_id`, `client_secret`.
   - `backup_backend`: `local` | `s3` | `azure_blob`.
   - For `local`: `backup_dir` (e.g., `backups`).
   - For `s3`: `[s3]` with `bucket_name`, `region_name`, `aws_access_key_id`, `aws_secret_access_key`.
   - For `azure_blob`: `[azure_blob]` with `connection_string`, `container_name`.
   - Optional: `sites` (IDs or resource paths: `contoso.sharepoint.com:/sites/Finance`).

> Important: `credentials.toml` is private and already in `.gitignore`. Do not commit.

### Option B: environment variables (no file)
Set in Windows (PowerShell):
```
$env:TENANT_ID = "your-tenant"
$env:CLIENT_ID = "your-client-id"
$env:CLIENT_SECRET = "your-secret"
$env:BACKUP_BACKEND = "local"  # or s3 / azure_blob
$env:BACKUP_DIR = "backups"
$env:SNAPSHOT_DIARIO = "true"   # or false
$env:SITES = "contoso.sharepoint.com:/sites/Finance,contoso.sharepoint.com:/sites/IT"

# S3
$env:S3_BUCKET_NAME = "your-bucket"
$env:S3_REGION_NAME = "us-east-1"
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "..."

# Azure Blob
$env:AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=..."
$env:AZURE_CONTAINER_NAME = "your-container"
```
The loader tries `credentials.toml`; if not present, it uses environment variables.

---

## ▶️ Run
```
env\Scripts\python.exe app.py
```

---

## 🧪 Tests (Mock)
- Mock backup flow:
```
env\Scripts\python.exe -m unittest tests.test_mock_backup
```
- Env fallback test (no `credentials.toml`):
```
env\Scripts\python.exe -m unittest tests.test_config_env_fallback
```

---

## 🗂️ Output Structure
- Local:
  - `backups/snapshots/YYYY-MM-DD/<Site>/<Drive>/...`
  - `backups/deleted/YYYY-MM-DD/...`
- S3/Azure Blob: same prefixes on bucket/container.
- Local state: `state/latest_manifest.json` and `state/latest_snapshot.txt`.

---

## 🔄 How It Works (step by step)
1. Load configuration (file or env).
2. Obtain token via MSAL (`obter_token`).
3. Resolve SharePoint sites and document libraries (drives).
4. Traverse folders/files via Graph, download content in stream.
5. Write files to the selected backend and build the manifest.
6. Compare current vs previous manifest to detect deleted items.
7. Copy deleted items to `deleted/YYYY-MM-DD`.
8. Save state for next run.

---

## ⏰ Scheduling (Windows Task Scheduler)
- Open Task Scheduler, create a daily task.
- Action: `Program/script` = `c:\...\env\Scripts\python.exe`
- Arguments: `c:\...\app.py`
- Conditions: enable according to your policy.

---

## 🛡️ Credentials Security
- Never commit `credentials.toml`.
- Prefer environment variables or a vault (Azure Key Vault, etc.).
- Rotate `client_secret` periodically.

---

## 🧰 Troubleshooting
- Authentication error (MSAL): check `tenant_id`, `client_id`, `client_secret` and admin consent.
- Empty site list: confirm resource paths or IDs.
- Insufficient permissions: ensure `Sites.Read.All` and `Files.Read.All` as Application with admin consent.
- Long runtime: limit `sites` or schedule off-peak hours.

---

## 🗺️ Roadmap
- Structured logs and telemetry.
- Filters by document library.
- Retries and rate control.
- Local snapshot compression.

---

## 🤝 Contributing
- Issues, questions and improvements are welcome.
- Keep pt‑BR identifiers and match the existing style.