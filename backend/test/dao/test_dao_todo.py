import pytest
from src.util.dao import DAO
import pymongo


# includes the required property
valid_obj_1 = {
    "description": "It's a unique description.",
    "done": True
}

# includes required property with repeated description
valid_obj_2 = {
    "description": "It's a unique description."
}

# missing required property
invalid_obj_1 = {
    "lastName": "lastname"
}

# includes required property and one that
# is not listed in the validator
invalid_obj_2 = {
    "description": "It's a description.",
    "name": "Firstname Lastname"
}

# property is of wrong type
invalid_obj_3 = {
    "url": True

}

@pytest.fixture(scope='function', params=['todo'])
def test_dao():
    """
        Fixture providing a DAO instance for performing
        database operations on the specified MongoDB collection.
    """
    client = pymongo.MongoClient('mongodb://localhost:27017')
    dao = DAO('todo')

    yield dao

    client.close()
    dao.drop()

@pytest.mark.integration
@pytest.mark.parametrize('new_obj', [
    (valid_obj_1),
    (valid_obj_2),
    ])
def test_todo_create_valid_returns_same_object(test_dao, new_obj):
    """
        Tests valid scenarios when the
        new object is registered to the database.
        Should return newly created object.
    """
    dao = test_dao
    res = dao.create(new_obj)
    res.pop('_id')
    assert res == new_obj

@pytest.mark.integration
@pytest.mark.parametrize('new_obj', [
    (invalid_obj_1),
    (invalid_obj_2),
    (invalid_obj_3)
    ])
def test_todo_invalid_obj_raise_error(test_dao, new_obj):
    """
        Tests create object with invalid object,
        Should raise WriteError.
    """
    dao = test_dao
    with pytest.raises(pymongo.errors.WriteError):
            dao.create(new_obj)
                     
# @pytest.mark.integration
# @pytest.mark.parametrize('new_obj', [
#     (valid_obj_1),
#     (valid_obj_2)
#     ])
# def test_todo_create_valid_obj(test_dao, new_obj):
#     """
#         Tests create object with valid object,
#         Object should be created.
#     """
#     dao = test_dao
#     assert dao.create(new_obj)

@pytest.mark.integration
@pytest.mark.parametrize('new_obj', [
    (invalid_obj_1),
    (invalid_obj_2),
    (invalid_obj_3)
    ])
def test_todo_not_create_invalid_obj(test_dao, new_obj):
    """
        Tests create object with invalid object,
        Object should not be created.
    """
    dao = test_dao
    try:
        dao.create(new_obj)
    except:
        pass

    count_invalid_objs = dao.collection.count_documents(new_obj)
    print(count_invalid_objs)
    assert count_invalid_objs == 0

@pytest.mark.integration
def test_todo_create_dup_raise_error(test_dao):
    """
    Tests create object with duplicate unique property,
    WriteError should be raised
    """
    dao = test_dao

    dao.create(valid_obj_2)

    with pytest.raises(pymongo.errors.WriteError):
       dao.create(valid_obj_2)


@pytest.mark.integration
def test_create_not_dup(test_dao):
    """
    Tests create object with duplicate unique property,
    duplicate object should not be created.
    """
    dao = test_dao

    dao.create(valid_obj_2)
    
    try:
        dao.create(valid_obj_2)
    except:
        pass

    count_users = dao.collection.count_documents(valid_obj_2)
    assert count_users == 1
