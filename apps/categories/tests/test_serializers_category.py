import pytest
from apps.categories.serializers import CategorySerializer


@pytest.mark.unit
def test_category_serializer_fields(category_factory):
    """Test that CategorySerializer has correct fields"""
    category = category_factory.build()
    serializer = CategorySerializer(instance=category)

    expected_fields = ["id", "name"]
    assert set(serializer.data.keys()) == set(expected_fields)


@pytest.mark.unit
def test_category_serializer_data(category_factory):
    """Test CategorySerializer returns correct data"""
    category = category_factory.build(name="Technology")
    serializer = CategorySerializer(instance=category)
    data = serializer.data

    assert data["id"] == category.id
    assert data["name"] == "Technology"


@pytest.mark.unit
def test_category_serializer_read_only_id():
    """Test that id field is read-only"""
    serializer = CategorySerializer()
    assert serializer.fields["id"].read_only is True
    assert serializer.fields["name"].read_only is False
