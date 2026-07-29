from exporter.export_to_app_script import main as export_to_app_script
from scraper.login import AUTH_FILE, save_login_state
from scraper.scraper import open_timetable
from standalize.standalize_data import main as standalize_data


def main() -> None:
    if not AUTH_FILE.exists():
        save_login_state()

    print("1/3 Đang đọc lịch từ HUST...")
    open_timetable(wait_for_close=False)

    print("2/3 Đang chuẩn hóa lịch...")
    standalize_data()

    print("3/3 Đang đồng bộ Google Sheet và Calendar...")
    export_to_app_script()


if __name__ == "__main__":
    main()
