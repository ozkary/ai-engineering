Feature: MTA Turnstile Data Discovery

  Scenario: Discover GCS files and generate a BigQuery external table pattern
    Given an ingestion agent with access to the GCS bucket "mta-turnstile-data"
    When the agent scans the bucket for daily turnstile logs
    Then the agent should return the wildcard URI pattern "gs://mta-turnstile-data/*.csv.gz"
    And the agent should assert that the schema contains the core fields "C/A", "STATION", "DATE", "ENTRIES", "EXIST"