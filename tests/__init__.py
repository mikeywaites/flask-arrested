import arrested


class UserResource(arrested.ApiResource):

    @arrested.register_hook('track_foo_user', on=arrested.BEFORE_HOOK)
    def track_foo(self):

        print 'foo'


if __name__ == "__main__":

    user = UserResource()
    user.get()
