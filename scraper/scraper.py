from pathlib import Path
from playwright.sync_api import sync_playwright
from scraper.parse_timetable import write_timetable_json

AUTH_FILE = Path("auth/office365.json")
OUTPUT_FILE = Path("store/timetable.json")
TIMETABLE_URL = "https://e.hust.edu.vn/students/learn/class-registration"
LOGIN_SUCCESS_URL = "https://e.hust.edu.vn/"


def timetable_scrapper(page) -> None:
    if not AUTH_FILE.exists():
        raise FileNotFoundError(
            "Chưa có auth/office365.json. "
            "Hãy chạy login.py trước."
        )

    page.goto(TIMETABLE_URL)

    page.get_by_text("Lịch học dự kiến").first.click()
    table = page.locator("table").filter(
        has=page.get_by_role("columnheader", name="Mã HP", exact=True)
    )
    table.locator("tbody tr.ant-table-row").first.wait_for()
    write_timetable_json(table.inner_html(), OUTPUT_FILE)

    print(f"Đã lưu thời khóa biểu tại: {OUTPUT_FILE}")


def open_timetable(wait_for_close: bool = True) -> None:
    if not AUTH_FILE.exists():
        raise FileNotFoundError(
            "Chưa có auth/office365.json. "
            "Hãy chạy login.py trước."
        )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
        )

        context = browser.new_context(
            storage_state=str(AUTH_FILE),
        )

        page = context.new_page()

        page.goto(
            TIMETABLE_URL,
            wait_until="networkidle",
        )

        print("URL hiện tại:", page.url)
        print("Tiêu đề:", page.title())

        page.get_by_role("button", name="Đăng nhập").click()

        page.wait_for_url(
            LOGIN_SUCCESS_URL,
            timeout=180_000,
        )

        timetable_scrapper(page)

        if wait_for_close:
            input("Nhấn Enter để đóng trình duyệt...")

        browser.close()


if __name__ == "__main__":
    open_timetable()
