import factory
from factory.django import DjangoModelFactory
from faker import Faker
from apps.accounts.models import Account

fake = Faker()


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Account
        skip_postgeneration_save = True

    class Params:
        # Traits for common scenarios
        admin = factory.Trait(is_active=True, is_admin=True)
        active = factory.Trait(is_active=True)
        inactive = factory.Trait(is_active=False, is_admin=False)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    phone = factory.LazyAttribute(lambda obj: f"+1{fake.numerify('##########')}")
    full_name = factory.Faker("name")
    birthday = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)
    is_active = False
    is_admin = False
    date_joined = factory.Faker("date_time_this_year")

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or "defaultpassword123"
        obj.set_password(password)
        obj.save(update_fields=["password"])


def create_batch_accounts(size=5, **kwargs):
    """Create multiple account instances."""
    return AccountFactory.create_batch(size, **kwargs)


def create_test_accounts_set():
    """Create a standard set of test accounts with predictable data."""
    accounts = {
        "regular_user": AccountFactory(
            email="regular@example.com",
            full_name="Regular User",
            active=True,  # Using trait
            password="testpass123",
        ),
        "admin_user": AccountFactory(
            email="admin@example.com",
            full_name="Admin User",
            admin=True,  # Using trait
            password="adminpass123",
        ),
        "inactive_user": AccountFactory(
            email="inactive@example.com",
            full_name="Inactive User",
            inactive=True,  # Using trait
            password="inactivepass123",
        ),
        "new_user": AccountFactory(
            email="newuser@example.com",
            full_name="New User",
            is_active=False,
            password="newpass123",
        ),
    }
    return accounts
