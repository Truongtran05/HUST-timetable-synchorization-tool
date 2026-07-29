import json
from config.time_config import time_config, date_config

def main():
    timetable = []
    standalize_table = []
    time_config_instance = time_config()
    date_config_instance = date_config()
    with open("store/timetable.json", "r", encoding="utf-8") as f:
        timetable = json.load(f)
    for item in timetable:
        for week in item["weeks"]:
            date = date_config_instance.get_date(week, item["weekday"])
            time_slot = time_config_instance.get_time_slot(item["time"])
            standalize_table.append({
                "date": str(date),
                "start_time": time_slot[0],
                "end_time": time_slot[1],
                "course_name": item["course_name"],
                "course_code": item["course_code"],
                "location": item["location"]
            })

    with open("store/standalize_table.json", "w", encoding="utf-8") as f:
        json.dump(standalize_table, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
