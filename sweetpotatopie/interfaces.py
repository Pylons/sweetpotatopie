from zope.interface import Interface

class IParser(Interface):
    """ Convert a text specification to a schema.
    """
    def __call__(text):
        """ Parse 'text' as YAML, returning a schema.
        """


