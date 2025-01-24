import pandas as pd
import argparse

def generate_array_from_csv(csv_path, constructor_name, parameter_column_map, comments_map=None):
    """
    Generates an array of constructor calls from a CSV file.

    :param csv_path: Path to the input CSV file.
    :param constructor_name: Name of the constructor (e.g., GradientTheme).
    :param parameter_column_map: Dictionary mapping constructor parameters to CSV columns.
    :param comments_map: Optional dictionary mapping values (e.g., theme names) to comments.
    :return: None (prints the array of constructor calls).
    """
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # List to hold the generated constructor calls
    constructor_calls = []

    # Iterate over the rows in the CSV
    for _, row in df.iterrows():
        # Dynamically build the parameter values
        parameters = []
        for param, column in parameter_column_map.items():
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found in the CSV")
            value = row[column]

            # Format the value based on type
            if isinstance(value, str):
                # Enclose string values in quotes
                parameters.append(f'"{value}"')
            elif isinstance(value, (int, float)) and "Color" in param:
                # Format numbers (e.g., colors) as hex with 0x prefix
                parameters.append(f'{int(value):#010x}')
            elif isinstance(value, bool) or str(value).lower() in ["true", "false"]:
                # Handle boolean values
                parameters.append(str(value).lower())
            else:
                # Default case (for integers, floats, etc.)
                parameters.append(str(value))

        # Generate the constructor call
        constructor_call = f"{constructor_name}({', '.join(parameters)})"

        # # Add a comment if mapping exists
        # comment_value = comments_map.get(row[parameter_column_map["themeName"]], "")
        # if comment_value:
        #     constructor_call += f" // {comment_value}"

        # Add to the list
        constructor_calls.append(constructor_call)

    # Print the output array
    print(",\n".join(constructor_calls) + ",")

def main():
    parser = argparse.ArgumentParser(description="Generate constructor calls from a CSV file.")
    parser.add_argument("csv_path", type=str, help="Path to the input CSV file")
    parser.add_argument("constructor_name", type=str, help="Name of the constructor (e.g., GradientTheme)")
    parser.add_argument(
        "--parameter_map",
        type=str,
        required=True,
        help=(
            "Mapping of constructor parameters to CSV columns in JSON format. "
            "Example: '{\"themeName\": \"ThemeName\", \"keyTextColor\": \"KeyTextColor\"}'"
        ),
    )
    parser.add_argument(
        "--comments_map",
        type=str,
        default="{}",
        help=(
            "Optional mapping of names to comments in JSON format. "
            "Example: '{\"කොමඩු\": \"Komadu\", \"ජම්බු\": \"Jambu\"}'"
        ),
    )

    args = parser.parse_args()

    # Convert JSON strings to dictionaries
    import json
    parameter_column_map = json.loads(args.parameter_map)
    comments_map = json.loads(args.comments_map)

    # Generate the constructor calls
    generate_array_from_csv(args.csv_path, args.constructor_name, parameter_column_map, comments_map)


if __name__ == "__main__":
    main()