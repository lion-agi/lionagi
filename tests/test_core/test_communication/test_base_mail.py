import pytest
from pydantic import ValidationError

from lionagi.core.communication.base_mail import BaseMail
from lionagi.core.generic.types import Element
from lionagi.core.typing import ID


@pytest.fixture
def sample_element():
    class SampleElement(Element):
        """Sample element class for ID testing"""

        pass

    return SampleElement()


def test_base_mail_initialization():
    """Test basic initialization of BaseMail"""
    mail = BaseMail(sender="system", recipient="user")
    assert mail.sender == "system"
    assert mail.recipient == "user"


def test_base_mail_default_values():
    """Test default values in BaseMail"""
    mail = BaseMail()
    assert mail.sender == "N/A"
    assert mail.recipient == "N/A"


def test_base_mail_with_valid_roles():
    """Test BaseMail with valid system roles"""
    valid_roles = ["system", "user", "assistant", "N/A"]

    for role in valid_roles:
        mail = BaseMail(sender=role, recipient=role)
        assert mail.sender == role
        assert mail.recipient == role


def test_base_mail_with_id(sample_element):
    """Test BaseMail with ID type values"""
    mail = BaseMail(sender=sample_element, recipient=sample_element)
    assert mail.sender == sample_element.ln_id
    assert mail.recipient == sample_element.ln_id


def test_base_mail_invalid_sender():
    """Test BaseMail with invalid sender"""
    with pytest.raises(ValueError, match="Invalid sender or recipient"):
        BaseMail(sender=123)  # Invalid type


def test_base_mail_invalid_recipient():
    """Test BaseMail with invalid recipient"""
    with pytest.raises(ValueError, match="Invalid sender or recipient"):
        BaseMail(recipient=123)  # Invalid type


def test_base_mail_none_values():
    """Test BaseMail with None values defaulting to N/A"""
    mail = BaseMail(sender=None, recipient=None)
    assert mail.sender == "N/A"
    assert mail.recipient == "N/A"


def test_base_mail_model_validation():
    """Test BaseMail model validation"""
    # Test with valid data
    valid_data = {"sender": "system", "recipient": "user"}
    mail = BaseMail(**valid_data)

    # Check only sender and recipient in validation
    serialized = {"sender": mail.sender, "recipient": mail.recipient}
    assert serialized == valid_data

    # Test with invalid data
    invalid_data = {"sender": 123, "recipient": {}}
    with pytest.raises(ValidationError):
        BaseMail(**invalid_data)


def test_base_mail_field_validator():
    """Test the field validator for sender and recipient"""
    from lionagi.core.communication.utils import validate_sender_recipient

    # Test with valid input
    assert validate_sender_recipient("system") == "system"
    assert validate_sender_recipient("N/A") == "N/A"
    assert validate_sender_recipient(None) == "N/A"

    # Test with invalid input
    with pytest.raises(ValueError):
        validate_sender_recipient(123)


def test_base_mail_inheritance():
    """Test that BaseMail properly inherits from Element and Communicatable"""
    mail = BaseMail()

    # Test Element inheritance
    assert hasattr(mail, "ln_id")
    assert hasattr(mail, "created_timestamp")

    # Test Communicatable inheritance
    assert hasattr(mail, "sender")
    assert hasattr(mail, "recipient")


def test_base_mail_serialization():
    """Test BaseMail serialization"""
    mail = BaseMail(sender="system", recipient="user")
    serialized = mail.model_dump()

    assert isinstance(serialized, dict)
    assert serialized["sender"] == "system"
    assert serialized["recipient"] == "user"
    assert "ln_id" in serialized
    assert "created_timestamp" in serialized
