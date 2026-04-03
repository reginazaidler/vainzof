from __future__ import annotations

import pandas as pd


EXPECTED_CTR_CURVE: dict[int, float] = {
    1: 0.285,
    2: 0.155,
    3: 0.11,
    4: 0.08,
    5: 0.062,
    6: 0.05,
    7: 0.041,
    8: 0.034,
    9: 0.029,
    10: 0.025,
    11: 0.021,
    12: 0.018,
}


def expected_ctr_from_position(position: float) -> float:
    bucket = int(round(position))
    bucket = max(1, min(12, bucket))
    return EXPECTED_CTR_CURVE.get(bucket, 0.018)


def filter_opportunities(
    df: pd.DataFrame,
    min_impressions: int,
    min_position: float,
    max_position: float,
    exclude_brand_queries: list[str],
) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df[
        (df["impressions"] >= min_impressions)
        & (df["position"] >= min_position)
        & (df["position"] <= max_position)
    ].copy()

    if exclude_brand_queries:
        pattern = "|".join(exclude_brand_queries)
        filtered = filtered[~filtered["query"].str.lower().str.contains(pattern, regex=True, na=False)]

    return filtered


def score_opportunities(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    scored = df.copy()
    scored["expected_ctr"] = scored["position"].apply(expected_ctr_from_position)
    ctr_gap = (scored["expected_ctr"] - scored["ctr"]).clip(lower=0)
    scored["opportunity_score"] = scored["impressions"] * ctr_gap / scored["position"].clip(lower=1)
    scored = scored.sort_values(by="opportunity_score", ascending=False)
    return scored
