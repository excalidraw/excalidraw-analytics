import json
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
VERSION_DIR = os.path.join(ROOT_DIR, "version")
TEMPLATE_FILE = os.path.join(ROOT_DIR, "template.html")
INDEX_FILE = os.path.join(ROOT_DIR, "index.html")


def main():
    with open(TEMPLATE_FILE, "r") as template:
        data = template.read()

    _, _, filenames = next(os.walk(VERSION_DIR))

    days = {}
    versions = set()

    for filename in filenames:
        with open(os.path.join(VERSION_DIR, filename), "r") as day_json:
            day = json.load(day_json)
        days[filename.replace(".json", "")] = day
        for key in day.keys():
            versions.add(key)

    sorted_days = sorted(days.items())
    sorted_versions = sorted(versions)

    rows = [["Day"]]
    for version in sorted_versions:
        rows[len(rows) - 1].append(version[-7:])

    for day in sorted_days:
        rows.append([day[0]])
        for version in sorted_versions:
            if version in day[1]:
                rows[len(rows) - 1].append((day[1][version]))
            else:
                rows[len(rows) - 1].append(0)

    data = data.replace("{ data }", "%r" % rows)

    with open(INDEX_FILE, "w") as index:
        index.write(data)

    print("Charts updated")


if __name__ == "__main__":
    main()
