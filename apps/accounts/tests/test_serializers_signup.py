import pytest
from django.contrib.auth import get_user_model
from apps.accounts.serializers import SignupSerializer
from datetime import date, datetime, timedelta

User = get_user_model()


@pytest.mark.unit
def test_valid_signup_data(valid_account):
    serializer = SignupSerializer(data=valid_account)
    assert serializer.is_valid()

    account = serializer.save()
    assert account.email == "newuser@example.com"
    assert account.phone == "+1234567890"
    assert account.full_name == "John Doe"
    assert account.birthday == date(1990, 1, 1)
    assert not account.is_active
    assert account.check_password("StrongPass123")


@pytest.mark.unit
def test_password_is_write_only(account_factory):
    """Test that password field is write-only"""
    account = account_factory.build(password="testpass123")
    serializer = SignupSerializer(instance=account)

    assert "password" not in serializer.data


@pytest.mark.unit
def test_password_minimum_length_validation(invalid_password_account):
    """Test password minimum length validation"""
    serializer = SignupSerializer(data=invalid_password_account)

    assert not serializer.is_valid()
    assert "password" in serializer.errors
    assert "Ensure this field has at least 6 characters" in str(
        serializer.errors["password"]
    )


@pytest.mark.unit
def test_missing_required_fields(account_factory):
    """Test validation when required fields are missing"""
    serializer = SignupSerializer(data={})
    assert not serializer.is_valid()

    required_fields = ["email", "password", "phone", "full_name", "birthday"]
    for field in required_fields:
        assert field in serializer.errors


@pytest.mark.unit
def test_invalid_email_format(invalid_email_account):
    """Test validation with invalid email format"""
    serializer = SignupSerializer(data=invalid_email_account)

    assert not serializer.is_valid()
    assert "email" in serializer.errors


@pytest.mark.unit
def test_duplicate_email_validation(account_factory):
    """Test that duplicate email addresses are not allowed"""
    account_factory.create(email="existing@example.com")
    duplicated_account = {
        "email": "existing@example.com",
        "password": "ValidPass123",
        "phone": "+9876543210",
        "full_name": "Another User",
        "birthday": "1995-05-05",
    }
    serializer = SignupSerializer(data=duplicated_account)

    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert (
        "account with this email already exists"
        in str(serializer.errors["email"]).lower()
    )


@pytest.mark.unit
@pytest.mark.django_db
def test_create_method_uses_create_user(valid_account):
    """Test that create method uses Account.objects.create_user"""
    serializer = SignupSerializer(data=valid_account)
    assert serializer.is_valid()

    account = serializer.save()
    assert User.objects.filter(email="newuser@example.com").exists()
    assert account.check_password("StrongPass123")
    assert not account.is_active


@pytest.mark.unit
def test_invalid_birthday_format(invalid_birthday_account):
    """Test validation with invalid birthday format"""
    serializer = SignupSerializer(data=invalid_birthday_account)
    assert not serializer.is_valid()
    assert "birthday" in serializer.errors


@pytest.mark.unit
@pytest.mark.django_db
def test_future_birthday_validation():
    """Test validation with future birthday date"""
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

    data = {
        "email": "test@example.com",
        "password": "ValidPass123",
        "phone": "+1234567890",
        "full_name": "Test User",
        "birthday": future_date,
    }

    serializer = SignupSerializer(data=data)
    assert serializer.is_valid()


@pytest.mark.unit
@pytest.mark.django_db
def test_serializer_fields():
    """Test that serializer has correct fields defined"""
    serializer = SignupSerializer()
    expected_fields = ["email", "password", "phone", "full_name", "birthday"]

    assert set(serializer.fields.keys()) == set(expected_fields)


@pytest.mark.unit
@pytest.mark.django_db
def test_password_field_properties():
    """Test password field properties"""
    serializer = SignupSerializer()
    password_field = serializer.fields["password"]

    assert password_field.write_only is True
    assert password_field.min_length == 6
    assert password_field.required is True


@pytest.mark.unit
@pytest.mark.django_db
def test_create_with_extra_fields():
    """Test that extra fields are ignored during creation"""
    data = {
        "email": "extra@example.com",
        "password": "ValidPass123",
        "phone": "+1234567890",
        "full_name": "Extra User",
        "birthday": "1990-01-01",
        "extra_field": "should be ignored",
    }

    serializer = SignupSerializer(data=data)
    assert serializer.is_valid()

    account = serializer.save()
    assert account.email == "extra@example.com"
    assert not hasattr(account, "extra_field")


@pytest.mark.unit
@pytest.mark.django_db
def test_password_not_returned_in_response():
    """Test that password is not included in serialized response data"""
    data = {
        "email": "response@example.com",
        "password": "SecurePass123",
        "phone": "+1234567890",
        "full_name": "Response User",
        "birthday": "1992-02-02",
    }

    serializer = SignupSerializer(data=data)
    assert serializer.is_valid()
    account = serializer.save()

    response_serializer = SignupSerializer(instance=account)
    response_data = response_serializer.data

    assert "password" not in response_data
    assert "email" in response_data
    assert "phone" in response_data
    assert "full_name" in response_data
    assert "birthday" in response_data
