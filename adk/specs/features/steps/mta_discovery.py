from behave import given, when, then
from tool_agent.agent import ToolAgent


@given('an ingestion agent with access to the GCS bucket "{bucket_name}"')
def step_impl_init(context, bucket_name):
    # Pass the bucket context to your agent instantiation
    context.bucket_name = bucket_name
    context.agent = ToolAgent(name="StorageIngestor", bucket=bucket_name)


@when("the agent scans the bucket for daily turnstile logs")
def step_impl_scan(context):
    # The agent executes its core system instruction against the bucket
    # and returns a structured dictionary or object containing its findings
    context.agent_output = context.agent.discover_schema()


@then('the agent should return the wildcard URI pattern "{expected_pattern}"')
def step_impl_assert_pattern(context, expected_pattern):
    # Extract the pattern the agent generated for BigQuery
    actual_pattern = context.agent_output.get("uri_pattern", "")
    assert actual_pattern == expected_pattern, (
        f"Expected pattern '{expected_pattern}', but agent generated: '{actual_pattern}'"
    )


@then('the agent should assert that the schema contains the core fields "{fields}"')
def step_impl_assert_fields(context, fields):
    # Parse the expected comma-separated string list
    expected_fields = [f.strip(' "') for f in fields.split(",")]

    actual_schema = context.agent_output.get("detected_fields", [])

    # Ensure every required column was successfully discovered by the agent
    for field in expected_fields:
        assert field in actual_schema, (
            f"Field validation failed. Expected column '{field}' was missing from agent discovery output."
        )
