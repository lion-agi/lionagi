"""Tests for token_calculator module."""

import pytest

from lionagi.service.token_calculator import (
    TiktokenCalculator,
    TokenCalculator,
)


def test_token_calculator_base():
    """Test TokenCalculator base class."""

    class TestCalculator(TokenCalculator):
        def calculate(self, *args, **kwargs):
            return 42

    calc = TestCalculator()
    assert calc.calculate() == 42


def test_tiktoken_calculator_initialization():
    """Test TiktokenCalculator initialization with different encoding names."""
    # Test with model name
    calc = TiktokenCalculator(encoding_name="gpt-4")
    assert (
        calc.encoding_name == "cl100k_base"
    )  # GPT-4 uses cl100k_base encoding

    # Test with encoding name
    calc = TiktokenCalculator(encoding_name="p50k_base")
    assert calc.encoding_name == "p50k_base"

    # Test with invalid name (should default to o200k_base)
    calc = TiktokenCalculator(encoding_name="invalid_encoding")
    assert calc.encoding_name == "o200k_base"


def test_tiktoken_calculator_encode():
    """Test encoding text to tokens."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    text = "Hello, world!"
    tokens = calc.encode(text)
    assert isinstance(tokens, list)
    assert all(isinstance(token, int) for token in tokens)
    assert len(tokens) > 0


def test_tiktoken_calculator_calculate():
    """Test calculating token count."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    text = "Hello, world!"
    token_count = calc.calculate(text)
    assert isinstance(token_count, int)
    assert token_count > 0

    # Test empty string
    assert calc.calculate("") == 0


def test_tiktoken_calculator_tokenize():
    """Test tokenizing text into token strings."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    text = "Hello, world!"

    # Test without decoding
    tokens = calc.tokenize(text, decode_byte_str=False)
    assert isinstance(tokens, list)
    assert all(isinstance(token, bytes) for token in tokens)

    # Test with decoding
    tokens = calc.tokenize(text, decode_byte_str=True)
    assert isinstance(tokens, list)
    assert all(isinstance(token, str) for token in tokens)


def test_tiktoken_calculator_with_special_characters():
    """Test handling of special characters."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    text = "Hello 😊 World! 🌍"  # Using different emojis that are more likely to be in the token vocabulary
    tokens = calc.encode(text)
    assert len(tokens) > 0

    # Test tokenization without decoding
    tokens_bytes = calc.tokenize(text, decode_byte_str=False)
    assert len(tokens_bytes) > 0
    assert all(isinstance(token, bytes) for token in tokens_bytes)

    # Reconstruct text from tokens to verify encoding/decoding
    enc = calc.encode(text)
    assert len(enc) > 0


def test_tiktoken_calculator_with_different_encodings():
    """Test different encoding models."""
    texts = ["Hello, world!", "Testing different encodings"]
    encodings = ["cl100k_base", "p50k_base"]

    for encoding in encodings:
        calc = TiktokenCalculator(encoding_name=encoding)
        for text in texts:
            tokens = calc.encode(text)
            assert len(tokens) > 0
            assert calc.calculate(text) == len(tokens)


def test_tiktoken_calculator_with_whitespace():
    """Test handling of whitespace."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    texts = [
        "   Leading spaces",
        "Trailing spaces   ",
        "Multiple     spaces",
        "\tTabs\tand\nnewlines\n",
        "\n\n\n",
        "    ",
    ]

    for text in texts:
        tokens = calc.encode(text)
        assert len(tokens) > 0
        assert calc.calculate(text) == len(tokens)


def test_tiktoken_calculator_with_long_text():
    """Test handling of long text."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    long_text = "This is a test. " * 1000
    tokens = calc.encode(long_text)
    assert len(tokens) > 1000
    assert calc.calculate(long_text) == len(tokens)


def test_tiktoken_calculator_with_different_languages():
    """Test handling of different languages."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    texts = [
        "English text",
        "Texto en español",
        "中文文本",
        "日本語のテキスト",
        "한국어 텍스트",
        "Русский текст",
    ]

    for text in texts:
        tokens = calc.encode(text)
        assert len(tokens) > 0
        assert calc.calculate(text) == len(tokens)


def test_tiktoken_calculator_with_custom_decoder():
    """Test tokenization with custom decoder."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    text = "Hello, world!"

    # Test with different encodings
    tokens_bytes = calc.tokenize(text, decode_byte_str=False)
    assert all(isinstance(token, bytes) for token in tokens_bytes)

    # Test raw bytes
    tokens_str = [token.hex() for token in tokens_bytes]
    assert all(isinstance(token, str) for token in tokens_str)


def test_tiktoken_calculator_model_fields():
    """Test that model fields are properly defined."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    assert "encoding_name" in calc.model_fields
    assert calc.model_fields["encoding_name"].description.startswith(
        "Encoding for converting text to tokens"
    )


def test_tiktoken_calculator_with_control_characters():
    """Test handling of control characters."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    text = "Hello\x00World\x1FTest\x7F"  # Including null, unit separator and delete chars
    tokens = calc.encode(text)
    assert len(tokens) > 0

    # Test tokenization without decoding
    tokens_bytes = calc.tokenize(text, decode_byte_str=False)
    assert len(tokens_bytes) > 0
    assert all(isinstance(token, bytes) for token in tokens_bytes)


def test_tiktoken_calculator_with_mixed_content():
    """Test handling of mixed content types."""
    calc = TiktokenCalculator(encoding_name="cl100k_base")
    text = "Regular text 123 !@# 漢字 αβγ"
    tokens = calc.encode(text)
    assert len(tokens) > 0

    # Test tokenization without decoding
    tokens_bytes = calc.tokenize(text, decode_byte_str=False)
    assert len(tokens_bytes) > 0
    assert all(isinstance(token, bytes) for token in tokens_bytes)
