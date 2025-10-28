import os
import shutil
import unittest
from datetime import datetime, timezone
from pathlib import Path

from backup.runner import executar_backup, graph as graph_real
from backup import graph_mock
from backup.config import ConfigAplicativo
from backup.storage.local import ArmazenamentoLocal


class TestBackupMock(unittest.TestCase):
    def setUp(self):
        # Diretório isolado para testes
        self.dir_saida = Path("backups_mock")
        if self.dir_saida.exists():
            shutil.rmtree(self.dir_saida)
        self.dir_saida.mkdir(parents=True, exist_ok=True)
        # Limpa estado para não interferir com execuções reais
        self.dir_estado = Path("state")
        if self.dir_estado.exists():
            shutil.rmtree(self.dir_estado)

        # Configuração mock (valores de credenciais não são usados pelo Graph mock)
        self.cfg = ConfigAplicativo(
            tenant_id="TENANT-MOCK",
            client_id="CLIENT-MOCK",
            client_secret="SECRET-MOCK",
            backup_backend="local",
            backup_dir=str(self.dir_saida),
            snapshot_diario=True,
            sites=[],
        )

        # Backend local apontando para backups_mock
        self.backend = ArmazenamentoLocal(self.cfg.backup_dir)

        # Monkeypatch do módulo graph no runner para usar mock
        # (Importado como atributo em backup.runner; substituímos e restauramos no tearDown)
        self.graph_original = graph_real
        import backup.runner as runner_mod
        runner_mod.graph = graph_mock

        # Monkeypatch de obter_token para não chamar MSAL
        self.obter_token_original = runner_mod.obter_token
        runner_mod.obter_token = lambda tenant, client, secret: "TOKEN-MOCK"

    def tearDown(self):
        # Restaura monkeypatches
        import backup.runner as runner_mod
        runner_mod.graph = self.graph_original
        runner_mod.obter_token = self.obter_token_original

        # Limpa diretórios de teste
        if self.dir_saida.exists():
            shutil.rmtree(self.dir_saida)
        if self.dir_estado.exists():
            shutil.rmtree(self.dir_estado)

    def test_fluxo_backup_mock(self):
        # Executa backup com cliente Graph mock
        executar_backup(self.cfg, self.backend)

        # Verifica saída esperada
        hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        caminho_arquivo = self.dir_saida / "snapshots" / hoje / "SiteMock" / "DriveMock" / "docs" / "relatorio.txt"
        self.assertTrue(caminho_arquivo.exists(), f"Arquivo esperado não foi criado: {caminho_arquivo}")

        # Verifica que estado foi gerado
        manifesto = Path("state") / "latest_manifest.json"
        self.assertTrue(manifesto.exists(), "Manifesto de estado não foi criado.")


if __name__ == "__main__":
    unittest.main()