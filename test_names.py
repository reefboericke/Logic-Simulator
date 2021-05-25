"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["S1", "S2", "G1"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    my_name.lookup(name_string_list)
    return my_name


def test_query_raises_exceptions(used_names):
    """Test if query raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.lookup(1)
    with pytest.raises(TypeError):
        used_names.lookup(None)


def test_lookup_raises_exceptions(name_string_list, used_names):
    """Test if lookup raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.lookup(1)
    with pytest.raises(TypeError):
        used_names.lookup(None)
    with pytest.raises(TypeError):
        used_names.lookup(name_string_list.append(1))
    with pytest.raises(TypeError):
        used_names.lookup(name_string_list.append(None))


def test_get_name_string_raises_exceptions(used_names):
    """Test if get_name_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("name_string, expected_name_id", [
    ("S1", 0),
    ("S2", 1),
    ("G1", 2),
    ("G2", None)
])
def test_query(used_names, new_names, name_string, expected_name_id):
    """Test if query returns the expected string."""
    # name_string is present
    assert used_names.query(name_string) == expected_name_id
    # name_string is absent
    assert new_names.query(name_string) is None


@pytest.mark.parametrize("name_string_list, expected_name_id_list", [
    # name_strings are present
    (["S1", "S2", "G1"], [0, 1, 2]),
    # one name_string is absent
    (["S1", "S2", "G1", "G2"], [0, 1, 2, 3]),
    # repeated name_string
    (["S1", "S1"], [0, 0])
])
def test_lookup(used_names, name_string_list, expected_name_id_list):
    """Test if lookup returns the expected string."""
    assert used_names.lookup(name_string_list) == expected_name_id_list


@pytest.mark.parametrize("name_id, expected_name_string", [
    (0, "S1"),
    (1, "S2"),
    (2, "G1"),
    (3, None)
])
def test_get_name_string(used_names, new_names, name_id, expected_name_string):
    """Test if get_string returns the expected string."""
    # name_string is present
    assert used_names.get_name_string(name_id) == expected_name_string
    # name_string is absent
    assert new_names.get_name_string(name_id) is None
