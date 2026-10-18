"""Kok-Tobe Lift: строит отчёт out/report.json из файла data/records.csv."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "records.csv"
OUT = ROOT / "out" / "report.json"
VARIANT = 14


def load_rows():
    with open(DATA, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def control_code(rows):
    text = "\n".join("|".join(row.values()) for row in rows)
    digest = hashlib.sha256(f"{VARIANT}\n{text}".encode("utf-8"))
    return digest.hexdigest()[:8].upper()


def money(value):
    return f"{value:,}".replace(",", " ") + " ₸"


def build(rows):
    by_hour = defaultdict(lambda: [0, 0])
    by_dir = defaultdict(lambda: [0, 0])
    by_day = defaultdict(lambda: [0, 0])
    for r in rows:
        p, a = int(r["passengers"]), int(r["amount"])
        h = by_hour[int(r["hour"])]
        h[0] += p
        h[1] += a
        d = by_dir[r["direction"]]
        d[0] += p
        d[1] += a
        day = by_day[r["date"]]
        day[0] += p
        day[1] += a
    revenue = sum(int(r["amount"]) for r in rows)
    people = sum(int(r["passengers"]) for r in rows)
    summary = [
        {"label": "Общая выручка", "value": money(revenue)},
        {"label": "Пассажиры", "value": people},
        {"label": "Чеков", "value": len(rows)},
    ]
    hours = sorted(by_hour.items(), key=lambda kv: (-kv[1][0], kv[0]))
    dirs = sorted(by_dir.items(), key=lambda kv: -kv[1][1])
    days = sorted(by_day.items())
    tables = [
        {"title": "Пассажиры по часам (два дня)",
         "columns": ["Час", "Пассажиров", "Выручка"],
         "rows": [[f"{k:02d}:00", v[0], money(v[1])] for k, v in hours]},
        {"title": "Выручка по направлениям",
         "columns": ["Направление", "Пассажиров", "Выручка"],
         "rows": [[k, v[0], money(v[1])] for k, v in dirs]},
        {"title": "Выручка по дням",
         "columns": ["Дата", "Пассажиров", "Выручка"],
         "rows": [[k, v[0], money(v[1])] for k, v in days]},
    ]
    return summary, tables


def main():
    rows = load_rows()
    summary, tables = build(rows)
    report = {
        "variant": VARIANT,
        "org": "Kok-Tobe Lift",
        "title": "Продажа билетов на канатную дорогу Кок-Тобе",
        "records": len(rows),
        "control_code": control_code(rows),
        "summary": summary,
        "tables": tables,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"out/report.json готов: {len(rows)} записей, контрольный код {report['control_code']}")


if __name__ == "__main__":
    main()
