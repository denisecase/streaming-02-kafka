"""tests/test_smoke.py - Smoke test for the example.

WHY: Professional Python projects include tests to verify that code runs
     correctly and to catch problems early when changes are made.
     Running tests is part of the standard workflow in every module.

OBS: You do not need to read or modify this file.
     It exists so that `uv run python -m pytest` passes.
"""


def test_producer_case_runs():
    """Confirm the Kafka producer example module runs without error."""
    from streaming.kafka_producer_case import main

    main()
