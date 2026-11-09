

\# Alpha Terra

\## Hyderabad Real Estate Data Intelligence Engine



\### 1. Project Overview



Alpha Terra is a proof-of-concept real estate data intelligence engine focused on four Hyderabad localities:



\- Madhapur

\- Khajaguda

\- Nanakramguda

\- Narsingi



The system demonstrates property data ingestion, database storage, data processing, price analysis and interactive dashboard visualisation.



\### 2. Technology Stack



\- Python

\- PostgreSQL 18

\- PostGIS

\- Pandas

\- NumPy

\- Scikit-learn

\- SQLAlchemy

\- Streamlit

\- Plotly



\### 3. System Architecture



1\. Property sample data is processed using Python.

2\. Cleaned property data is exported to CSV.

3\. PostgreSQL stores localities, developers, projects, properties and listings.

4\. PostGIS supports geographic data storage.

5\. Price observations maintain listing price snapshots.

6\. SQL queries generate locality and BHK-level analytics.

7\. Streamlit and Plotly display interactive dashboard results.



\### 4. Database Modules



\- Localities

\- Developers

\- Projects

\- Canonical Properties

\- Listings

\- Price Observations

\- Transaction Records



\### 5. Analytics



The proof of concept demonstrates:



\- Average asking price by locality

\- Average price per square foot

\- Minimum and maximum price per square foot

\- BHK-wise price comparisons

\- Property listing details

\- Property Intelligence Score calculation

\- K-means clustering demonstration



\### 6. Dashboard



The interactive dashboard provides:



\- Total listing count

\- Average asking price

\- Average price per square foot

\- Locality filters

\- Locality comparison chart

\- BHK comparison chart

\- Listing-level data table

\- CSV download



\### 7. Running the Project



Install dependencies:



```bash

python -m pip install -r requirements.txt

```



Run the data processing pipeline:



```bash

python src/pipeline\_poc.py

```



Run the dashboard:



```bash

python -m streamlit run dashboard/app.py

```



Enter the PostgreSQL password in the dashboard sidebar when prompted.



\### 8. Current Proof-of-Concept Data



The current demonstration contains:



\- 4 localities

\- 1 synthetic developer

\- 4 synthetic projects

\- 9 canonical properties

\- 9 synthetic listings

\- 9 initial price observations



\### 9. Important Data Disclaimer



All current developer, project, property and listing records are synthetic sample data created for proof-of-concept testing.



They are not verified real estate listings, actual transaction records, official market prices or validated developer information.



The initial price observations represent a baseline snapshot only. They do not establish historical price trends.



\### 10. Future Enhancements



\- Integrate verified public real estate datasets.

\- Add authorised API-based data ingestion.

\- Implement automated listing deduplication.

\- Add recurring price observations.

\- Develop locality-level geographic visualisations.

\- Improve property valuation and investment scoring.

\- Add automated data quality and validation tests.



