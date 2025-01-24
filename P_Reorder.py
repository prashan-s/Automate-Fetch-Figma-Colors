import pandas as pd

class CSVHandler:
    def __init__(self, old_csv_path, new_csv_path):
        # Read old and new CSVs
        self.old_csv = pd.read_csv(old_csv_path)
        self.new_csv = pd.read_csv(new_csv_path)
    
    def copy_column(self, column_name, target_column_name=None):
        """
        Copies a column from the old CSV to the new CSV.
        Optionally, rename the column in the new CSV.
        """
        if column_name not in self.old_csv.columns:
            raise ValueError(f"Column '{column_name}' not found in old CSV")
        
        # Use the target column name or keep the same name
        target_column_name = target_column_name or column_name
        self.new_csv[target_column_name] = self.old_csv[column_name]
    
    def reorder_columns(self, column_order):
        """
        Reorders the columns in the new CSV based on the provided column order.
        Any missing columns will be ignored, and additional columns will be appended at the end.
        """
        current_columns = self.new_csv.columns.tolist()
        new_order = [col for col in column_order if col in current_columns]
        remaining_columns = [col for col in current_columns if col not in new_order]
        self.new_csv = self.new_csv[new_order + remaining_columns]
    
    def to_array(self):
        """
        Converts the final DataFrame into an array of dictionaries.
        """
        return self.new_csv.to_dict(orient='records')
    
    def save_to_csv(self, output_path):
        """
        Saves the final DataFrame to a CSV file.
        """
        self.new_csv.to_csv(output_path, index=False)

# Usage Example
old_csv_path = "P/BorderThemeGradient.csv"
new_csv_path = "P/BorderThemeGradient.csv"
output_csv_path = "./F/F-BorderThemeGradient.csv"

# Initialize the handler
handler = CSVHandler(old_csv_path, new_csv_path)

# Copy a column from the old CSV to the new CSV
# handler.copy_column(column_name="KeyBoarderEnabled", target_column_name="KeyBoarderEnabled")

# Reorder columns in the new CSV
handler.reorder_columns(["ThemeName","KeyTextColor","PredictionBarStartColor","KeyBackgroundColor","KeyboardBackground","KeyBorderStartColor","KeyBorderEndColor"])

# Generate the array from the new CSV
#data_array = handler.to_array()
#//print(data_array)

# Save the updated CSV
handler.save_to_csv(output_csv_path)