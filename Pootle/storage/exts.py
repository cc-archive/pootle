"""Extension support."""


class AnnotationProperty(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, type=None):
        return instance.annotations[self.name]

    def __set__(self, instance, value):
        assert isinstance(value, basestring)
        instance.annotations[self.name] = value

