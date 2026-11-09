
-- Alpha Terra: BHK-wise price analysis
-- Synthetic proof-of-concept data only

SELECT
    loc.locality_name,
    cp.bhk_type,

    COUNT(li.listing_id) AS listing_count,

    ROUND(AVG(li.current_asking_price), 2)
        AS avg_asking_price,

    ROUND(AVG(li.current_psf_price), 2)
        AS avg_price_per_sqft

FROM listings li

JOIN canonical_properties cp
    ON li.property_id = cp.property_id

JOIN localities loc
    ON cp.locality_id = loc.locality_id

GROUP BY
    loc.locality_name,
    cp.bhk_type

ORDER BY
    loc.locality_name,
    cp.bhk_type;
