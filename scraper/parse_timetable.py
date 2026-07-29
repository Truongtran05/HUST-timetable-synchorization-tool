import json
import re
from html.parser import HTMLParser
from pathlib import Path


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows = []
        self._in_body = False
        self._row = None
        self._cell = None
        self._skip_row = False

    def handle_starttag(self, tag, attrs) -> None:
        attributes = dict(attrs)
        if tag == "tbody":
            self._in_body = True
        elif self._in_body and tag == "tr":
            self._row = []
            self._skip_row = attributes.get("aria-hidden") == "true"
        elif self._row is not None and tag == "td":
            self._cell = []
        elif self._cell is not None and tag == "br":
            self._cell.append("\n")

    def handle_endtag(self, tag) -> None:
        if self._cell is not None and tag in {"div", "p"}:
            self._cell.append("\n")
        elif tag == "td" and self._cell is not None:
            text = "".join(self._cell).replace("\xa0", " ")
            lines = [" ".join(line.split()) for line in text.splitlines()]
            self._row.append("\n".join(line for line in lines if line))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if not self._skip_row:
                self.rows.append(self._row)
            self._row = None
        elif tag == "tbody":
            self._in_body = False

    def handle_data(self, data) -> None:
        if self._cell is not None:
            self._cell.append(data)


def _expand_weeks(value: str) -> list[int]:
    weeks = []
    for start, end in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", value):
        first = int(start)
        weeks.extend(range(first, int(end) + 1) if end else [first])
    return weeks


def _lines(value: str) -> list[str]:
    return [line for line in value.splitlines() if line] or [""]


def parse_timetable(html: str) -> list[dict]:
    parser = _TableParser()
    parser.feed(html)
    timetable = []

    for cells in parser.rows:
        if len(cells) < 8 or not cells[6] or not cells[7]:
            continue

        weekdays = re.findall(r"T[2-8]", cells[1])
        shift = re.findall(r"[SCsc]", cells[1])
        times = _lines(cells[2])
        weeks = _lines(cells[3])
        locations = _lines(cells[4])
        session_count = max(len(weekdays), len(times), len(weeks), len(locations))

        def value_at(values, index):
            return values[index] if index < len(values) else values[-1]

        for index in range(session_count):
            timetable.append(
                {
                    "course_name": " ".join(cells[7].split()),
                    "course_code": " ".join(cells[6].split()),
                    "weekday": value_at(weekdays, index),
                    "time": " ".join([value_at(times, index), value_at(shift, index)]),
                    "weeks": _expand_weeks(value_at(weeks, index)),
                    "location": value_at(locations, index),
                }
            )

    return timetable


def write_timetable_json(html: str, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(parse_timetable(html), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    write_timetable_json(
        Path("timetable.html").read_text(encoding="utf-8"),
        Path("store/timetable.json"),
    )
