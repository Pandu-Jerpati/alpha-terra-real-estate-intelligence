import pandas as pd
from sqlalchemy import create_engine, text
from getpass import getpass

# Project paths
CSV_PATH = "data/cleaned_properties.csv"

# Read cleaned property data
df = pd.read_csv(CSV_PATH)

# Database connection
password = getpass("Enter PostgreSQL password: ")

engine = create_engine(
    "postgresql+psycopg://postgres@localhost:6940/alpha_terra_db",
    connect_args={"password": password}
)

insert_sql = text("""
    INSERT INTO canonical_properties (
        project_id,
        locality_id,
        bhk_type,
        carpet_area_sqft
    )
    SELECT
        p.project_id,
        l.locality_id,
        :bhk_type,
        :carpet_area
    FROM projects p
    JOIN localities l ON l.locality_id = p.locality_id
    WHERE l.locality_name = :locality
      AND p.canonical_project_name =
          'SYNTHETIC POC PROJECT - ' || l.locality_name
""")

try:
    with engine.begin() as connection:
        for _, row in df.iterrows():
            result = connection.execute(
                insert_sql,
                {
                    "locality": row["locality"],
                    "bhk_type": f'{int(row["bhk"])} BHK',
                    "carpet_area": float(row["carpet_area"])
                }
            )

            if result.rowcount != 1:
                raise RuntimeError(
                    f"Expected one project match for {row['listing_id']}; "
                    f"got {result.rowcount}"
                )

    print(f"SUCCESS: Inserted {len(df)} canonical properties.")

except Exception as error:
    print("IMPORT FAILED:", error)

finally:
    engine.dispose()