import os
import pandas as pd
from flask import Flask, render_template, request, send_file
from rapidfuzz import process, fuzz
import matplotlib.pyplot as plt

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
CLEANED_FILE = os.path.join(UPLOAD_FOLDER, 'steam_cleaned.csv')
PLOT_FILE = os.path.join(UPLOAD_FOLDER, 'duplicates_plot.png')

def visualize_exact_duplicates(df):
    exact_dups = df[df.duplicated()]
    dup_titles = exact_dups[1].value_counts().head(10)

    if not dup_titles.empty:
        plt.figure(figsize=(10, 5))
        dup_titles.plot(kind='barh', color='skyblue')
        plt.title("Top 10 Game Titles Among Exact Duplicates")
        plt.xlabel("Count")
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(PLOT_FILE)
        plt.close()

    return len(exact_dups), exact_dups.head().to_html(classes='table table-sm')

def preview_partial_duplicates(df, sample_size=1000, threshold=90):
    sample_df = df.sample(min(sample_size, len(df)), random_state=42)
    titles = sample_df[1].tolist()
    seen = set()
    partial_dups = []

    for title in titles:
        if title in seen:
            continue
        matches = process.extract(title, titles, scorer=fuzz.token_sort_ratio, limit=None)
        for match_title, score, _ in matches:
            if score >= threshold and title != match_title:
                partial_dups.append((title, match_title, score))
                seen.add(match_title)
                break

    return pd.DataFrame(partial_dups, columns=["Title", "Similar Title", "Score"]).head(10).to_html(classes='table table-sm')

def remove_partial_duplicates(group):
    titles = group[1].tolist()
    to_remove = set()
    for title in titles:
        if title in to_remove:
            continue
        matches = process.extract(title, titles, scorer=fuzz.token_sort_ratio, limit=None)
        for match_title, score, _ in matches:
            if score > 90 and match_title != title:
                to_remove.add(match_title)
    return group[~group[1].isin(to_remove)]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            return render_template('index.html', error='Please upload a CSV file.')

        df = pd.read_csv(file, header=None)

        exact_count, exact_sample = visualize_exact_duplicates(df)
        partial_sample = preview_partial_duplicates(df)

        df = df.drop_duplicates()
        grouped = df.groupby([0, 2])
        cleaned = [remove_partial_duplicates(group) for _, group in grouped]
        df_cleaned = pd.concat(cleaned, ignore_index=True)
        df_cleaned.to_csv(CLEANED_FILE, index=False, header=False)

        return render_template('index.html',
                               exact_count=exact_count,
                               exact_sample=exact_sample,
                               partial_sample=partial_sample,
                               plot_file=PLOT_FILE,
                               download_link=CLEANED_FILE)

    return render_template('index.html')

@app.route('/download')
def download():
    return send_file(CLEANED_FILE, as_attachment=True)

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
