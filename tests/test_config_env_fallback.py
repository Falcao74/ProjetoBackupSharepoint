import os
import unittest
from pathlib import Path

from backup.config import carregar_configuracao, ConfigAplicativo


class TestConfigEnvFallback(unittest.TestCase):
    def setUp(self):
        # Garante que credentials.toml não cause interferência
        self.credentials_path = Path("credentials.toml")
        self.had_file = self.credentials_path.exists()
        if self.had_file:
            # Renomeia temporariamente caso exista
            self.temp_path = Path("credentials.toml.bak")
            if self.temp_path.exists():
                self.temp_path.unlink()
            self.credentials_path.rename(self.temp_path)
        # Salva snapshot de env
        self.env_backup = dict(os.environ)

    def tearDown(self):
        # Restaura env
        os.environ.clear()
        os.environ.update(self.env_backup)
        # Restaura arquivo
        if hasattr(self, "temp_path") and self.temp_path.exists():
            self.temp_path.rename(self.credentials_path)

    def test_carregar_de_env_sucesso(self):
        os.environ["TENANT_ID"] = "TENANT-ENV"
        os.environ["CLIENT_ID"] = "CLIENT-ENV"
        os.environ["CLIENT_SECRET"] = "SECRET-ENV"
        os.environ["BACKUP_BACKEND"] = "local"
        os.environ["BACKUP_DIR"] = "backups_env"
        os.environ["SNAPSHOT_DIARIO"] = "false"
        os.environ["SITES"] = "siteA, siteB"

        cfg = carregar_configuracao()
        self.assertIsInstance(cfg, ConfigAplicativo)
        self.assertEqual(cfg.tenant_id, "TENANT-ENV")
        self.assertEqual(cfg.client_id, "CLIENT-ENV")
        self.assertEqual(cfg.client_secret, "SECRET-ENV")
        self.assertEqual(cfg.backup_backend, "local")
        self.assertEqual(cfg.backup_dir, "backups_env")
        self.assertEqual(cfg.snapshot_diario, False)
        self.assertEqual(cfg.sites, ["siteA", "siteB"])

    def test_sem_arquivo_sem_env_erro(self):
        # Sem arquivo e sem env obrigatórios deve gerar FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            carregar_configuracao()


if __name__ == "__main__":
    unittest.main()