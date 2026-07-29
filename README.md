# HUST Timetable to Google Calendar

Công cụ tự động lấy **thời khóa biểu tạm thời** trên trang đăng ký lớp của
Đại học Bách khoa Hà Nội, chuẩn hóa lịch theo từng tuần, ghi dữ liệu vào Google
Sheets và tạo sự kiện trên Google Calendar.

Sau khi cài đặt xong, toàn bộ quy trình được chạy bằng một lệnh:

```powershell
.\.venv\Scripts\python.exe .\sync.py
```

> [!WARNING]
> `deleteAllExtraStudyEvents()` trong `exporter/google_apps_script.gs` hiện xóa
> **toàn bộ sự kiện** của calendar có tên `CALENDAR_NAME` trong khoảng
> `START_DATE`–`END_DATE` trước khi tạo lại lịch. Hãy dùng một calendar riêng
> chỉ dành cho lịch học, đặt đúng khoảng ngày, và đọc mục
> [Cấu hình Google Calendar](#4-cấu-hình-google-calendar) trước khi chạy.

## Chức năng

- Đăng nhập `e.hust.edu.vn` qua Microsoft/Office 365 và lưu phiên đăng nhập cục bộ.
- Đọc bảng **Lịch học dự kiến** trên trang đăng ký lớp.
- Tách tuần học, thứ, giờ học, mã học phần, tên học phần và phòng học.
- Chuyển tuần học thành ngày cụ thể dựa trên ngày thứ Hai của tuần 1.
- Ghi dữ liệu đã chuẩn hóa vào Google Sheets qua Apps Script Web App.
- Tạo sự kiện Google Calendar với tiêu đề `Mã HP - Tên học phần`.

## Luồng hoạt động

```text
e.hust.edu.vn
      │
      ▼
store/timetable.json
      │
      ▼
store/standalize_table.json
      │
      ▼
Google Apps Script Web App
      ├── Google Sheet: tab Timetable
      └── Google Calendar: tạo sự kiện lịch học
```

`auth/`, `store/`, `.env` và `.venv` đều được Git bỏ qua. Vì vậy khi clone repo
trên máy mới, bạn phải cài môi trường và cấu hình lại thông tin Google; token
đăng nhập HUST cũng được tạo lại trên chính máy đó.

## Yêu cầu

- Windows 10/11 và PowerShell.
- Python 3.10 trở lên.
- Tài khoản sinh viên truy cập được `https://e.hust.edu.vn/`.
- Một tài khoản Google có quyền dùng Google Sheets, Apps Script và Calendar.

Không cần Google Cloud Console, service account hay file credentials JSON của
Google.

## Cài đặt trên máy mới

### 1. Clone và cài Python

```powershell
git clone <URL_REPOSITORY>
cd calender_sync
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

Nếu máy không nhận lệnh `py`, thay `py` bằng `python` ở lệnh tạo môi trường ảo.
Không bắt buộc kích hoạt virtual environment vì các lệnh trong README gọi trực
tiếp Python bên trong `.venv`.

### 2. Tạo Google Sheet

1. Tạo một Google Spreadsheet mới.
2. Đổi tên tab cần ghi dữ liệu thành `Timetable`.
3. Lấy Spreadsheet ID từ URL:

   ```text
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

   Phần nằm giữa `/d/` và `/edit` chính là `SPREADSHEET_ID`.

Không cần tự tạo tiêu đề cột. Mỗi lần chạy, Apps Script sẽ xóa nội dung tab và
ghi lại sáu cột:

```text
date | start_time | end_time | course_name | course_code | location
```

### 3. Tạo và cấu hình Google Apps Script

1. Trong Google Sheet, mở **Extensions → Apps Script**.
2. Mở file `exporter/google_apps_script.gs` trong repo, sao chép toàn bộ nội
   dung vào file `Code.gs` của Apps Script.
3. Thay giá trị sau bằng ID lấy ở bước trên:

   ```javascript
   const SPREADSHEET_ID = "DIEN_SPREADSHEET_ID_VAO_DAY";
   ```

4. Nếu tab không tên `Timetable`, sửa `WORKSHEET_NAME` cho khớp chính xác. Cách
   đơn giản nhất là giữ nguyên tên tab `Timetable`.
5. Trong Apps Script, mở **Project Settings → Script properties → Add script
   property** và tạo:

   | Property | Value |
   |---|---|
   | `EXPORT_TOKEN` | Một chuỗi bí mật dài do bạn tự tạo |

Có thể tạo token ngay trong PowerShell:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
```

Sao chép kết quả để dùng **giống hệt nhau** trong Script Properties và file
`.env`. Đây là secret riêng của ứng dụng, không phải Google OAuth token và không
phải Spreadsheet ID. Không commit token lên GitHub.

### 4. Cấu hình Google Calendar

Trong `Code.gs`, tìm hàm `deleteAllExtraStudyEvents()` và sửa:

```javascript
const CALENDAR_NAME = 'TEN_LICH_TREN_GG_CALENDAR_LUU_LICH_HOC';
const START_DATE = new Date('2026-08-01T00:00:00+07:00');
const END_DATE   = new Date('2026-12-31T23:59:59+07:00');
```

- `CALENDAR_NAME`: tên hiển thị chính xác của calendar sẽ bị dọn dữ liệu.
- `START_DATE`, `END_DATE`: khoảng ngày của học kỳ, múi giờ `+07:00`.
- Code hiện tại không dùng Calendar ID; nó tìm calendar bằng tên.
- `autoFill()` tạo sự kiện bằng `CalendarApp.getDefaultCalendar()`. Vì vậy, với
  code hiện tại, `CALENDAR_NAME` phải trỏ đến chính default calendar nếu muốn
  xóa và tạo trên cùng một lịch.

> [!CAUTION]
> Cách hoạt động hiện tại có thể xóa cả sự kiện cá nhân trong default calendar.
> Chỉ tiếp tục khi calendar và khoảng ngày trên không chứa dữ liệu cần giữ.

Trong Apps Script editor:

1. Chọn hàm `authorizeSpreadsheet` rồi bấm **Run**.
2. Chọn tài khoản Google, mở **Advanced** nếu Google hiển thị cảnh báo ứng dụng
   chưa xác minh, sau đó cho phép project truy cập Sheet và Calendar.
3. Chạy `testAutoFillDateParsing`; hàm kết thúc không có lỗi nghĩa là định dạng
   ngày giờ hợp lệ.

Không chạy thủ công `autoFill()` trước khi đã kiểm tra kỹ cảnh báo xóa dữ liệu.

### 5. Deploy Apps Script thành Web App

1. Chọn **Deploy → New deployment**.
2. Chọn loại **Web app**.
3. Đặt **Execute as** thành **Me**.
4. Đặt quyền truy cập thành **Anyone** để chương trình Python có thể POST tới
   endpoint; request vẫn phải có `EXPORT_TOKEN` mới được chấp nhận.
5. Bấm **Deploy** và sao chép Web App URL có dạng:

   ```text
   https://script.google.com/macros/s/DEPLOYMENT_ID/exec
   ```

Phải dùng URL kết thúc bằng `/exec`, không dùng URL editor kết thúc bằng `/edit`.
Mỗi khi sửa `Code.gs`, vào **Deploy → Manage deployments → Edit**, chọn
**New version** rồi deploy lại; nếu không, `/exec` có thể vẫn chạy code cũ.

### 6. Tạo file `.env`

Tạo file `.env` tại thư mục gốc của repo:

```dotenv
APPS_SCRIPT_URL=https://script.google.com/macros/s/DEPLOYMENT_ID/exec
EXPORT_TOKEN=TOKEN_DA_LUU_TRONG_SCRIPT_PROPERTIES
```

`APPS_SCRIPT_URL` là URL Web App ở bước 5. `EXPORT_TOKEN` phải trùng tuyệt đối
với Script Property ở bước 3. File `.env` đã nằm trong `.gitignore`.

### 7. Chạy đồng bộ

Đảm bảo bạn đã đăng ký lớp và trang HUST đã có bảng **Lịch học dự kiến**, sau đó
chạy tại thư mục gốc:

```powershell
.\.venv\Scripts\python.exe .\sync.py
```

Nhập ngày thứ Hai bắt đầu tuần 1 theo định dạng `YYYY-MM-DD`, ví dụ:

```text
Nhập ngày thứ Hai bắt đầu tuần 1 (YYYY-MM-DD): 2026-09-07
```

Ở lần chạy đầu tiên:

1. Chromium mở trang đăng nhập HUST.
2. Tool chọn đăng nhập Office 365.
3. Bạn hoàn tất tài khoản Microsoft và MFA trong cửa sổ trình duyệt.
4. Phiên đăng nhập được lưu vào `auth/office365.json`.
5. Tool mở trang đăng ký lớp, lấy thời khóa biểu, ghi Sheet và gọi Calendar.

Kết quả thành công có dạng:

```text
1/3 Đang đọc lịch từ HUST...
2/3 Đang chuẩn hóa lịch...
3/3 Đang đồng bộ Google Sheet và Calendar...
Đã export 120 lịch học; tạo 120 sự kiện
```

Số dòng và số sự kiện thực tế phụ thuộc thời khóa biểu. `tạo 0 sự kiện` có thể
có nghĩa các sự kiện cùng tiêu đề, giờ bắt đầu và giờ kết thúc đã tồn tại.

## Chạy kiểm tra

```powershell
.\.venv\Scripts\python.exe -m unittest test_sync exporter.test_export_to_app_script -v
```

Các test kiểm tra luồng gọi và payload HTTP bằng mock; chúng không đăng nhập
HUST và không tạo dữ liệu thật trên Google.

## Chạy lại và làm mới đăng nhập HUST

Các lần sau vẫn dùng cùng lệnh `sync.py`. Nếu phiên HUST hết hạn hoặc đăng nhập
lỗi, xóa file cục bộ `auth/office365.json` rồi chạy lại để đăng nhập và tạo phiên
mới:

```powershell
Remove-Item -LiteralPath .\auth\office365.json
.\.venv\Scripts\python.exe .\sync.py
```

## Xử lý lỗi thường gặp

### `Hãy đặt APPS_SCRIPT_URL và EXPORT_TOKEN trong biến môi trường`

File `.env` chưa tồn tại, đặt sai thư mục, sai tên biến hoặc giá trị đang rỗng.
File phải nằm cạnh `sync.py`.

### `JSONDecodeError: Expecting value`

Thường do `APPS_SCRIPT_URL` là URL `/edit` và server trả HTML thay vì JSON. Hãy
dùng URL Web App `/exec` và kiểm tra deployment.

### `Unauthorized`

`EXPORT_TOKEN` trong `.env` không trùng Script Property `EXPORT_TOKEN`. Không
dùng OAuth token của Google cho giá trị này.

### `Không tìm thấy sheet Timetable`

Tên tab trong Spreadsheet không khớp `WORKSHEET_NAME`. Tên file Google Sheet
không phải tên tab.

### Sheet cập nhật nhưng Calendar không có sự kiện

- Deploy một **New version** của Web App sau khi sửa Apps Script.
- Kiểm tra mục **Executions** trong Apps Script để xem lỗi quyền Calendar.
- Xác nhận tài khoản tại **Execute as: Me** sở hữu đúng default calendar.
- Xem số `createdEvents` được in sau khi chạy: `0` có thể do chống trùng; giá trị
  không xuất hiện thường cho thấy deployment đang chạy phiên bản cũ.

### Không tìm thấy bảng hoặc Playwright bị timeout

- Xác nhận trang đăng ký lớp đang có mục **Lịch học dự kiến** và cột **Mã HP**.
- Xóa `auth/office365.json` rồi đăng nhập lại nếu phiên đã hết hạn.
- Cài lại Chromium bằng `python -m playwright install chromium` như bước 1.

## Cấu trúc thư mục

```text
calender_sync/
├── sync.py                         # Chạy toàn bộ quy trình
├── scraper/                        # Đăng nhập và lấy bảng lịch HUST
├── standalize/                     # Chuyển tuần/thứ/tiết thành ngày giờ
├── config/time_config.py           # Ánh xạ tiết học sang giờ
├── exporter/
│   ├── export_to_app_script.py     # POST dữ liệu sang Web App
│   └── google_apps_script.gs       # Ghi Sheet và tạo Calendar event
├── auth/                            # Phiên HUST, không commit
├── store/                           # JSON trung gian, không commit
├── .env                             # URL và token, không commit
└── requirements.txt
```

## Lưu ý bảo mật và giới hạn
- Nếu token từng bị lộ, tạo token mới và cập nhật cả Script Properties lẫn
  `.env`.
- Web App chạy dưới tài khoản Google của người deploy, nên Sheet và Calendar
  được thao tác bằng quyền của tài khoản đó.
- Tool phụ thuộc giao diện hiện tại của `e.hust.edu.vn`; nếu HUST đổi tên nút,
  cột hoặc cấu trúc bảng thì scraper có thể cần cập nhật.
- Tool chỉ phản ánh **lịch học dự kiến** tại thời điểm chạy; hãy chạy lại sau khi
  lịch đăng ký thay đổi.
