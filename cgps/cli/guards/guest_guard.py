from functools import wraps


def guest():
    def deco(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if self._auth_service.verify_login():
                print(f"You are already logged in as {self._auth_service.username}, please logout first")
                return
            return fn(self, *args, **kwargs)
        return wrapper
    return deco
