import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv("FIGMA_API_TOKEN")
FILE_KEY = os.getenv("FIGMA_FILE_KEY")
NODE_IDS = os.getenv("FIGMA_NODE_IDS")

URL = f"https://api.figma.com/v1/files/{FILE_KEY}/nodes?ids={NODE_IDS}"

# Set the headers
HEADERS = {
    "X-FIGMA-TOKEN": API_TOKEN
}

def fetch_node_data():
    """Fetch specific node data from Figma API."""
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

def extract_node_colors(node_data):
    """Extract colors from node data and save to a JSON file."""
    nodes = node_data.get("nodes", {})
    output = []

    for node_id, node_info in nodes.items():
        document = node_info.get("document", {})
        fills = document.get("fills", [])
        frame_name = document.get("name", "Unnamed Frame")
        for fill in fills:
            if fill["type"] == "SOLID":
                color = fill["color"]
                r, g, b = color["r"] * 255, color["g"] * 255, color["b"] * 255
                opacity = fill.get("opacity", 1)
                rgba = f"rgba({int(r)}, {int(g)}, {int(b)}, {opacity})"
                output.append({"frame": frame_name, "color": rgba})

    # Write output to JSON file
    with open("figma_colors.json", "w") as json_file:
        json.dump(node_data, json_file, indent=4)
    print("Data has been written to figma_colors.json")

def main():
    try:
        node_data = fetch_node_data()
        extract_node_colors(node_data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
