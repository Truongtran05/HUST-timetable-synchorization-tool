import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from exporter import export_to_app_script


class ExportTest(unittest.TestCase):
    def test_posts_rows_to_apps_script(self):
        item = {column: column for column in export_to_app_script.COLUMNS}
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"ok": true}'

        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "data.json"
            env_file = Path(directory) / ".env"
            data_file.write_text(json.dumps([item]), encoding="utf-8")
            env_file.write_text("APPS_SCRIPT_URL=https://example.test\nEXPORT_TOKEN=secret\n", encoding="utf-8")
            with (
                patch.dict(os.environ, {}, clear=True),
                patch.object(export_to_app_script, "ENV_FILE", env_file),
                patch.object(export_to_app_script, "DATA_FILE", data_file),
                patch.object(export_to_app_script, "urlopen", return_value=response) as urlopen,
            ):
                export_to_app_script.main()

        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["token"], "secret")
        self.assertEqual(payload["rows"], [export_to_app_script.COLUMNS, list(item.values())])


if __name__ == "__main__":
    unittest.main()
