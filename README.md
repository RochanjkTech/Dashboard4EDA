===================================================
Steam Dataset Duplicate Cleaner - Flask Web App
===================================================

This Flask web application visualizes and cleans duplicates 
from the Steam dataset (steam-200k.csv). It performs both 
exact and fuzzy duplicate detection and allows downloading 
a cleaned version of the dataset.

-------------------------
🔧 FEATURES
-------------------------

- Loads a pre-defined dataset: steam-200k.csv
- Detects and displays:
  - Number of exact duplicate rows
  - Top 10 most duplicated game titles
  - Sample of fuzzy/partial duplicates using RapidFuzz
- Generates a bar chart of duplicate game titles
- Cleans both exact and fuzzy duplicates
- Allows downloading the cleaned dataset
- Simple, responsive UI using Bootstrap

-------------------------
📁 PROJECT STRUCTURE
-------------------------

steam-cleaner-app/
├── app.py                   → Flask backend
├── steam-200k.csv           → Original dataset (input)
├── static/
│   ├── steam_cleaned.csv    → Output cleaned CSV
│   └── duplicates_plot.png  → Bar chart image
├── templates/
│   └── index.html           → HTML interface
├── deduplicator.py (optional) → Helper module if logic is separated
└── README.txt               → This file

-------------------------
⚙️ REQUIREMENTS
-------------------------

- Python 3.x
- Flask
- pandas
- matplotlib
- seaborn
- rapidfuzz

Install dependencies with:

pip install flask pandas matplotlib seaborn rapidfuzz

-------------------------
▶️ HOW TO RUN
-------------------------

1. Make sure steam-200k.csv is present in the root directory.
2. Run the Flask app:

   python app.py

3. Open your browser and navigate to:

   http://127.0.0.1:5000

4. View the results and click to download the cleaned dataset.

-------------------------
📝 NOTES
-------------------------

- No file upload is needed; the dataset is preloaded.
- Cleaning is based on both exact matching and fuzzy logic (token_sort_ratio > 90).
- The bar chart visualizes the most frequent duplicate titles.

-------------------------
📬 CONTACT
-------------------------

Developed for learning purposes and data cleaning demonstration.

