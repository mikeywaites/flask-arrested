
__all__ = [
    'GetListMixin', 'CreateMixin', 'GetObjectMixin', 'PutObjectMixin',
    'PatchObjectMixin', 'DeleteObjectMixin', 'ObjectMixin'
]


class HTTPMixin(object):
    """
    """

    def _response(self, body, status):
        """
        """

        return (self.make_response(body, status=status))


class GetListMixin(HTTPMixin):
    """Base ListMixin class that defines the expected API for all ListMixins
    """

    def get_objects(self):
        """
        """

        raise NotImplementedError()

    def list_response(self, status=200):
        """Pull the processed data from the response_handler and return a response.

        :param status: The HTTP status code returned with the response

        .. seealso:
            :meth:`Endpoint.make_response`
            :meth:`Endpoint.handle_get_request`
        """

        return self._response(self.response.get_response_data(), status=status)

    def handle_get_request(self):
        """Handle incoming GET request to an Endpoint and return an
        array of results by calling :meth:`.GetListMixin.get_objects`.

        .. seealso::
            :meth:`GetListMixin.get_objects`
            :meth:`Endpoint.get`
        """
        self.objects = self.get_objects()
        self.response = self.get_response_handler()

        self.response.process(self.objects)

        return self.list_response()


class CreateMixin(HTTPMixin):
    """Base CreateMixin class that defines the expected API for all CreateMixins
    """

    def save_object(self, obj):
        """Called by :meth:`CreateMixin.handle_post_request` ater the incoming data has
        been marshalled by the RequestHandler.

        :param obj: The marhsaled object from RequestHandler.
        """
        return obj

    def create_response(self, status=201):
        """Generate a Response object for a POST request.  By default, the newly created
        object will be passed to the specified ResponseHandler and will be serialized
        as the response body.
        """
        self.response = self.get_response_handler()
        self.response.process(self.obj)

        return self._response(self.response.get_response_data(), status=status)

    def handle_post_request(self):
        """Handle incoming POST request to an Endpoint and marshal the request data
        via the specified RequestHandler.  :meth:`.CreateMixin.save_object`. is then
        called and must be implemented by mixins implementing this interfce.

        .. seealso::
            :meth:`CreateMixin.save_object`
            :meth:`Endpoint.post`
        """
        self.request = self.get_request_handler()
        self.obj = self.request.process().data

        self.save_object(self.obj)
        return self.create_response()


class ObjectMixin(object):
    """Mixin that provides an interface for working with single data objects
    """

    allow_none = False

    def get_object(self):
        """Called by :meth:`GetObjectMixin.handle_get_request`.  Concrete classes should
        implement this method and return object typically by id.

        :raises: NotImplementedError
        """
        raise NotImplementedError()

    def object_response(self, status=200):
        """Generic response generation for Endpoints that return a single
        serialized object.

        :param status: The HTTP status code returned with the response
        :returns: Response object
        """

        self.response = self.get_response_handler()
        self.response.process(self.obj)
        return self._response(self.response.get_response_data(), status=status)

    @property
    def obj(self):
        """Returns the value of :meth:`ObjectMixin.get_object` and sets a private
        property called _obj.  This property ensures the logic around allow_none
        is enforced across Endpoints using the Object interface.

        :raises: :class:`werkzeug.exceptions.BadRequest`
        :returns: The result of :meth:ObjectMixin.get_object`
        """
        if not getattr(self, '_obj', None):
            self._obj = self.get_object()
            if self._obj is None and not self.allow_none:
                self.return_error(404)

        return self._obj

    @obj.setter
    def obj(self, value):
        """Sets the value of the private _obj property.
        """
        self._obj = value


class GetObjectMixin(HTTPMixin, ObjectMixin):
    """Base GetObjectMixins class that defines the expected API for all GetObjectMixins
    """

    def handle_get_request(self):
        """Handle incoming GET request to an Endpoint and return a
        single object by calling :meth:`.GetListMixin.get_object`.

        .. seealso::
            :meth:`GetListMixin.get_objects`
            :meth:`Endpoint.get`
        """
        return self.object_response()


class PutObjectMixin(HTTPMixin, ObjectMixin):
    """Base PutObjectMixins class that defines the expected API for all PutObjectMixin
    """

    def put_request_response(self, status=200):
        """Pull the processed data from the response_handler and return a response.

        :param status: The HTTP status code returned with the response

        .. seealso:
            :meth:`ObjectMixin.object_response`
            :meth:`Endpoint.handle_put_request`
        """

        return self.object_response(status=status)

    def handle_put_request(self):
        """
        """
        obj = self.obj
        self.request = self.get_request_handler()
        self.request.process()

        self.update_object(obj)
        return self.put_request_response()

    def update_object(self, obj):
        """Called by :meth:`PutObjectMixin.handle_put_request` ater the incoming data has
        been marshalled by the RequestHandler.

        :param obj: The marhsaled object from RequestHandler.
        """
        return obj


class PatchObjectMixin(HTTPMixin, ObjectMixin):
    """Base PatchObjectMixin class that defines the expected API for all PatchObjectMixin
    """

    def patch_request_response(self, status=200):
        """Pull the processed data from the response_handler and return a response.

        :param status: The HTTP status code returned with the response

        .. seealso:
            :meth:`ObjectMixin.object_response`
            :meth:`Endpoint.handle_put_request`
        """

        return self.object_response(status=status)

    def handle_patch_request(self):
        """
        """
        obj = self.obj
        self.request = self.get_request_handler()
        self.request.process()

        self.patch_object(obj)
        return self.patch_request_response()

    def patch_object(self, obj):
        """Called by :meth:`PatchObjectMixin.handle_patch_request` ater the
        incoming data has been marshalled by the RequestHandler.

        :param obj: The marhsaled object from RequestHandler.
        """
        return obj


class DeleteObjectMixin(HTTPMixin, ObjectMixin):
    """Base DeletehObjecttMixin class that defines the expected API for
    all DeletehObjecttMixins.
    """

    def delete_request_response(self, status=204):
        """Pull the processed data from the response_handler and return a response.

        :param status: The HTTP status code returned with the response

        """
        return (self.make_response('', status=status))

    def handle_delete_request(self):
        """
        """
        self.delete_object(self.obj)
        return self.delete_request_response()

    def delete_object(self, obj):
        """Called by :meth:`DeleteObjectMixin.handle_delete_request`.

        :param obj: The marhsaled object being deleted.
        """
        return obj
