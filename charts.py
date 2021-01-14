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

    chart_rows = [["Day"]]
    for version in sorted_versions:
        chart_rows[len(chart_rows) - 1].append(version[-7:])

    for day in sorted_days:
        chart_rows.append([day[0]])
        for version in sorted_versions:
            if version in day[1]:
                chart_rows[len(chart_rows) - 1].append((day[1][version]))
            else:
                chart_rows[len(chart_rows) - 1].append(0)

    report = {}
    for version in sorted(sorted_versions, reverse=True):
        report[version] = {}
        for day in sorted_days:
            report[version][day[0]] = 0
            if version in day[1]:
                report[version][day[0]] = day[1][version]

    version_head = "<tr><th>Version</th>"

    for day in sorted_days:
        version_head += "<th>%s</th>" % day[0]

    version_head += "</tr>"
    version_body = ""

    for row in report:
        version_body += (
            "<tr><td><a href='https://github.com/excalidraw/excalidraw/commit/%s'>%s</a></td>"
            % (row[-7:], row)
        )
        for day in report[row]:
            version_body += "<td>%s</td>" % (report[row][day] or "-")
        version_body += "</tr>\n"

    data = data.replace("{ data }", "%r" % chart_rows)
    data = data.replace("{ version_head }", version_head)
    data = data.replace("{ version_body }", version_body)

    with open(INDEX_FILE, "w") as index:
        index.write(data)

    print("Charts updated")


if __name__ == "__main__":
    main()
