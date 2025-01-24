# Figma Automation - Keyboard Themes

## Setup

1. Create a virtual environment:

   ```sh
   python -m venv .venv
   ```

2. Activate the virtual environment:

   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the root directory and add the following environment variables:
   ```env
   FIGMA_API_TOKEN=your_figma_api_token
   FIGMA_FILE_KEY=your_figma_file_key
   FIGMA_NODE_IDS=your_figma_node_ids
   ```

## Usage

1. Run the Fetch Figma script:

   ```sh
   python fetch_figma.py
   ```

2. Run the Separator script:
   ```sh
   python separator.py
   ```

This will generate a separated `.csv` file.

## Customization

To modify the keys, edit the main method in the `separator.py` file.
