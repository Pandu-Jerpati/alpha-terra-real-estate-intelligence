import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def run_pipeline():
    print("=" * 66)
    print(" ALPHA TERRA REAL ESTATE INTELLIGENCE ENGINE (HYDERABAD CORRIDOR) ")
    print("=" * 66)

    # 1. Raw Ingestion (Madhapur, Khajaguda, Nanakramguda, Narsingi)
    raw_data = [
        {"listing_id": "HYD-MBD-001", "locality": "Madhapur", "bhk": 3, "carpet_area": 1650, "asking_price": 18500000, "dist_tech_hub_km": 1.2, "dev_score": 4.5, "rera_valid": True},
        {"listing_id": "HYD-MBD-002", "locality": "Madhapur", "bhk": 2, "carpet_area": 1100, "asking_price": 12000000, "dist_tech_hub_km": 1.8, "dev_score": 4.2, "rera_valid": True},
        {"listing_id": "HYD-KHJ-001", "locality": "Khajaguda", "bhk": 3, "carpet_area": 1800, "asking_price": 17500000, "dist_tech_hub_km": 3.1, "dev_score": 4.0, "rera_valid": True},
        {"listing_id": "HYD-KHJ-002", "locality": "Khajaguda", "bhk": 2, "carpet_area": 1250, "asking_price": 11000000, "dist_tech_hub_km": 3.4, "dev_score": 3.8, "rera_valid": True},
        {"listing_id": "HYD-NNK-001", "locality": "Nanakramguda", "bhk": 3, "carpet_area": 2200, "asking_price": 28000000, "dist_tech_hub_km": 0.8, "dev_score": 4.8, "rera_valid": True},
        {"listing_id": "HYD-NNK-002", "locality": "Nanakramguda", "bhk": 4, "carpet_area": 3100, "asking_price": 42000000, "dist_tech_hub_km": 1.1, "dev_score": 4.9, "rera_valid": True},
        {"listing_id": "HYD-NRS-001", "locality": "Narsingi", "bhk": 2, "carpet_area": 1150, "asking_price": 7800000, "dist_tech_hub_km": 6.5, "dev_score": 3.7, "rera_valid": True},
        {"listing_id": "HYD-NRS-002", "locality": "Narsingi", "bhk": 3, "carpet_area": 1550, "asking_price": 10500000, "dist_tech_hub_km": 6.0, "dev_score": 3.9, "rera_valid": True},
        {"listing_id": "HYD-NRS-003", "locality": "Narsingi", "bhk": 2, "carpet_area": 950, "asking_price": 6200000, "dist_tech_hub_km": 7.2, "dev_score": 3.4, "rera_valid": False},
        {"listing_id": "HYD-MBD-003", "locality": "Madhapur", "bhk": 4, "carpet_area": 2800, "asking_price": 34000000, "dist_tech_hub_km": 1.0, "dev_score": 4.6, "rera_valid": True}
    ]

    df = pd.DataFrame(raw_data)
    print(f"\n[1] Ingestion: Received {len(df)} records.")

    # 2. Validation & Quality Filter
    df["price_psf"] = (df["asking_price"] / df["carpet_area"]).round(2)
    valid_df = df[df["rera_valid"] == True].copy()
    quarantined = len(df) - len(valid_df)
    print(f"[2] Validation: Quarantined {quarantined} invalid record(s).")

    # 3. K-Means Clustering
    features = ["price_psf", "asking_price", "dist_tech_hub_km"]
    scaler = StandardScaler()
    scaled_matrix = scaler.fit_transform(valid_df[features])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    valid_df["cluster_raw"] = kmeans.fit_predict(scaled_matrix)

    psf_order = valid_df.groupby("cluster_raw")["price_psf"].mean().sort_values().index
    cluster_labels = {
        psf_order[0]: "Budget Friendly / Value Hub",
        psf_order[1]: "Mid-Range / Core Residential",
        psf_order[2]: "High-Rise / Premium Tech Hub"
    }
    valid_df["market_category"] = valid_df["cluster_raw"].map(cluster_labels)

    # 4. Property Intelligence Score (0 - 100)
    max_dist = valid_df["dist_tech_hub_km"].max()
    valid_df["loc_score"] = (1 - (valid_df["dist_tech_hub_km"] / (max_dist + 1))) * 100
    cluster_mean_psf = valid_df.groupby("cluster_raw")["price_psf"].transform("mean")
    valid_df["val_score"] = np.clip((1 + (cluster_mean_psf - valid_df["price_psf"]) / cluster_mean_psf) * 50, 10, 100)
    valid_df["dev_norm"] = (valid_df["dev_score"] / 5.0) * 100

    valid_df["property_intelligence_score"] = (
        0.35 * valid_df["val_score"] +
        0.30 * valid_df["loc_score"] +
        0.20 * valid_df["dev_norm"] +
        0.15 * 100.0
    ).round(2)

    valid_df.to_csv("data/cleaned_properties.csv", index=False)
    print("[3] Output saved to 'data/cleaned_properties.csv'.\n")

    cols = ["listing_id", "locality", "bhk", "carpet_area", "asking_price", "price_psf", "market_category", "property_intelligence_score"]
    print(valid_df[cols].to_string(index=False))

if __name__ == "__main__":
    run_pipeline()