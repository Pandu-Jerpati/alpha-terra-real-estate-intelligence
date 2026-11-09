
import pandas as pd
from sqlalchemy import create_engine, text
from getpass import getpass

CSV_PATH = "data/cleaned_properties.csv"

df = pd.read_csv(CSV_PATH)

password = getpass("Enter PostgreSQL password: ")

engine = create_engine(
    "postgresql+psycopg://postgres@localhost:6940/alpha_terra_db",
    connect_args={"password": password}
)

insert_sql = text("""
    INSERT INTO listings (
        property_id,
        source_platform,
        source_listing_id,
        listing_status,
        current_asking_price,
        carpet_area_sqft,
        is_active
    )
    SELECT
        cp.property_id,
        'SYNTHETIC_POC',
        CAST(:listing_id AS VARCHAR),
        'ACTIVE',
        :asking_price,
        :carpet_area,
        TRUE
    FROM canonical_properties cp
    JOIN localities l
        ON l.locality_id = cp.locality_id
    WHERE l.locality_name = :locality
      AND cp.bhk_type = :bhk_type
      AND cp.carpet_area_sqft = :carpet_area
      AND NOT EXISTS (
          SELECT 1
          FROM listings existing
          WHERE existing.source_platform = 'SYNTHETIC_POC'
            AND existing.source_listing_id =
                CAST(:listing_id AS VARCHAR)
      )
""")

try:
    inserted = 0

    with engine.begin() as connection:
        for _, row in df.iterrows():

            result = connection.execute(
                insert_sql,
                {
                    "listing_id": str(row["listing_id"]),
                    "locality": str(row["locality"]),
                    "bhk_type": f'{int(row["bhk"])} BHK',
                    "asking_price": float(row["asking_price"]),
                    "carpet_area": float(row["carpet_area"])
                }
            )

            if result.rowcount != 1:
                raise RuntimeError(
                    f"Listing {row['listing_id']} was not inserted. "
                    "Check its property mapping or duplicate status."
                )

            inserted += 1

    print(f"SUCCESS: Inserted {inserted} synthetic listings.")
    print("Price per square foot will be calculated by PostgreSQL.")

except Exception as error:
    print("IMPORT FAILED:", error)

finally:
    engine.dispose()
