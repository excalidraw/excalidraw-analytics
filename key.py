import json
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FILE = os.path.join(ROOT_DIR, "excalidraw.json")
KEY_FILE = os.path.join(ROOT_DIR, "excalidraw-key.json")


def main():
    if (
        not os.path.exists(KEY_FILE)
        and os.environ.get("ANALYTICS_PRIVATE_KEY")
        and os.environ.get("ANALYTICS_PRIVATE_KEY_ID")
    ):
        with open(TEMPLATE_FILE, "r") as template:
            data = json.load(template)

        data["private_key"] = os.environ.get("ANALYTICS_PRIVATE_KEY")
        data["private_key_id"] = os.environ.get("ANALYTICS_PRIVATE_KEY_ID")

        with open(KEY_FILE, "w") as key:
            json.dump(data, key, indent=2)


if __name__ == "__main__":
    main()
