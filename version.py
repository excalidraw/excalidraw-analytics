from apiclient.discovery import build
from datetime import datetime
from datetime import timedelta
from oauth2client.service_account import ServiceAccountCredentials
import os
import json


SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
VIEW_ID = "208661610"

THRESSHOLD = 10

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
        column_header = report.get("columnHeader", {})
        dimension_headers = column_header.get("dimensions", [])

        for row in report.get("data", {}).get("rows", []):
            dimensions = row.get("dimensions", [])
            metrics = row.get("metrics", [])
            if ("version" not in dimensions) and ("size" not in dimensions):
                continue

            version = ""
            for header, dimension in zip(dimension_headers, dimensions):
                if header == "ga:eventLabel" and len(dimension) == 28:
                    version = dimensions[2]
                elif header == "ga:eventLabel" and dimension == "size":
                    version = "2021-01-10T00:00:00Z"

            if not version:
                continue

            hits = int(metrics[0]["values"][0])

            if hits < THRESSHOLD:
                continue

            counts[version] = hits
            print(version, ":", hits)

    return counts


def main():
    if not os.path.exists(KEY_FILE):
        print("Key file not found", KEY_FILE)
        return

    today = datetime.today()

    current_date = today + timedelta(days=-1)
    # Set current date to 2021-01-11 to count all visits from the beginning:
    # current_date = datetime(2021, 1, 11)

    analytics = initialize_analyticsreporting()
    while current_date <= today:
        day = current_date.strftime("%Y-%m-%d")
        print()
        print(day)
        print("-" * 40)
        response = get_version_report(analytics, day)
        day_versions = print_version_response(response, day)

        # noramalize days
        total_in_day = 0
        for versions in day_versions:
            total_in_day += day_versions[versions]

        for versions in day_versions:
            if total_in_day > 0:
                day_versions[versions] = (
                    round(day_versions[versions] / total_in_day * 10000) / 10000
                )

        if day_versions:
            with open(os.path.join(VERSION_DIR, day + ".json"), "w") as outfile:
                json.dump(day_versions, outfile, indent=2, sort_keys=True)

        current_date += timedelta(days=1)
        print()


if __name__ == "__main__":
    main()
