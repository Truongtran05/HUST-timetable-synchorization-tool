import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sync


class SyncTest(unittest.TestCase):
    def test_runs_all_steps_in_order(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(sync, "AUTH_FILE", Path(directory) / "missing.json"),
                patch.object(sync, "save_login_state", side_effect=lambda: calls.append("login")),
                patch.object(sync, "open_timetable", side_effect=lambda **kwargs: calls.append(("scrape", kwargs))),
                patch.object(sync, "standalize_data", side_effect=lambda: calls.append("standalize")),
                patch.object(sync, "export_to_app_script", side_effect=lambda: calls.append("export")),
            ):
                sync.main()

        self.assertEqual(
            calls,
            ["login", ("scrape", {"wait_for_close": False}), "standalize", "export"],
        )


if __name__ == "__main__":
    unittest.main()
