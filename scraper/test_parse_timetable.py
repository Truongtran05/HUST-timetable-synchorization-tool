from parse_timetable import parse_timetable


def test_parse_timetable() -> None:
    html = """
    <tbody><tr>
      <td>1</td><td>T2 (S)</td><td>Tiết 1-3</td><td>2-9,11-18</td>
      <td>D9-306</td><td>171206</td><td>IT3080</td><td>Mạng máy tính</td>
    </tr></tbody>
    """
    assert parse_timetable(html) == [
        {
            "course_name": "Mạng máy tính",
            "course_code": "IT3080",
            "weekday": "T2",
            "time": "Tiết 1-3",
            "weeks": [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18],
            "location": "D9-306",
        }
    ]


if __name__ == "__main__":
    test_parse_timetable()
