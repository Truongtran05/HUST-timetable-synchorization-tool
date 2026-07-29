import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
DATA_FILE = PROJECT_ROOT / "store/standalize_table.json"
COLUMNS = ["date", "start_time", "end_time", "course_name", "course_code", "location"]


def load_env() -> None:
    if not ENV_FILE.exists():
        return

    # ponytail: chỉ hỗ trợ KEY=VALUE đơn giản; dùng python-dotenv nếu cần multiline/interpolation.
    for raw_line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
        key, separator, value = raw_line.partition("=")
        key = key.strip()
        if separator and key in {"APPS_SCRIPT_URL", "EXPORT_TOKEN"}:
            os.environ.setdefault(key, value.strip().strip("'\""))


def main() -> None:
    load_env()
    url = os.environ.get("APPS_SCRIPT_URL")
    token = os.environ.get("EXPORT_TOKEN")
    if not url or not token:
        raise ValueError("Hãy đặt APPS_SCRIPT_URL và EXPORT_TOKEN trong biến môi trường")

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError(f"Không có lịch học trong {DATA_FILE}")

    rows = [COLUMNS] + [[item[column] for column in COLUMNS] for item in data]
    request = Request(
        url,
        data=json.dumps({"token": token, "rows": rows}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError(result.get("error", "Apps Script trả về lỗi không xác định"))

    print(f"Đã export {len(data)} lịch học; tạo {result.get('createdEvents')} sự kiện")

if __name__ == "__main__":
    main()
