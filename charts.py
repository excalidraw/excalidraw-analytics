from datetime import datetime
from opencolor import oc
import json
import os


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
VERSION_DIR = os.path.join(ROOT_DIR, "version")
TEMPLATE_FILE = os.path.join(ROOT_DIR, "template.html")
INDEX_FILE = os.path.join(ROOT_DIR, "index.html")


def chart_colors(index):
    return [
        oc["grape"][index],
        oc["red"][index],
        oc["orange"][index],
        oc["yellow"][index],
        oc["lime"][index],
        oc["green"][index],
        oc["teal"][index],
        oc["cyan"][index],
        oc["blue"][index],
        oc["indigo"][index],
        oc["violet"][index],
    ]


chart_colors_bg = chart_colors(1)
chart_colors_text = chart_colors(9)
empty_color = oc["gray"][1]
usage_colors = [
    oc["lime"][0],
    oc["lime"][1],
    oc["lime"][2],
    oc["lime"][3],
    oc["lime"][5],
    oc["lime"][6],
]


def string2date(string):
    return datetime.strptime(string, "%Y-%m-%d").strftime("%d %b")


def render_cell(value, max):
    color_id = round((value / max) * (len(usage_colors) - 1))
    if value:
        return "<td style='background-color: %s'>%2.1f%%</td>" % (
            usage_colors[color_id],
            value * 100,
        )
    return "<td style='background-color: %s'>-</td>" % (empty_color)


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

    # find max_value
    max_value = 0

    for day in sorted_days:
        for version in day[1]:
            max_value = max(max_value, day[1][version])

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

    version_head = "<tr><th>Version</th><th>Commit</th><th style='background-color: {}'></th>".format(
        empty_color
    )

    for day in sorted_days:
        version_head += "<th>%s</th>" % string2date(day[0])

    version_head += "</tr>"
    version_body = ""

    current_version_date = ""
    for index, row in enumerate(report):
        version_date = row[:10]
        version_datetime = row[:16].replace("T", " ")
        version_hash = row[-7:]
        color_bg = chart_colors_bg[
            (index - len(sorted_versions)) % len(chart_colors_bg)
        ]
        color_text = chart_colors_text[
            (index - len(sorted_versions)) % len(chart_colors_text)
        ]
        if version_date != current_version_date:
            version_body += "<tr><td style='background-color: {}' colspan='{}'></td></tr>".format(
                empty_color, 3 + len(report[row])
            )
        version_body += "<tr><td style='background-color: {}; color: {};'><code>{}</code></td>".format(
            color_bg, color_text, version_datetime,
        )
        version_body += "<td style='background-color: {};'><code><a style='color: {};' href='https://github.com/excalidraw/excalidraw/commit/{}'>{}</a></code></td><td style='background-color: {}'></td>".format(
            color_bg, color_text, version_hash, version_hash, empty_color,
        )
        for day in report[row]:
            version_body += render_cell(report[row][day], max_value)
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
