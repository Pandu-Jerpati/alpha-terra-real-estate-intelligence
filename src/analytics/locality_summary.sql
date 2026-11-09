
-- Alpha Terra: Locality-level market summary
-- Synthetic proof-of-concept data only

SELECT
    loc.locality_name,
    COUNT(li.listing_id) AS listing_count,

    ROUND(AVG(li.current_asking_price), 2)
        AS avg_asking_price,

    ROUND(AVG(li.current_psf_price), 2)
        AS avg_price_per_sqft,

    ROUND(MIN(li.current_psf_price), 2)
        AS min_price_per_sqft,

    ROUND(MAX(li.current_psf_price), 2)
        AS max_price_per_sqft

FROM listings li

JOIN canonical_properties cp
    ON li.property_id = cp.property_id

JOIN localities loc
    ON cp.locality_id = loc.locality_id

GROUP BY loc.locality_name

ORDER BY avg_price_per_sqft DESC;
