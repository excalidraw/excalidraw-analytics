from datetime import datetime
from opencolor import oc
import json
import os


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
VERSION_DIR = os.path.join(ROOT_DIR, "version")
TEMPLATE_FILE = os.path.join(ROOT_DIR, "template.html")
INDEX_FILE = os.path.join(ROOT_DIR, "index.html")


colors = [
    oc["lime"][0],
    oc["lime"][1],
    oc["lime"][2],
    oc["lime"][3],
    oc["lime"][4],
    oc["lime"][5],
]


def string2date(string):
    return datetime.strptime(string, "%Y-%m-%d").strftime("%d %b")


def renderCell(value, max):
    color_id = round((value / max) * (len(colors) - 1))
    if value:
        return "<td style='background-color: %s'>%2.1f%%</td>" % (
            colors[color_id],
            value * 100,
        )
    return "<td style='background-color: %s'>-</td>" % (oc["gray"][0])


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

    # find maxValue
    maxValue = 0

    for day in sorted_days:
        for version in day[1]:
            maxValue = max(maxValue, day[1][version])

    chart_rows = [["Day"]]
    for version in sorted_versions:
        chart_rows[len(chart_rows) - 1].append(version[-7:])

    for day in sorted_days:
        chart_rows.append([string2date(day[0])])
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
        version_head += "<th>%s</th>" % string2date(day[0])

    version_head += "</tr>"
    version_body = ""

    current_version_date = ''
    for row in report:
        version_date = row[:10]
        if version_date != current_version_date:
            version_body += "<tr><td style='background-color: {}' colspan='{}'></td></tr>".format(oc["gray"][0], 1 + len(report[row]))

        version_body += (
            "<tr><td><code>%s [<a href='https://github.com/excalidraw/excalidraw/commit/%s'>%s</a>]</code></td>"
            % (row[:16].replace("T", " "), row[-7:], row[-7:])
        )
        for day in report[row]:
            version_body += renderCell(report[row][day], maxValue)
        version_body += "</tr>\n"
        current_version_date = version_date

    data = data.replace("{ data }", "%r" % chart_rows)
    data = data.replace("{ version_head }", version_head)
    data = data.replace("{ version_body }", version_body)

    with open(INDEX_FILE, "w") as index:
        index.write(data)

    print("Charts updated")


if __name__ == "__main__":
    main()
