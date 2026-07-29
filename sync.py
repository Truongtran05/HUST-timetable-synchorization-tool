from datetime import date

from exporter.export_to_app_script import main as export_to_app_script
from scraper.login import AUTH_FILE, save_login_state
from scraper.scraper import open_timetable
from standalize.standalize_data import main as standalize_data


def main() -> None:
    while True:
        try:
            semester_start = date.fromisoformat(input("Nhập ngày thứ Hai bắt đầu tuần 1 (YYYY-MM-DD): ").strip())
            if semester_start.weekday() != 0:
                raise ValueError
            break
        except ValueError:
            print("Ngày không hợp lệ; hãy nhập một ngày thứ Hai theo dạng YYYY-MM-DD.")

    if not AUTH_FILE.exists():
        save_login_state()

    print("1/3 Đang đọc lịch từ HUST...")
    open_timetable(wait_for_close=True)

    print("2/3 Đang chuẩn hóa lịch...")
    standalize_data(semester_start)

    print("3/3 Đang đồng bộ Google Sheet và Calendar...")
    export_to_app_script()


if __name__ == "__main__":
    main()
