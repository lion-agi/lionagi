# File: tests/test_validate/test_validate_key.py

from typing import Any

import pytest

from lionagi.libs.validate.fuzzy_match_keys import fuzzy_match_keys


class TestValidateKeys:
    """Comprehensive tests for fuzzy_match_keys function."""

    def test_basic_functionality(self):
        """Test basic functionality with default parameters."""
        test_dict = {
            "user_name": "John",
            "email_addr": "john@example.com",
        }
        expected = ["username", "email_address"]

        result = fuzzy_match_keys(test_dict, expected)
        # With default settings, original keys should be preserved
        assert "username" in result
        assert "email_address" in result

    def test_exact_matches(self):
        """Test when keys exactly match expected keys."""
        exact_dict = {
            "username": "John",
            "email_address": "john@example.com",
        }
        expected = ["username", "email_address"]
        result = fuzzy_match_keys(exact_dict, expected)
        assert result == exact_dict

    def test_empty_inputs(self):
        """Test empty input scenarios."""
        # Empty dictionary
        assert fuzzy_match_keys({}, []) == {}

        # Empty expected keys
        result = fuzzy_match_keys({"a": 1}, [])
        assert result == {"a": 1}

    def test_fuzzy_matching(self):
        """Test fuzzy matching with different thresholds."""
        test_dict = {"user_name": "John", "emailAddress": "john@example.com"}
        expected = ["username", "email_address"]

        # Test with fuzzy matching enabled and remove unmatched
        result = fuzzy_match_keys(
            test_dict,
            expected,
            fuzzy_match=True,
            similarity_threshold=0.7,
            handle_unmatched="remove",
        )
        assert "username" in result
        assert "email_address" in result
        assert "user_name" not in result
        assert "emailAddress" not in result

        # Test with fuzzy matching disabled
        result_no_fuzzy = fuzzy_match_keys(
            test_dict, expected, fuzzy_match=False
        )
        assert "user_name" in result_no_fuzzy
        assert "emailAddress" in result_no_fuzzy

    def test_handle_unmatched_modes(self):
        """Test different handle_unmatched modes."""
        test_dict = {"user_name": "John", "extra": "value"}
        expected = ["username"]

        # Test raise mode
        with pytest.raises(ValueError):
            fuzzy_match_keys(test_dict, expected, handle_unmatched="raise")

        # Test remove mode
        result_remove = fuzzy_match_keys(
            test_dict, expected, handle_unmatched="remove"
        )
        assert "extra" not in result_remove

        # Test fill mode
        result_fill = fuzzy_match_keys(
            test_dict, expected, handle_unmatched="fill", fill_value="default"
        )
        assert "extra" in result_fill
        assert "username" in result_fill

        # Test force mode
        result_force = fuzzy_match_keys(
            test_dict, expected, handle_unmatched="force", fill_value="default"
        )
        assert "extra" not in result_force
        assert "username" in result_force

    def test_strict_mode(self):
        """Test strict mode behavior."""
        test_dict = {"partial": "value"}
        expected = ["partial", "missing"]

        with pytest.raises(ValueError):
            fuzzy_match_keys(test_dict, expected, strict=True)

        result = fuzzy_match_keys(test_dict, expected, strict=False)
        assert "partial" in result

    def test_edge_cases_and_invalid_inputs(self):
        """Test edge cases and invalid inputs."""
        valid_dict = {"key": "value"}
        valid_keys = ["key"]

        # Invalid similarity threshold
        with pytest.raises(ValueError):
            fuzzy_match_keys(valid_dict, valid_keys, similarity_threshold=1.5)

        # None input dictionary
        with pytest.raises(TypeError):
            fuzzy_match_keys(None, valid_keys)

        # None keys
        with pytest.raises(TypeError):
            fuzzy_match_keys(valid_dict, None)

        # Invalid similarity algorithm
        with pytest.raises(ValueError):
            fuzzy_match_keys(valid_dict, valid_keys, similarity_algo="invalid")

    def test_fill_value_and_mapping(self):
        """Test fill value and mapping functionality."""
        test_dict = {"existing": "value"}
        expected = ["existing", "missing1", "missing2"]
        fill_mapping = {"missing1": "custom1", "missing2": "custom2"}

        result = fuzzy_match_keys(
            test_dict,
            expected,
            handle_unmatched="fill",
            fill_mapping=fill_mapping,
        )
        assert result["missing1"] == "custom1"
        assert result["missing2"] == "custom2"

    def test_custom_similarity_function(self):
        """Test using a custom similarity function."""

        def custom_similarity(s1: str, s2: str) -> float:
            return 1.0 if s1.lower() == s2.lower() else 0.0

        test_dict = {"User_Name": "John"}
        expected = ["user_name"]

        result = fuzzy_match_keys(
            test_dict,
            expected,
            similarity_algo=custom_similarity,
            fuzzy_match=True,
        )
        assert len(result) > 0
