"""Tests for the TaskBoard package metadata."""

import taskboard


def test_package_metadata_is_exposed():
    assert taskboard.__version__ == "0.1.0"
    assert taskboard.__doc__
    assert "TaskBoard" in taskboard.__doc__