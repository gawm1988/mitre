"""
This script filters the ID, title, description, and associated tactics from MITRE ATT&CK techniques and writes them to a DataFrame.
"""

from pathlib import Path
import pandas as pd
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--file", required=True, type=Path)
args = arg_parser.parse_args()

def build_csv(xlsx_path: Path, sheet: str, out_csv: Path) -> None:

    TACTIC_TO_INDEX = {
        "Reconnaissance": 0,
        "Resource Development": 1,
        "Initial Access": 2,
        "Execution": 3,
        "Persistence": 4,
        "Privilege Escalation": 5,
        "Defense Evasion": 6,
        "Credential Access": 7,
        "Discovery": 8,
        "Lateral Movement": 9,
        "Collection": 10,
        "Command and Control": 11,
        "Exfiltration": 12,
        "Impact": 13,
    }

    INDEX_TO_TACTIC = {v: k for k, v in TACTIC_TO_INDEX.items()}

    def parse_tactics(tactics_str: str) -> list[int]:
        if pd.isna(tactics_str):
            return []
        return [TACTIC_TO_INDEX[t.strip()] for t in tactics_str.split(",") if t.strip() in TACTIC_TO_INDEX]

    df = pd.read_excel(
        xlsx_path,
        sheet_name=sheet,
        usecols=["ID", "name", "description", "tactics"],
        dtype=str
    )

    df["text"] = df["name"] + ": " + df["description"]
    df["tactic_ids"] = df["tactics"].apply(parse_tactics)
    '''
    # One-Hot-Encoding (optional)
    for i in range(14):
        tactic_name = INDEX_TO_TACTIC[i]
        df[tactic_name] = df["tactic_ids"].apply(lambda ids: int(i in ids))
    '''
    columns_to_export = (["ID", "text", "tactic_ids"] )
                         # + list(INDEX_TO_TACTIC.values()))    #uncomment line for adding one-hot encoding
    df[columns_to_export].to_csv(out_csv, index=False, encoding="utf-8")
    print(f"{len(df):,} entries exported → {out_csv}")



def main() -> None:
    xlsx_path = Path(f"./resources/{args.file}")
    sheet = "techniques"
    out_csv = Path("./resources/techniques.csv")

    build_csv(xlsx_path, sheet, out_csv)

if __name__ == "__main__":
    main()
