import pandas as pd
from rapidfuzz import process, fuzz   #importing packages
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv('steam-200k.csv', header=None)


exact_dups = df[df.duplicated()]
print(f" Exact duplicate rows: {len(exact_dups)}")
if not exact_dups.empty:
    print("\nSample exact duplicates:\n", exact_dups.head())


dup_titles = exact_dups[1].value_counts().head(10)                           # visualize  exact duplicates
plt.figure(figsize=(10, 5))
sns.barplot(x=dup_titles.values, y=dup_titles.index, palette="viridis")
plt.title("Top 10 Game Titles Among Exact Duplicates")
plt.xlabel("Count")
plt.tight_layout()
plt.show()


def preview_partial_duplicates(df, sample_size=1000, threshold=90):
    sample_df = df.sample(min(sample_size, len(df)), random_state=42)
    titles = sample_df[1].tolist()
    seen = set()
    partial_dups = []
                                                                                       ## visulaize partial duplicates
    for title in titles:
        if title in seen:
            continue
        matches = process.extract(title, titles, scorer=fuzz.token_sort_ratio, limit=None)
        for match_title, score, _ in matches:
            if score >= threshold and title != match_title:
                partial_dups.append((title, match_title, score))
                seen.add(match_title)
                break

    return pd.DataFrame(partial_dups, columns=["Title", "Similar Title", "Score"])

partial_preview = preview_partial_duplicates(df)
print(f"\n Sample partial duplicates (fuzzy matches, score >= 90): {len(partial_preview)}")
print(partial_preview.head(10))


df = df.drop_duplicates()                         # remove duplicates


def remove_partial_duplicates(group):
    titles = group[1].tolist()
    to_remove = set()
    for title in titles:
        if title in to_remove:
            continue
        matches = process.extract(title, titles, scorer=fuzz.token_sort_ratio, limit=None)     #remove partial duplicates
        for match_title, score, _ in matches:
            if score > 90 and match_title != title:
                to_remove.add(match_title)
    return group[~group[1].isin(to_remove)]


grouped = df.groupby([0, 2]) 
cleaned = [remove_partial_duplicates(group) for _, group in grouped]
df_cleaned = pd.concat(cleaned, ignore_index=True)

df_cleaned.to_csv('steam_cleaned.csv', index=False, header=False)
