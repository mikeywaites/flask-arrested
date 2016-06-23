Resources
=================

Resources are classes that proivide specific handling for certain HTTP requests.


ListbableResource
~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`arrested.api.BaseListableResource` provides handling for GET requests.  It typically serializes a collection of objects
and returns to the user.

ListableResources are used in conjunction with :class:`arrested.api.Api` classes and other Resources to define endpoints.

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.api import BaseListableResource

    class UserIndexApi(Api, BaseListableResource):
        url = '/users'
        endpoint_name = 'users.index'
        response_handler = MyResponseHandler
        scopes = ['read:users', 'write:users']
        methods = ['GET', ]

        def get_objects(self):
            return get_users()


Classes using :class:`.BaseListableResource` must implement the ``get_objects`` method.  A ``response_handler`` is also required to handle
GET requests using the :class:`.BaseListableResource` resource.

:meth:`.BaseListableResource.get_objects` can return anything that can be handled by your ``response_handler`` IE a list of dict or a list of SQlAlchemy models, it's up to your selected response_handler
to handle the data returned form ``get_objects``.


.. sourcecode:: python

    def get_objects(self):
        stmt = db.session.query(User) \
            .filter(User.is_active == true()) \
            .order_by(User.name.desc())

        return stmt.all()


.. seealso::
    :class:`.BaseListableResource`

    :ref:`handlers`


CreateableResource
~~~~~~~~~~~~~~~~~~~~~~~~~
:class:`.BaseCreateableResource` provides handling for POST requests.  It typically marshals data and then creates a new object.  CreateableResource will then serialize and return the newly createed.

AS :class:`.BaseCreateableResource` both marshals and serializes data it must define a ``request_handler`` and a ``response_handler``.

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.api import BaseCreatebaleResource

    class UserIndexApi(Api, BaseCreatebaleResource):
        url = '/users'
        endpoint_name = 'users.index'
        response_handler = MyResponseHandler
        request_handler = MyRequestHandler
        scopes = ['read:users', 'write:users']
        methods = ['GET', 'POST']


Additonally classes using :class:`.BaseCreateableResource` must also implement the ``save_object`` method.

.. sourcecode:: python

    def save_object(self):

        db.session.add(self.request.data)
        db.session.commit()

.. seealso::
    :class:`.BaseCreateableResource`

    :ref:`handlers`


ObjectResource
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. seealso::
    :class:`.BaseObjectResource`

    :ref:`handlers`


UpdateableResource
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. seealso::
    :class:`.BaseUpdateableResource`

    :ref:`handlers`


PatchableResource
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. seealso::
    :class:`.BasePatchableResource`

    :ref:`handlers`

DeleteableResource
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. seealso::
    :class:`.BaseDeleteableResource`

    :ref:`handlers`
