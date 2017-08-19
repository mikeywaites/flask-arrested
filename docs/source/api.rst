.. _api:

Developer Interface
===================

.. module:: arrested

This part of the documentation covers all the interfaces of Arrested.


API
------------------

.. autoclass:: arrested.api.ArrestedAPI
   :members:
   :inherited-members:


Resource
------------------

.. autoclass:: arrested.resource.Resource
   :members:


Endpoint
------------------

.. autoclass:: arrested.endpoint.Endpoint
   :members:
   :inherited-members:


Mixins
------------------

.. autoclass:: arrested.mixins.GetListMixin
   :members:

.. autoclass:: arrested.mixins.CreateMixin
   :members:

.. autoclass:: arrested.mixins.ObjectMixin
   :members:

.. autoclass:: arrested.mixins.GetObjectMixin
   :members:

.. autoclass:: arrested.mixins.PutObjectMixin
   :members:

.. autoclass:: arrested.mixins.PatchObjectMixin
   :members:

.. autoclass:: arrested.mixins.DeleteObjectMixin
   :members:


Handlers
------------------

.. autoclass:: arrested.handlers.Handler
   :members:

.. autoclass:: arrested.handlers.JSONResponseMixin
   :members:

.. autoclass:: arrested.handlers.JSONRequestMixin
   :members:

.. autoclass:: arrested.handlers.RequestHandler
   :members:

.. autoclass:: arrested.handlers.ResponseHandler
   :members:


Exceptions
----------

.. autoexception:: arrested.exceptions.ArrestedException
