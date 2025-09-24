import pandas as pd, re, unicodedata, html
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--file", type=str, help="Path to data file")
args = arg_parser.parse_args()

src = f"./resources/{args.file}"
df = None
last_err = None
for enc in ["utf-8", "utf-8-sig", "latin-1"]:
    try:
        df = pd.read_csv(src, encoding=enc)
        break
    except Exception as e:
        last_err = e
if df is None:
    raise last_err

cols = list(df.columns)
texts = cols[1]

# ---------- Define cleaning function (stdlib only) ----------
# Compile reusable regex patterns
TAG = re.compile(r"<[^>]+>")                              # HTML tags
MD_CODE_BLOCKS = re.compile(r"```.*?```", re.DOTALL)      # fenced code ```...```
MD_INLINE_CODE = re.compile(r"`[^`]*`")                   # `inline`
MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")            # ![alt](url)
MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")            # [text](url)
URLS = re.compile(r"https?://\S+")                        # naked URLs
HEADINGS = re.compile(r"^\s{0,3}#{1,6}\s*", re.MULTILINE) # # H1..H6
BLOCKQUOTES = re.compile(r"^\s{0,3}>\s?", re.MULTILINE)   # > quote
HRULES = re.compile(r"^\s*(-{3,}|_{3,}|\*{3,})\s*$", re.MULTILINE)
LIST_BULLETS = re.compile(r"^\s*([-*+]\s+|\d+\.\s+)", re.MULTILINE)
ZERO_WIDTH = re.compile(r"[\u200B-\u200D\uFEFF]")
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B-\x1F\x7F]")   # allow \t,\n,\r
NBSP = re.compile(r"\u00A0")                              # non-breaking space
TRIM_AROUND_NEWLINE = re.compile(r"[ \t]*\n[ \t]*")       # trim spaces around \n
MULTISPACE = re.compile(r"[ \t]{2,}")                     # multi spaces/tabs
MULTINEWLINE = re.compile(r"\n{3,}")                      # >2 newlines

def clean_text(text: str, keep_newlines: bool = False) -> str:
    """Remove HTML/Markdown, normalize Unicode, and tidy whitespace."""
    if text is None:
        return ""
    t = str(text)

    # Unicode normalization & HTML entity unescape
    t = unicodedata.normalize("NFKC", t)
    t = html.unescape(t)

    # Remove zero-width & control chars (but keep \n, \t, \r for now)
    t = ZERO_WIDTH.sub("", t)
    t = CONTROL_CHARS.sub(" ", t)
    t = NBSP.sub(" ", t)

    # Markdown & HTML stripping (order matters)
    t = MD_CODE_BLOCKS.sub(" ", t)
    t = MD_INLINE_CODE.sub(lambda m: m.group(0).strip("`"), t)  # drop backticks
    t = MD_IMAGE.sub(" ", t)
    t = MD_LINK.sub(r"\1", t)                 # keep link text, drop URL
    t = HEADINGS.sub("", t)
    t = BLOCKQUOTES.sub("", t)
    t = HRULES.sub(" ", t)
    t = LIST_BULLETS.sub("", t)
    t = TAG.sub(" ", t)                       # strip HTML tags
    t = URLS.sub(" ", t)                      # remove naked URLs

    if keep_newlines:
        # Collapse excessive spaces, tidy newlines but preserve paragraphs
        t = MULTISPACE.sub(" ", t)
        t = TRIM_AROUND_NEWLINE.sub("\n", t)
        t = MULTINEWLINE.sub("\n\n", t)       # keep max one empty line
        return t.strip()
    else:
        # Collapse all whitespace to single spaces (one-liner)
        t = re.sub(r"\s+", " ", t)
        return t.strip()

# ---------- Apply cleaning to 2nd column ----------
orig_series = df[texts].astype(str)
clean_nl = orig_series.apply(lambda s: clean_text(s, keep_newlines=True))
clean_compact = orig_series.apply(lambda s: clean_text(s, keep_newlines=False))

# Attach as new columns (keep original intact)
#df["text"] = orig_series
#df["text"] = clean_nl
df["text"] = clean_compact

# ---------- Simple before/after summary ----------
def has_pattern(s, rgx):
    try:
        return bool(rgx.search(s))
    except Exception:
        return False

summary_rows = []
patterns = {
    "html_tags": TAG,
    "md_fence": MD_CODE_BLOCKS,
    "md_inline_code": MD_INLINE_CODE,
    "md_image": MD_IMAGE,
    "md_link": MD_LINK,
    "urls": URLS,
    "heading": HEADINGS,
    "blockquote": BLOCKQUOTES,
    "hrule": HRULES,
    "list_bullet": LIST_BULLETS,
}

total = len(orig_series)
for label, rgx in patterns.items():
    before = sum(orig_series.apply(lambda s: has_pattern(s, rgx)))
    after = sum(clean_nl.apply(lambda s: has_pattern(s, rgx)))
    summary_rows.append({
        "pattern": label,
        "before_count": before,
        "after_count": after,
        "reduction_%": round(100.0 * (before - after) / max(before, 1), 1)
    })

# Length deltas
len_df = pd.DataFrame({
    "orig_len": orig_series.str.len(),
    "clean_nl_len": clean_nl.str.len(),
    "clean_len": clean_compact.str.len()
})
length_summary = pd.DataFrame({
    "metric": ["avg_len", "median_len"],
    "orig": [round(len_df["orig_len"].mean(),1), int(len_df["orig_len"].median())],
    "clean_nl": [round(len_df["clean_nl_len"].mean(),1), int(len_df["clean_nl_len"].median())],
    "clean": [round(len_df["clean_len"].mean(),1), int(len_df["clean_len"].median())],
})

summary_df = pd.DataFrame(summary_rows).sort_values(["after_count","before_count"], ascending=[True, False])

print(summary_df)

# ---------- Save result ----------
out_path = f"./resources/{args.file[:-4]}_clean.csv"
df.to_csv(out_path, index=False, encoding="utf-8")

print(f"Cleaning done, file saved → {out_path}")
