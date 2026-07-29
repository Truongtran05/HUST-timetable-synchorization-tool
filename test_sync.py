import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import sync


class SyncTest(unittest.TestCase):
    def test_runs_all_steps_in_order(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch("builtins.input", return_value="2026-09-07"),
                patch.object(sync, "AUTH_FILE", Path(directory) / "missing.json"),
                patch.object(sync, "save_login_state", side_effect=lambda: calls.append("login")),
                patch.object(sync, "open_timetable", side_effect=lambda **kwargs: calls.append(("scrape", kwargs))),
                patch.object(sync, "standalize_data", side_effect=lambda value: calls.append(("standalize", value))),
                patch.object(sync, "export_to_app_script", side_effect=lambda: calls.append("export")),
            ):
                sync.main()

        self.assertEqual(
            calls,
            ["login", ("scrape", {"wait_for_close": False}), ("standalize", date(2026, 9, 7)), "export"],
        )

    def test_reprompts_until_start_date_is_a_monday(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch("builtins.input", side_effect=["sai", "2026-09-08", "2026-09-07"]),
                patch.object(sync, "AUTH_FILE", Path(directory)),
                patch.object(sync, "open_timetable"),
                patch.object(sync, "standalize_data") as standalize_data,
                patch.object(sync, "export_to_app_script"),
            ):
                sync.main()

        standalize_data.assert_called_once_with(date(2026, 9, 7))


if __name__ == "__main__":
    unittest.main()
