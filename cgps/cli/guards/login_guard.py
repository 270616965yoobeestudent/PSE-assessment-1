from functools import wraps


def logged_in():
    def deco(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if not self._auth_service.verify_login():
                print("You are not logged in, please login first")
                return
            id = self._auth_service.id
            kwargs.setdefault('user_id', id)
            return fn(self, *args, **kwargs,)
        return wrapper
    return deco
