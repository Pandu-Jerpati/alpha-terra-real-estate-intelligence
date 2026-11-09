
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

st.set_page_config(
    page_title="Alpha Terra | Property Intelligence",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ Alpha Terra")
st.subheader("Hyderabad Real Estate Intelligence Dashboard")

st.warning(
    "Proof of concept: All property, project, developer and price "
    "records currently shown are synthetic sample data, not verified "
    "market listings or actual transaction prices."
)

st.sidebar.header("Database Connection")
db_password = st.sidebar.text_input(
    "PostgreSQL password",
    type="password"
)

if not db_password:
    st.info("Enter your PostgreSQL password in the sidebar to load the dashboard.")
    st.stop()

try:
    connection_url = (
        "postgresql+psycopg://postgres:"
        + quote_plus(db_password)
        + "@localhost:6940/alpha_terra_db"
    )

    engine = create_engine(connection_url)

    query = text("""
        SELECT
            l.source_listing_id,
            loc.locality_name,
            cp.bhk_type,
            cp.carpet_area_sqft,
            l.current_asking_price,
            l.current_psf_price,
            l.listing_status
        FROM listings l
        JOIN canonical_properties cp
            ON l.property_id = cp.property_id
        JOIN localities loc
            ON cp.locality_id = loc.locality_id
        WHERE l.source_platform = 'SYNTHETIC_POC'
        ORDER BY loc.locality_name, l.source_listing_id
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    engine.dispose()

    if df.empty:
        st.error("No listing records found in the database.")
        st.stop()

except Exception as error:
    st.error("Database connection or query failed.")
    st.code(str(error))
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

localities = sorted(df["locality_name"].dropna().unique())

selected_localities = st.sidebar.multiselect(
    "Select localities",
    localities,
    default=localities
)

filtered_df = df[
    df["locality_name"].isin(selected_localities)
].copy()

if filtered_df.empty:
    st.warning("Select at least one locality.")
    st.stop()

# KPI metrics
st.header("Market Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Listings", len(filtered_df))

col2.metric(
    "Average Asking Price",
    f"₹{filtered_df['current_asking_price'].mean() / 100000:.2f} L"
)

col3.metric(
    "Average Price / Sq. Ft.",
    f"₹{filtered_df['current_psf_price'].mean():,.0f}"
)

col4.metric(
    "Localities Covered",
    filtered_df["locality_name"].nunique()
)

st.divider()

# Locality analysis
st.header("Locality Price Comparison")

locality_summary = (
    filtered_df.groupby("locality_name", as_index=False)
    .agg(
        listing_count=("source_listing_id", "count"),
        average_psf=("current_psf_price", "mean"),
        average_price=("current_asking_price", "mean")
    )
)

locality_summary["average_psf"] = locality_summary["average_psf"].round(2)

fig_locality = px.bar(
    locality_summary,
    x="locality_name",
    y="average_psf",
    color="locality_name",
    text_auto=".0f",
    title="Average Asking Price per Sq. Ft. by Locality",
    labels={
        "locality_name": "Locality",
        "average_psf": "Average Price per Sq. Ft. (₹)"
    }
)

st.plotly_chart(fig_locality, use_container_width=True)

# BHK analysis
st.header("BHK-wise Price Analysis")

bhk_summary = (
    filtered_df.groupby(["locality_name", "bhk_type"], as_index=False)
    .agg(
        average_psf=("current_psf_price", "mean"),
        listing_count=("source_listing_id", "count")
    )
)

fig_bhk = px.bar(
    bhk_summary,
    x="locality_name",
    y="average_psf",
    color="bhk_type",
    barmode="group",
    text_auto=".0f",
    title="Average Price per Sq. Ft. by Locality and BHK",
    labels={
        "locality_name": "Locality",
        "average_psf": "Average Price per Sq. Ft. (₹)",
        "bhk_type": "Configuration"
    }
)

st.plotly_chart(fig_bhk, use_container_width=True)

# Listing-level details
st.header("Property Listing Details")

display_df = filtered_df.rename(columns={
    "source_listing_id": "Listing ID",
    "locality_name": "Locality",
    "bhk_type": "Configuration",
    "carpet_area_sqft": "Carpet Area (Sq. Ft.)",
    "current_asking_price": "Asking Price (₹)",
    "current_psf_price": "Price per Sq. Ft. (₹)",
    "listing_status": "Status"
})

st.dataframe(display_df, use_container_width=True, hide_index=True)

# Download filtered data
csv_data = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Listing Data (CSV)",
    data=csv_data,
    file_name="alpha_terra_listings.csv",
    mime="text/csv"
)

st.caption(
    "Alpha Terra Proof of Concept | Hyderabad | "
    "Data is synthetic and intended only for demonstration."
)
