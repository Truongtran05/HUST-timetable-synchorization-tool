import re
from datetime import date, timedelta

class time_config:
    time_slots = {}

    def __init__(self):
        self.time_slots = {
            "1 S": ["06:45" , "07:30"],
            "2 S": ["07:30" , "08:15"],
            "3 S": ["08:25" , "09:10"],
            "4 S": ["09:20" , "10:05"],
            "5 S": ["10:15" , "11:00"],
            "6 S": ["11:00" , "11:45"],
            "1 C": ["12:30" , "13:15"],
            "2 C": ["13:15" , "14:00"],
            "3 C": ["14:10" , "14:55"],
            "4 C": ["15:05" , "15:50"],
            "5 C": ["16:00" , "16:45"],
            "6 C": ["16:45" , "17:30"],
        }

    def get_time_slot(self, time_str: str) -> list[str]:
        direct_time = re.fullmatch(r"(\d{2}:\d{2})-(\d{2}:\d{2}) [SCsc]", time_str)
        if direct_time:
            return list(direct_time.groups())

        period_time = re.fullmatch(r"Tiết ([1-6])-([1-6]) ([SCsc])", time_str)
        if not period_time:
            raise ValueError(f"Định dạng thời gian không hợp lệ: {time_str}")

        start_period, end_period, shift = period_time.groups()
        if int(start_period) > int(end_period):
            raise ValueError(f"Tiết bắt đầu phải trước tiết kết thúc: {time_str}")

        shift = shift.upper()
        return [
            self.time_slots[f"{start_period} {shift}"][0],
            self.time_slots[f"{end_period} {shift}"][1],
        ]

class date_config:
    def __init__(self, start_date: date):
        self.start_date = start_date

    def get_date(self, week: int, weekday: str) -> date:
        if week < 1 or weekday not in {f"T{day}" for day in range(2, 9)}:
            raise ValueError("week phải >= 1 và weekday phải từ T2 đến T8")

        return self.start_date + timedelta(weeks=week - 1, days=int(weekday[1:]) - 2)


if __name__ == "__main__":
    time_config_instance = time_config()
    assert time_config_instance.get_time_slot("Tiết 1-3 S") == ["06:45", "09:10"]
    assert time_config_instance.get_time_slot("12:30-15:00 C") == ["12:30", "15:00"]

    config = date_config(date(2026, 9, 7))
    assert config.get_date(1, "T2") == date(2026, 9, 7)
    assert config.get_date(2, "T8") == date(2026, 9, 20)
