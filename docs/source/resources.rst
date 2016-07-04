Resources
=================

Resources are classes that proivide specific handling for certain HTTP requests.


ListbableResource
~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`arrested.api.ListableResource` provides handling for GET requests.  It typically serializes a collection of objects
and returns to the user.

ListableResources are used in conjunction with :class:`arrested.api.Api` classes and other Resources to define endpoints.

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.api import ListableResource

    class UserIndexApi(Api, ListableResource):
        url = '/users'
        endpoint_name = 'users.index'
        response_handler = MyResponseHandler
        methods = ['GET', ]

        def get_objects(self):
            return get_users()


Classes using :class:`.ListableResource` must implement the ``get_objects`` method.  A ``response_handler`` is also required to handle
GET requests using the :class:`.ListableResource` resource.

:meth:`.ListableResource.get_objects` can return anything that can be handled by your ``response_handler`` IE a list of dict or a list of SQlAlchemy models, it's up to your selected response_handler
to handle the data returned form ``get_objects``.


.. sourcecode:: python

    def get_objects(self):
        stmt = db.session.query(User) \
            .filter(User.is_active == true()) \
            .order_by(User.name.desc())

        return stmt.all()


.. seealso::
    :class:`.ListableResource`

    :ref:`handlers`


CreateableResource
~~~~~~~~~~~~~~~~~~~~~~~~~
:class:`.CreateableResource` provides handling for POST requests.  It typically marshals data and then creates a new object.  CreateableResource will then serialize and return the newly createed.

AS :class:`.CreateableResource` both marshals and serializes data it must define a ``request_handler`` and a ``response_handler``.

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.api import BaseCreatebaleResource

    class UserIndexApi(Api, BaseCreatebaleResource):
        url = '/users'
        endpoint_name = 'users.index'
        response_handler = MyResponseHandler
        request_handler = MyRequestHandler
        methods = ['GET', 'POST']


Additonally classes using :class:`.CreateableResource` must also implement the ``save_object`` method.

.. sourcecode:: python

    def save_object(self):

        db.session.add(self.request.data)
        db.session.commit()

.. seealso::
    :class:`.CreateableResource`

    :ref:`handlers`


ObjectResource
~~~~~~~~~~~~~~~~~~~~~~~~~
:class:`arrested.api.ObjectResource` provides handling for GET requests.  It typically serializes a single object.

ObjectResources are used in conjunction with :class:`arrested.api.Api` classes and other Resources to define endpoints.

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.api import ObjectResource

    class UserIndexApi(Api, ObjectResource):
        url = '/users/<string:obj_id>'
        endpoint_name = 'users.object'
        response_handler = MyResponseHandler
        methods = ['GET', ]

        def get_objects(self):
            return get_users()


Classes using :class:`.ObjectResource` must implement the ``get_object`` method.  A ``response_handler`` is also required to handle
GET requests.

:meth:`.ObjectResource.get_object` can return anything that can be handled by your ``response_handler`` IE a dict or a SQlAlchemy model, it's up to your selected response_handler
to handle the data returned from ``get_objects``.


.. sourcecode:: python

    def get_object(self):
        stmt = db.session.query(User) \
            .filter(User.is_active == true()) \
            .filter(User.id == self.kwargs['id']) \

        return stmt.one_or_none()


.. seealso::
    :class:`.ObjectResource`

    :ref:`handlers`


UpdateableResource
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. seealso::
    :class:`.UpdateableResource`

    :ref:`handlers`


PatchableResource
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. seealso::
    :class:`.PatchableResource`

    :ref:`handlers`

DeleteableResource
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. seealso::
    :class:`.DeleteableResource`

    :ref:`handlers`
