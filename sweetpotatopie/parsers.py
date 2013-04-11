import colander
import deform
import yaml
from zope.interface import implementer

from .interfaces import IParser
from ._compat import u

"""
   --- !schema
   name : myschema
   children :
     - !field.sequence
       name : statistics
       children :
         - !field.mapping
           name : submap
           children :
             - !field.float
               name : min
             - !field.float
               name : max
"""


def _typed_node(typ, mapping):
    type_args = mapping.pop('type_args', {})
    children = mapping.pop('children', [])
    return colander.SchemaNode(typ(**type_args), *children, **mapping)


def _field(field_type):
    def _nested(loader, node):
        mapping = loader.construct_mapping(node, deep=True)
        return _typed_node(field_type, mapping)
    return _nested


def _validator(klass):
    def _nested(loader, node):
        mapping = loader.construct_mapping(node, deep=True)
        return klass(**mapping)
    return _nested


def _one_of(loader, node):
    mapping = loader.construct_mapping(node, deep=True)
    choices = mapping.pop('choices')
    return colander.OneOf(choices, **mapping)


def _all(loader, node):
    mapping = loader.construct_mapping(node, deep=True)
    validators = mapping.pop('validators')
    return colander.All(*validators, **mapping)

def _widget(widget_type):
    def _nested(loader, node):
        mapping = loader.construct_mapping(node, deep=True)
        return widget_type(**mapping)
    return _nested


def configure_loader(loader):
    if 'yaml_constructors' not in loader.__dict__:
        loader.yaml_constructors = loader.yaml_constructors.copy()
    ctors = loader.yaml_constructors
    ctors[u('!field.string')] = _field(colander.String)
    ctors[u('!field.integer')] = _field(colander.Integer)
    ctors[u('!field.float')] = _field(colander.Float)
    ctors[u('!field.decimal')] = _field(colander.Decimal)
    ctors[u('!field.boolean')] = _field(colander.Boolean)
    ctors[u('!field.datetime')] = _field(colander.DateTime)
    ctors[u('!field.date')] = _field(colander.Date)
    ctors[u('!field.time')] = _field(colander.Time)
    ctors[u('!field.tuple')] = _field(colander.Tuple)
    ctors[u('!field.set')] = _field(colander.Set)
    ctors[u('!field.sequence')] = _field(colander.Sequence)
    ctors[u('!field.mapping')] = _field(colander.Mapping)
    ctors[u('!validator.function')] = _validator(colander.Function)
    ctors[u('!validator.regex')] = _validator(colander.Regex)
    ctors[u('!validator.email')] = _validator(colander.Email)
    ctors[u('!validator.range')] = _validator(colander.Range)
    ctors[u('!validator.length')] = _validator(colander.Length)
    ctors[u('!validator.one_of')] = _one_of
    ctors[u('!validator.all')] = _all
    ctors[u('!schema')] = _field(colander.Mapping)
    ctors[u('!widget.checkboxes')] = _widget(deform.widget.CheckboxChoiceWidget)
    ctors[u('!widget.radio')] = _widget(deform.widget.RadioChoiceWidget)
    ctors[u('!widget.richtext')] = _widget(deform.widget.RichTextWidget)
    ctors[u('!widget.select')] = _widget(deform.widget.SelectWidget)
    ctors[u('!widget.textarea')] = _widget(deform.widget.TextAreaWidget)
    return loader


@implementer(IParser)
class SchemaParser(object):
    """ Create a profile tree from a YAML text.

    See ../docs/declarative.rst for docs.
    """

    def __call__(self, text):
        """ See IParser.
        """
        loader = yaml.Loader(text)
        return configure_loader(loader).get_single_data()
