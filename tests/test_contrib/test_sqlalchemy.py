import pytest

from mock import patch, Mock
from flask_sqlalchemy import SQLAlchemy

from arrested import Endpoint
from arrested.exceptions import ArrestedException
from arrested.contrib.sql_alchemy import (
    DBMixin,
    DBListMixin,
    DBCreateMixin,
    DBObjectMixin
)


class Model(object):

    id = 'foo'
    name = 'foo'


def test_get_db_session(app):

    db = SQLAlchemy(app)
    assert DBMixin().get_db_session() == db.session


def test_db_list_mixin_requires_get_query(app):

    mixin = DBListMixin()
    with pytest.raises(NotImplementedError):
        mixin.get_query()


def test_db_list_mixin_get_objects(app):


    with patch.object(DBListMixin, 'get_query') as query_mock:
        query_mock.return_value.all.return_value = ['foo', 'bar']
        res = DBListMixin().get_objects()
        assert res == ['foo', 'bar']


def test_db_list_mixin_get_result(app):

    query_mock = Mock()
    query_mock.return_value.all.return_value = ['foo', 'bar']

    res = DBListMixin().get_result(query_mock.return_value)
    assert res == ['foo', 'bar']
    query_mock.return_value.all.assert_called_once()


def test_db_create_mixin_save_object(app):

    session_mock = Mock()
    fake = Mock()

    with patch.object(
        DBCreateMixin, 'get_db_session', return_value=session_mock) as get_session_mock:

        DBCreateMixin().save_object(fake)

        get_session_mock.assert_called_once()

        session_mock.add.assert_called_once_with(fake)
        session_mock.commit.assert_called_once()


def test_db_object_mixin_get_object(app):

    mixin = DBObjectMixin()
    mixin.kwargs = {'obj_id': 1}  # Simulate kwargs being set by an Endpoint class.
    mixin.model = Model
    query_mock = patch.object(DBObjectMixin, 'get_query')
    mock_query = query_mock.start()
    mock_query.return_value.filter.return_value.one_or_none.return_value = 'foo'

    res = mixin.get_object()

    assert res == 'foo'

    query_mock.stop()


def test_db_object_mixin_get_result(app):

    mock_query = Mock()
    mock_query.return_value.one_or_none.return_value = 'foo'
    mixin = DBObjectMixin()
    mixin.kwargs = {'obj_id': 1}  # Simulate kwargs being set by an Endpoint class.

    res = mixin.get_result(mock_query.return_value)

    assert res == 'foo'
    mock_query.return_value.one_or_none.assert_called_once()


def test_db_object_mixin_filter_by_id_model_must_be_set(app):

    mock_query = Mock()
    mixin = DBObjectMixin()
    mixin.kwargs = {'obj_id': 1}  # Simulate kwargs being set by an Endpoint class.

    with pytest.raises(ArrestedException):
        mixin.filter_by_id(mock_query.return_value)


def test_db_object_mixin_filter_by_id_invalid_id_field(app):

    mock_query = Mock()
    mixin = DBObjectMixin()
    mixin.model = Model
    mixin.model_id_param = 'bar'
    mixin.kwargs = {'obj_id': 1}  # Simulate kwargs being set by an Endpoint class.

    with pytest.raises(ArrestedException):
        mixin.filter_by_id(mock_query.return_value)



def test_db_object_mixin_filter_by_id(app):

    mock_query = Mock()
    mixin = DBObjectMixin()
    mixin.model = Model
    mixin.kwargs = {'obj_id': 1}  # Simulate kwargs being set by an Endpoint class.

    mixin.filter_by_id(mock_query.return_value)

    params = (Model.id == 1)
    mock_query.return_value.filter.assert_called_once_with(params)


def test_db_update_mixin_update_object(app):

    session_mock = Mock()
    fake = Mock()

    with patch.object(
        DBObjectMixin, 'get_db_session', return_value=session_mock) as get_session_mock:

        DBObjectMixin().update_object(fake)

        get_session_mock.assert_called_once()

        session_mock.add.assert_called_once_with(fake)
        session_mock.commit.assert_called_once()


def test_db_delete_mixin_delete_object(app):

    session_mock = Mock()
    fake = Mock()

    with patch.object(
        DBObjectMixin, 'get_db_session', return_value=session_mock) as get_session_mock:

        DBObjectMixin().delete_object(fake)

        get_session_mock.assert_called_once()

        session_mock.delete.assert_called_once_with(fake)
        session_mock.commit.assert_called_once()


def test_db_mixins_mro(app):

    class IndexApi(Endpoint, DBListMixin, DBCreateMixin):
        pass


    class ObjectApi(Endpoint, DBObjectMixin):
        pass
