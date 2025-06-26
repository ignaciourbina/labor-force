import pandas as pd
import re

def parse_frey_osborne(xlsx_path: str,
                       csv_path: str | None = None) -> pd.DataFrame:
    """
    Parse Frey–Osborne automation-risk data.

    Parameters
    ----------
    xlsx_path : str
        Path to frey_osborne_automation_risk_index.xlsx.
    csv_path : str | None, default None
        If provided, the parsed table is saved to this CSV.

    Returns
    -------
    pd.DataFrame
        Columns: Rank (int), Probability (float), Label (Int64 with NA),
                 SOC code (str), Occupation (str)
    """
    # 1) Load and drop header
    raw = pd.read_excel(xlsx_path, header=None)
    lines = raw.iloc[1:, 0].astype(str)

    # 2) Regex
    pattern = re.compile(
        r"^\s*(\d+)\.\s+([01](?:\.\d+)?)\s+(?:(0|1)\s+)?(\d{2}-\d{4})\s+(.+)$"
    )

    parsed = []
    for line in lines:
        m = pattern.match(line)
        if not m:
            raise ValueError(f"Couldn’t parse: {line!r}")

        rank        = int(m.group(1))
        probability = float(m.group(2))

        # --- NEW: keep blank label as NA -------------------------------
        label_raw = m.group(3)
        label = pd.NA if label_raw is None else int(label_raw)
        # ----------------------------------------------------------------

        soc_code    = m.group(4)
        occupation  = m.group(5).strip()

        parsed.append((rank, probability, label, soc_code, occupation))

    df = (
        pd.DataFrame(
            parsed,
            columns=["Rank", "Probability", "Label", "SOC code", "Occupation"]
        )
        .astype({"Label": "Int64"})        # nullable integer
        .sort_values("Rank")
        .reset_index(drop=True)
    )

    if csv_path:
        df.to_csv(csv_path, index=False)

    return df

# Example usage:
df = parse_frey_osborne("frey_osborne_automation_risk_index.xlsx",
                        "frey_osborne_automation_risk_index_clean.csv")

pd.read_csv("frey_osborne_automation_risk_index_clean.csv").to_excel("frey_osborne_automation_risk_index_clean.xlsx", index=False)

