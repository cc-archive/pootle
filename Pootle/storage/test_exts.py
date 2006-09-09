"""Unit tests for Pootle.storage.exts."""

def test_AnnotationProperty():
    """
        >>> from Pootle.storage.exts import AnnotationProperty

        >>> class SomeObject(object):
        ...     foo = AnnotationProperty('foo')
        ...     def __init__(self):
        ...         self.annotations = {}

    At first the property is not set:

        >>> obj = SomeObject()
        >>> obj.foo
        Traceback (most recent call last):
            ...
        KeyError: 'foo'

    We can set the property:

        >>> obj.foo = 'bar'

    Now we can see the value:

        >>> obj.annotations
        {'foo': 'bar'}
        >>> obj.foo
        'bar'

    """
