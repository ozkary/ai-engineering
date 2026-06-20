# System Instructions

When doing the data discovery and analysis you must follow these governance and requirement information, which should enable you to have context about the data and how to enforce design standards and naming conventions.

## GOVERNANCE_RULES
- Dataset: Use '{data_set}' for ALL tables, views, and procedures.
- Field Naming: Use snake_case for all column names with lower case letters (e.g., station_name, turnstile_id).
- External Table Naming: Use 'ext_' prefix (e.g.  ext_turnstile)
- Table Naming: Use 'dim_' prefix for physical tables (e.g., dim_turnstile).
- View Naming: Use 'vw_' prefix for logic layers (e.g., vw_turnstile).
- Stored Procedures Naming:  Use 'sp_' prefix with the area name and action name (e.g., sp_station_incremental_update) 
- Lineage: Every 'CREATE' statement must include a description identifying the source GCS path.
- Data Pipeline Naming: Use 'dp_' prefix with the area name and action (e.g., dp_station_incremental_update)

## PROJECT_REQUIREMENTS
Analyze the MTA dataset and identify all dimension areas (e.g., Station, Booth, Time).

- Create a view for each dimension: vw_{area}. 
- Each view should generate a surrogate key for the record using a combination of unique fields 'sk_{area}' use using TO_HEX(SHA1(CONCAT(natural_keys))) 
- Create a central fact view: vw_turnstile.
- The Facts must use these 'sk_' keys as Foreign Keys to join with Dimensions
- Combine the 'date' and 'time' fields from the raw source into a single 'created' DATETIME field.
- Ensure type casting is done on the views (e.g., strings to int)
- The final output should follow a Star Schema architecture to simplify BI reporting.
