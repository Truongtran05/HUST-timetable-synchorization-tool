from pathlib import Path

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://e.hust.edu.vn/sso/login"
LOGIN_SUCCESS_URL = "https://e.hust.edu.vn/"
AUTH_FILE = Path("auth/office365.json")


def save_login_state() -> None:
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            slow_mo=300,
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(
            LOGIN_URL,
            wait_until="domcontentloaded",
        )

        print("Đang mở trang đăng nhập...")
        page.locator("button.social-btn.office").click()

        print(
            "Hãy hoàn tất đăng nhập Microsoft và xác minh MFA "
            "trong cửa sổ trình duyệt."
        )

        page.wait_for_url(
            LOGIN_SUCCESS_URL,
            timeout=180_000,
        )

        context.storage_state(path=str(AUTH_FILE))

        print(f"Đã lưu trạng thái đăng nhập tại: {AUTH_FILE}")

        browser.close()


if __name__ == "__main__":
    save_login_state()
