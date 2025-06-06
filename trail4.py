import pandas as pd
import re
from rapidfuzz import fuzz

df = pd.read_csv("steam-200k.csv", header=None)                             #read csv and assign column names
df.columns = ["user_id", "game_name", "activity", "misc1", "misc2"]

def normalize_game_title(title: str) -> str:
    title = title.strip().lower()
    roman_to_arabic = {                                                          #normalizing game name
        r"\bxxx\b": "30", r"\bxxix\b": "29", r"\bxxviii\b": "28",
        r"\bxxvii\b": "27", r"\bxxvi\b": "26", r"\bxxv\b": "25",
        r"\bxxiv\b": "24", r"\bxxiii\b": "23", r"\bxxii\b": "22",
        r"\bxxi\b": "21", r"\bxx\b": "20", r"\bxix\b": "19",
        r"\bxviii\b": "18", r"\bxvii\b": "17", r"\bxvi\b": "16",
        r"\bxv\b": "15", r"\bxiv\b": "14", r"\bxiii\b": "13",
        r"\bxii\b": "12", r"\bxi\b": "11", r"\bx\b": "10",
        r"\bix\b": "9", r"\bviii\b": "8", r"\bvii\b": "7",
        r"\bvi\b": "6", r"\bv\b": "5", r"\biv\b": "4",
        r"\biii\b": "3", r"\bii\b": "2", r"\bi\b": "1"
    }
    for pattern, replacement in roman_to_arabic.items():
        title = re.sub(pattern, replacement, title)
    title = re.sub(r"([a-z])(\d+)", r"\1 \2", title)
    title = re.sub(r"(\d+)([a-z])", r"\1 \2", title)
    title = re.sub(r"[^a-z0-9 ]+", "", title)
    return re.sub(r"\s+", " ", title).strip()

def extract_base_and_version(title: str):
    match = re.search(r"^(.*?)(?:\s+(\d+))?$", title)
    if not match:
        return title, None                                          # get base and version name and no
    base = match.group(1).strip()
    version = match.group(2)
    return base, int(version) if version else None

kept_indices = []
duplicates = []

for (user_id, activity), group in df.groupby(["user_id", "activity"]):
    buckets = []
    group = group.reset_index()                                                   #create groups
    
    for _, row in group.iterrows():
        row_index = row["index"]
        original_title = row["game_name"]
        normalized_title = normalize_game_title(original_title)
        base_title, version = extract_base_and_version(normalized_title)
        matched = False
        
        for bucket in buckets:
            rep = bucket[0]
            rep_base = rep["base"]                                          #creation of buckets
            rep_version = rep["version"]
            rep_normalized = rep["normalized"]
            
            if base_title != rep_base:
                continue
            if version is not None and rep_version is not None and version != rep_version:
                continue
            
            similarity = fuzz.ratio(normalized_title, rep_normalized)
            threshold = 95
            
            if version is None and rep_version is None:
                if similarity >= threshold:
                    reason = f"Fuzzy match ≥{threshold} with base '{rep_base}' (no version conflict)"
                    duplicates.append((user_id, activity, rep["original"], original_title, similarity, reason))
                    matched = True
                    break
            else:
                if similarity == 100 and (rep_version == version or rep_version is None or version is None):
                    reason = "Exact match (100%) after numeral normalization"
                    duplicates.append((user_id, activity, rep["original"], original_title, similarity, reason))
                    matched = True
                    break
                continue
        
        if not matched:
            buckets.append([{
                "index": row_index,
                "original": original_title,
                "normalized": normalized_title,
                "base": base_title,
                "version": version
            }])
    
    for bucket in buckets:
        kept_indices.append(bucket[0]["index"])

cleaned_data = df.loc[sorted(kept_indices)].reset_index(drop=True)
duplicate_log = pd.DataFrame(duplicates, columns=[
    "user_id", "activity", "kept_title", "removed_title", "fuzzy_ratio", "reason"
])

print("Deleted titles and reasons:")
print(duplicate_log.to_string(index=False))

cleaned_data.to_csv("steam-200k-cleaned.csv", index=False)
duplicate_log.to_csv("steam-200k-deleted-report.csv", index=False)
