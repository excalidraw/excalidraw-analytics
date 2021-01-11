from apiclient.discovery import build
from datetime import datetime
from datetime import timedelta
from oauth2client.service_account import ServiceAccountCredentials
import os
import json


SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
VIEW_ID = "208661610"

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
VERSION_DIR = os.path.join(ROOT_DIR, "version")
KEY_FILE = os.path.join(ROOT_DIR, "excalidraw-key.json")


def initialize_analyticsreporting():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, SCOPES)
    return build("analyticsreporting", "v4", credentials=credentials)


def get_version_report(analytics, day="yesterday"):
    return (
        analytics.reports()
        .batchGet(
            body={
                "reportRequests": [
                    {
                        "viewId": VIEW_ID,
                        "dateRanges": [{"startDate": day, "endDate": day}],
                        "metrics": [{"expression": "ga:totalEvents"}],
                        "dimensions": [
                            {"name": "ga:eventCategory"},
                            {"name": "ga:eventAction"},
                            {"name": "ga:eventLabel"},
                        ],
                    }
                ]
            }
        )
        .execute()
    )


def print_version_response(response, day):
    counts = {}
    for report in response.get("reports", []):
        columnHeader = report.get("columnHeader", {})
        dimensionHeaders = columnHeader.get("dimensions", [])

        for row in report.get("data", {}).get("rows", []):
            dimensions = row.get("dimensions", [])
            dateRangeValues = row.get("metrics", [])

            if "version" not in dimensions:
                continue

            found = False
            for header, dimension in zip(dimensionHeaders, dimensions):
                if header == "ga:eventLabel" and len(dimension) == 28:
                    found = True

            if not found:
                continue

            counts[dimensions[2]] = int(dateRangeValues[0]["values"][0])
            print(dimensions[2], ":", int(dateRangeValues[0]["values"][0]))

    return counts


def print_header(versions):
    print(["Date"] + [version[-7:] for version in versions], ",")


def print_rows(days, versions):
    for day in days:
        row = []
        row.append(day[0])

        for version in versions:
            if version in day[1]:
                row.append(day[1][version])
            else:
                row.append(0)
        print(row, ",")


def main():
    current_date = datetime(2021, 1, 10)
    today = datetime.today()
    while current_date < today:
        day = current_date.strftime("%Y-%m-%d")
        print()
        print(day)
        print("-" * 40)
        analytics = initialize_analyticsreporting()
        response = get_version_report(analytics, day)
        day_versions = print_version_response(response, day)
        with open(os.path.join(VERSION_DIR, day + ".json"), "w") as outfile:
            json.dump(day_versions, outfile, indent=2)

        current_date += timedelta(days=1)
        print()


if __name__ == "__main__":
    main()
