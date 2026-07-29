from pathlib import Path
from playwright.sync_api import sync_playwright
from scraper.parse_timetable import write_timetable_json

AUTH_FILE = Path("auth/office365.json")
OUTPUT_FILE = Path("store/timetable.json")
TIMETABLE_URL = "https://e.hust.edu.vn/students/learn/class-registration"
HOMEPAGE_URL = "https://e.hust.edu.vn/"
LOGIN_SUCCESS_URL ="https://e.hust.edu.vn/students/learn/timetable"

def timetable_scrapper(page) -> None:
    if not AUTH_FILE.exists():
        raise FileNotFoundError(
            "Chưa có auth/office365.json. "
            "Hãy chạy login.py trước."
        )

    page.goto(
        HOMEPAGE_URL,
        wait_until="networkidle",
    )
    page.wait_for_url(HOMEPAGE_URL, wait_until="networkidle", timeout=10000)

    login_button = page.get_by_role("button", name="Đăng nhập").first
    login_button.click()

    page.wait_for_url(LOGIN_SUCCESS_URL, wait_until="networkidle", timeout=10000)

    page.goto(
        TIMETABLE_URL,
        wait_until="networkidle",
    )
    page.wait_for_url(TIMETABLE_URL, wait_until="networkidle", timeout=10000)

    if page.url.rstrip("/") != TIMETABLE_URL:
        raise RuntimeError(
            f"HUST đã chuyển hướng tới {page.url}. "
            "Phiên đăng nhập có thể đã hết hạn; hãy xóa "
            "auth/office365.json rồi chạy lại."
        )

    nav_button = page.get_by_text("Lịch học dự kiến").first
    nav_button.click()

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
        timetable_scrapper(page)

        if wait_for_close:
            input("Nhấn Enter để đóng trình duyệt...")

        browser.close()


if __name__ == "__main__":
    open_timetable()
