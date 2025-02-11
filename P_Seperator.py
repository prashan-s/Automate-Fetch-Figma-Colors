import json
import csv
from typing import Dict, List, Tuple, Optional
import os


def color_to_hex(color: Dict[str, float]) -> str:
    """Convert RGBA color to 0xAARRGGBB format."""
    r = round(color.get("r", 0) * 255)
    g = round(color.get("g", 0) * 255)
    b = round(color.get("b", 0) * 255)
    a = round(color.get("a", 1) * 255)
    return f"0x{a:02X}{r:02X}{g:02X}{b:02X}"


def process_fills(fills: List[Dict]) -> Tuple[Optional[str], Optional[Tuple[str, str]]]:
    """Process fill colors to extract solid or gradient colors."""
    for fill in fills:
        if fill['type'] == "SOLID":
            color = fill['color']
            return color_to_hex(color), None
        elif fill['type'] in ["GRADIENT_LINEAR", "GRADIENT_RADIAL"]:
            gradient_stops = fill.get("gradientStops", [])
            if len(gradient_stops) >= 2:
                start_color = color_to_hex(gradient_stops[0]["color"])
                end_color = color_to_hex(gradient_stops[-1]["color"])
                return None, (start_color, end_color)
    return None, None


class ThemeExtractor:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.nodes = self._load_json()

    def _load_json(self) -> Dict:
        """Load the JSON data from the file."""
        with open(self.json_path, 'r') as file:
            data = json.load(file)
        return data.get("nodes", {})

    def extract_themes(self, prefix: str) -> Dict[str, Dict[str, Dict]]:
        """Extract themes based on a given prefix."""
        themes = {}

        def parse_frame_name(frame_name: str) -> Optional[Tuple[str, str, Optional[str]]]:
            """Extract theme number and key type from frame name."""
            localized_name = None
            
            if "-" in frame_name:
                frame_name, localized_name = frame_name.split("-", 1)

            if frame_name.startswith(prefix):
                parts = frame_name.split("_", 2)
                if len(parts) >= 2:
                    theme_number = parts[1]
                    key_type = parts[2] if len(parts) > 2 else None
                    return theme_number, key_type, localized_name
            return None
        
        def traverse_children(children):
            for child in children:
                frame_name = child.get("name", "")
                parsed = parse_frame_name(frame_name)
                if parsed:
                    theme_number, key_type, localized_name = parsed
                    print("key_type",key_type)
                    fills = child.get("fills", [])
                    strokes = child.get("strokes", [])
                    solid_color, gradient_colors = process_fills(fills)
                    stroke_solid_color, stroke_gradient_colors = process_fills(strokes)
                    if theme_number not in themes:
                        themes[theme_number] = {}
                    themes[theme_number][key_type] = {
                        "localized_name": localized_name,
                        "solid_color": solid_color,
                        "gradient_colors": gradient_colors,
                        "s_solid_color": stroke_solid_color,
                        "s_gradient_colors": stroke_gradient_colors
                    }
                if "children" in child:
                    traverse_children(child["children"])

        for node_id, node_info in self.nodes.items():
            document = node_info.get("document", {})
            if "children" in document:
                traverse_children(document["children"])

        return themes


