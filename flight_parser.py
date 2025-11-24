import argparse
import csv
import json
from datetime import datetime
import os


def validate_flight(row):
    errors = []
    required = ["flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "price"]

    for f in required:
        if not row.get(f):
            errors.append(f"missing {f}")

    if errors:
        return False, "; ".join(errors)

    fid = row["flight_id"].strip()
    if not (2 <= len(fid) <= 8 and fid.isalnum()):
        errors.append("invalid flight_id")

    for f in ["origin", "destination"]:
        code = row[f].strip()
        if not (len(code) == 3 and code.isalpha() and code.isupper()):
            errors.append(f"invalid {f}")

    def parse_date(key):
        try:
            return datetime.strptime(row[key].strip(), "%Y-%m-%d %H:%M")
        except:
            errors.append(f"invalid {key}")
            return None

    dep = parse_date("departure_datetime")
    arr = parse_date("arrival_datetime")

    if dep and arr and arr <= dep:
        errors.append("arrival <= departure")

    try:
        if float(row["price"]) <= 0:
            errors.append("price <= 0")
    except:
        errors.append("invalid price")

    if errors:
        return False, "; ".join(errors)
    return True, ""


def process_csv(path):
    valid = []
    errors = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        line_no = 2
        for row in reader:
            ok, reason = validate_flight(row)
            if ok:
                row["price"] = float(row["price"])
                valid.append(row)
            else:
                errors.append(f"{path} - line {line_no}: {reason}")
            line_no += 1

    return valid, errors


def filter_flights(all_flights, query):
    matches = []
    for f in all_flights:
        ok = True
        for key, val in query.items():
            if key == "price":
                if float(f["price"]) > float(val):
                    ok = False
                    break
            else:
                if f.get(key) != val:
                    ok = False
                    break
        if ok:
            matches.append(f)
    return matches


def response_filename():
    sid = "231ADB260"
    name = "Ahmet_Can"
    lastname = "Karayoluk"
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    return f"response_{sid}_{name}_{lastname}_{ts}.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="single CSV file")
    parser.add_argument("-o", default="db.json")
    parser.add_argument("-q", help="JSON queries file")
    args = parser.parse_args()

    all_flights = []

    if args.i:
        valid, errors = process_csv(args.i)
        all_flights.extend(valid)

        with open(args.o, "w", encoding="utf-8") as f:
            json.dump(all_flights, f, indent=4)

        with open("errors.txt", "w", encoding="utf-8") as f:
            for e in errors:
                f.write(e + "\n")

        print(f"Valid: {len(valid)}, Invalid: {len(errors)}")
        print("Written to db.json & errors.txt")

    if args.q:
        if not all_flights:
            if os.path.exists(args.o):
                with open(args.o, encoding="utf-8") as f:
                    all_flights = json.load(f)

        with open(args.q, encoding="utf-8") as f:
            queries = json.load(f)

        results = []
        for q in queries:
            results.append({"query": q, "matches": filter_flights(all_flights, q)})

        name = response_filename()
        with open(name, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        print(f"Saved query results to {name}")


if __name__ == "__main__":
    main()
