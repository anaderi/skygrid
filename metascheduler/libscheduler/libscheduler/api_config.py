import random


class APIConfig(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)

        return cls._instance


a1 = Singleton(A)
a2 = Singleton(A)