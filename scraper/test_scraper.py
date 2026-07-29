import unittest
from unittest.mock import Mock, patch

from scraper.scraper import TIMETABLE_URL, timetable_scrapper


class TimetableScrapperTest(unittest.TestCase):
    @patch("scraper.scraper.AUTH_FILE")
    def test_reports_redirect_before_looking_for_timetable(self, auth_file) -> None:
        auth_file.exists.return_value = True
        page = Mock(url="https://e.hust.edu.vn/students")

        with self.assertRaisesRegex(RuntimeError, "đã chuyển hướng"):
            timetable_scrapper(page)

        page.goto.assert_called_once_with(TIMETABLE_URL, wait_until="networkidle")
        page.get_by_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()