class CSVWriter:
    @staticmethod
    def write_csv(file_name: str, headers: List[str], data: List[Dict]):
        """Write data to a CSV file."""
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        sorted_data = sorted(data, key=lambda x: x["ID"])
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(sorted_data)

    @staticmethod
    def prepare_color_theme(themes: Dict[str, Dict]) -> List[Dict]:
        """Prepare data for ColorTheme.csv."""
        rows = []
        for theme_number, keys in themes.items():
            rows.append({
                "ID": f"KBC_{theme_number}",
                "ThemeName": keys.get(None, {}).get("localized_name") or  f"KBC_{theme_number}",
                "KeyTextColor": keys.get("KYT", {}).get("solid_color"),
                "PredictionBarColor": keys.get("PR", {}).get("solid_color"),
                "KeyBackgroundColor": keys.get("KYBG", {}).get("solid_color"),
                "KeyboardBackgroundColor": keys.get(None, {}).get("solid_color")
            })
        return rows

    @staticmethod
    def prepare_gradient_theme(themes: Dict[str, Dict]) -> List[Dict]:
        """Prepare data for GradientTheme.csv."""
        rows = []
        for theme_number, keys in themes.items():
            background = keys.get(None, {}).get("gradient_colors", (None, None))
            #prediction_bar = keys.get("PR", {}).get("gradient_colors", (None, None))
            rows.append({
                "ID": f"KBG_{theme_number}",
                "ThemeName": keys.get(None, {}).get("localized_name") or  f"KBG_{theme_number}",
                "KeyTextColor": keys.get("KYT", {}).get("solid_color"),
                "KeyBackgroundColor": keys.get("KYBG", {}).get("solid_color"),
                "KeyboardBackgroundStartColor": background[1],
                "KeyboardBackgroundEndColor": background[0],
                "PredictionBarStartColor": keys.get("PR", {}).get("solid_color"),
                "PredictionBarEndColor": keys.get("PR", {}).get("solid_color")
            })
        return rows

    @staticmethod
    def prepare_radial_theme(themes: Dict[str, Dict]) -> List[Dict]:
        """Prepare data for RadialTheme.csv."""
        rows = []
        for theme_number, keys in themes.items():
            background = keys.get(None, {}).get("gradient_colors", (None, None))
            #prediction_bar = keys.get("PR", {}).get("gradient_colors", (None, None))
            rows.append({
                "ID": f"KBR_{theme_number}",
                "ThemeName": keys.get(None, {}).get("localized_name") or  f"KBR_{theme_number}",
                "KeyTextColor": keys.get("KYT", {}).get("solid_color"),
                "KeyBackgroundColor": keys.get("KYBG", {}).get("solid_color"),
                "KeyboardBackgroundStartColor": background[0],
                "KeyboardBackgroundEndColor": background[1],
                "PredictionBarStartColor": keys.get("PR", {}).get("solid_color"),
                "PredictionBarEndColor": keys.get("PR", {}).get("solid_color")
            })
        return rows

    @staticmethod
    def prepare_border_theme_gradient(themes: Dict[str, Dict]) -> List[Dict]:
        """Prepare data for BorderTheme.csv."""
        rows = []
        for theme_number, keys in themes.items():
            key_stroke = keys.get("KYBG", {}).get("s_gradient_colors", (None, None))
            if not key_stroke:
                key_stroke = (f"0xFFFFFF", f"0xFFFFFF")
            print("key_stroke", key_stroke)
            rows.append({
                "ID": f"KBB_{theme_number}",
                "ThemeName": keys.get(None, {}).get("localized_name") or  f"KBB_{theme_number}",
                "KeyTextColor": keys.get("KYT", {}).get("solid_color"),
                "KeyBackgroundColor": keys.get("KYBG", {}).get("solid_color"),
                "KeyboardBackground": keys.get(None, {}).get("solid_color"),
                "KeyBorderStartColor": key_stroke[0],
                "KeyBorderEndColor": key_stroke[1],
                "PredictionBarStartColor": keys.get("PR", {}).get("solid_color"),
                "PredictionBarEndColor": keys.get("PR", {}).get("solid_color")
            })
        return rows

    @staticmethod
    def prepare_border_theme_solid(themes: Dict[str, Dict]) -> List[Dict]:
        """Prepare data for BorderTheme.csv."""
        rows = []
        for theme_number, keys in themes.items():
            rows.append({
                "ID": f"KBB_{theme_number}",
                "ThemeName": keys.get(None, {}).get("localized_name") or  f"KBB_{theme_number}",
                "KeyTextColor": keys.get("KYT", {}).get("solid_color"),
                "KeyBackgroundColor": keys.get("KYBG", {}).get("solid_color"),
                "KeyboardBackground": keys.get(None, {}).get("solid_color"),
                "KeyBorderStartColor": keys.get("KYBG", {}).get("s_solid_color"),
                "KeyBorderEndColor": keys.get("KYBG", {}).get("s_solid_color"),
                "PredictionBarStartColor": keys.get("PR", {}).get("solid_color"),
                "PredictionBarEndColor": keys.get("PR", {}).get("solid_color")
            })
        return rows

def main():
    json_file = "figma_colors.json"
    extractor = ThemeExtractor(json_file)

    # Extract themes based on prefixes
    color_themes = extractor.extract_themes("KBC")
    gradient_themes = extractor.extract_themes("KBG")
    radial_themes = extractor.extract_themes("KBR")
    border_themes_gradient = extractor.extract_themes("KBB")
    border_themes_solid = extractor.extract_themes("KBSB")

    # Write CSV files
    CSVWriter.write_csv("./Output/ColorTheme.csv",
                        ["ID", "ThemeName", "KeyTextColor", "PredictionBarColor", "KeyBackgroundColor", "KeyboardBackgroundColor"],
                        CSVWriter.prepare_color_theme(color_themes))

    CSVWriter.write_csv("./Output/GradientTheme.csv",
                        ["ID", "ThemeName", "KeyTextColor", "KeyBackgroundColor", "KeyboardBackgroundStartColor", "KeyboardBackgroundEndColor", "PredictionBarStartColor", "PredictionBarEndColor"],
                        CSVWriter.prepare_gradient_theme(gradient_themes))

    CSVWriter.write_csv("./Output/RadialTheme.csv",
                        ["ID", "ThemeName", "KeyTextColor", "KeyBackgroundColor", "KeyboardBackgroundStartColor", "KeyboardBackgroundEndColor", "PredictionBarStartColor", "PredictionBarEndColor"],
                        CSVWriter.prepare_radial_theme(radial_themes))

    CSVWriter.write_csv("./Output/BorderThemeGradient.csv",
                        ["ID", "ThemeName", "KeyTextColor", "KeyBackgroundColor", "KeyboardBackground", "KeyBorderStartColor", "KeyBorderEndColor","PredictionBarStartColor","PredictionBarEndColor"],
                        CSVWriter.prepare_border_theme_gradient(border_themes_gradient))

    CSVWriter.write_csv("./Output/BorderThemeSolid.csv",
                        ["ID", "ThemeName", "KeyTextColor", "KeyBackgroundColor", "KeyboardBackground", "KeyBorderStartColor", "KeyBorderEndColor","PredictionBarStartColor","PredictionBarEndColor"],
                        CSVWriter.prepare_border_theme_solid(border_themes_solid))

    print("CSV files have been created successfully in the './Output/' directory.")


if __name__ == "__main__":
    main()
