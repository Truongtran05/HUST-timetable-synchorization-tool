const SPREADSHEET_ID = "DIEN_SPREADSHEET_ID_VAO_DAY";
const WORKSHEET_NAME = "Timetable";
const TIME_ZONE = "Asia/Ho_Chi_Minh";

function authorizeSpreadsheet() {
  SpreadsheetApp.openById(SPREADSHEET_ID).getName();
}

function autoFill() {
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(WORKSHEET_NAME);
  if (!sheet) throw new Error(`Không tìm thấy sheet ${WORKSHEET_NAME}`);
  if (sheet.getLastRow() < 2) return 0;

  const rows = sheet.getRange(2, 1, sheet.getLastRow() - 1, 6).getValues();
  const items = rows.filter(row => row[0]).map((row, index) => {
    const [date, startTime, endTime, courseName, courseCode, location] = row;
    if (!startTime || !endTime || !courseName || !courseCode) {
      throw new Error(`Thiếu dữ liệu bắt buộc ở dòng ${index + 2}`);
    }

    const start = parseDateTime(date, startTime);
    const end = parseDateTime(date, endTime);
    if (end <= start) throw new Error(`Giờ kết thúc không hợp lệ ở dòng ${index + 2}`);

    return {
      title: `${courseCode} - ${courseName}`,
      start,
      end,
      location: String(location || ""),
      description: `Mã học phần: ${courseCode}`,
    };
  });
  if (!items.length) return 0;

  deleteAllExtraStudyEvents()

  const calendar = CalendarApp.getDefaultCalendar();
  const rangeStart = new Date(Math.min(...items.map(item => item.start.getTime())));
  const rangeEnd = new Date(Math.max(...items.map(item => item.end.getTime())));
  const existing = new Set(
    calendar
      .getEvents(rangeStart, rangeEnd)
      .map(event => eventKey(event.getTitle(), event.getStartTime(), event.getEndTime())),
  );

  let created = 0;
  for (const item of items) {
    const key = eventKey(item.title, item.start, item.end);
    if (existing.has(key)) continue;

    calendar.createEvent(item.title, item.start, item.end, {
      location: item.location,
      description: item.description,
    });
    existing.add(key);
    created++;
  }

  console.log(`Đã tạo ${created}/${items.length} sự kiện`);
  return created;
}

function parseDateTime(date, time) {
  const dateText = date instanceof Date ? Utilities.formatDate(date, TIME_ZONE, "yyyy-MM-dd") : String(date);
  const timeText = time instanceof Date ? Utilities.formatDate(time, TIME_ZONE, "HH:mm") : String(time);
  return Utilities.parseDate(`${dateText} ${timeText}`, TIME_ZONE, "yyyy-MM-dd HH:mm");
}

function eventKey(title, start, end) {
  return `${title}|${start.getTime()}|${end.getTime()}`;
}

function testAutoFillDateParsing() {
  const actual = Utilities.formatDate(parseDateTime("2026-09-14", "06:45"), TIME_ZONE, "yyyy-MM-dd HH:mm");
  if (actual !== "2026-09-14 06:45") throw new Error(`Parse sai ngày giờ: ${actual}`);
}

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    const expectedToken = PropertiesService.getScriptProperties().getProperty("EXPORT_TOKEN");
    if (!expectedToken || body.token !== expectedToken) return jsonResponse({ok: false, error: "Unauthorized"});
    if (!Array.isArray(body.rows) || !body.rows.length) return jsonResponse({ok: false, error: "rows không hợp lệ"});

    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(WORKSHEET_NAME);
    if (!sheet) return jsonResponse({ok: false, error: `Không tìm thấy sheet ${WORKSHEET_NAME}`});

    sheet.clearContents();
    sheet.getRange(1, 1, body.rows.length, body.rows[0].length).setValues(body.rows);
    const createdEvents = autoFill();
    return jsonResponse({ok: true, createdEvents});
  } catch (error) {
    return jsonResponse({ok: false, error: String(error)});
  }
}

function jsonResponse(body) {
  return ContentService.createTextOutput(JSON.stringify(body)).setMimeType(ContentService.MimeType.JSON);
}



function deleteAllExtraStudyEvents() {
  const CALENDAR_NAME = 'TEN_LICH_TREN_GG_CALENDAR_LUU_LICH_HOC';

  // Chỉnh khoảng thời gian cần xóa.
  const START_DATE = new Date('2026-08-01T00:00:00+07:00');
  const END_DATE   = new Date('2026-12-31T23:59:59+07:00');

  const calendars = CalendarApp.getCalendarsByName(CALENDAR_NAME);

  if (calendars.length === 0) {
    throw new Error(
      `Không tìm thấy calendar có tên: ${CALENDAR_NAME}`
    );
  }

  if (calendars.length > 1) {
    throw new Error(
      `Tìm thấy nhiều calendar cùng tên "${CALENDAR_NAME}". ` +
      'Nên sử dụng Calendar ID để tránh xóa nhầm.'
    );
  }

  const calendar = calendars[0];
  const events = calendar.getEvents(START_DATE, END_DATE);

  console.log(`Tìm thấy ${events.length} sự kiện.`);

  events.forEach(event => {
    console.log(
      `Đang xóa: ${event.getTitle()} | ${event.getStartTime()}`
    );

    event.deleteEvent();
  });

  console.log(`Đã xóa ${events.length} sự kiện.`);
}