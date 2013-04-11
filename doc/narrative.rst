Declaring :mod:`Colander` Schemas via YAML
==========================================

Colander schemas can be defined in a `YAML <http://pyyaml.org/>`_ file
as a sequence of field objects, e.g.:

.. code-block: yaml

   !schema
     children:
       - !field.string
          name: first_name
       - !field.string
          name: last_name
       - !field.date
          name: birth_date


Schema Fields
-------------

Each :mod:`colandar` schema consists of a sequence of one or more nodes;
typically, each node corresponds to a single data element ("field").
Some nodes represent compound data values, such as sequences or mappings.


Scalar Field Types
++++++++++++++++++

:mod:`reward` defines YAML constructors which build
:class:`colander.SchemaNode` instances with the following "scalar" Colander
field types:

- :class:`colander.String`

- :class:`colander.Integer`

- :class:`colander.Float`

- :class:`colander.Decimal`

- :class:`colander.Boolean`

- :class:`colander.Datetime`

- :class:`colander.Date`

Each field in the YAML file can contain a nested YAML mapping for the
:class:`colander.SchemaNode` constructor arguments.  The ``name`` argument
is required for all fields:

.. code-block:: yaml

  !schema
    children:
      - !field.string
        name: title
      - !field.integer
        name: rating
      - !field.float
        name: weight
      - !field.decimal
        name: price
      - !field.boolean
        name: active
      - !field.datetime
        name: expires
      - !field.date
        name: joined


Compound Field Types
++++++++++++++++++++

:mod:`reward` defines YAML constructors which build
:class:`colander.SchemaNode` instances for the following "compound" Colander
field types:

- :class:`colander.Tuple`

- :class:`colander.Sequence`

- :class:`colander.Mapping`

Each field in the YAML file can contain a nested YAML mapping for the
:class:`colander.SchemaNode` constructor arguments.  As with scalar fields,
the ``name`` argument is required for all fields.

:class:`colander.Tuple` fields require one item in their ``elements``
argument per element of the corresponding tuple:

.. code-block:: yaml

   !schema
     children:
       - !field.tuple
         name : statistics
         children :
           - !field.float
             name : min
           - !field.float
             name : max
           - !field.float
             name : mean
           - !field.float
             name : median
           - !field.float
             name : stddev

:class:`colander.Sequence` fields require single child node, which defines
the schema for each item in the sequence:

.. code-block:: yaml

   !schema
     children:
       - !field.sequence
         name : contacts
         children :
           - !field.Mapping
             children:
             - !field.string
                name : nickname
             - !field.string
                name : phone

:class:`colander.Mapping` fields take a series of child nodes, each defining
the schema for a the value corresponding to the ``name`` of the node.

.. code-block:: yaml

   !schema
     children:
       - !field.mapping",
         name : statistics
         children :
           - !field.float
             name : min
           - !field.float
             name : max
           - !field.float
             name : mean
           - !field.float
             name : median
           - !field.float
             name : stddev


Configuring Field Metadata
++++++++++++++++++++++++++

The ``title`` and ``descritpion`` values might be used by form-generation
machinery to generated a label and help text for the form field:

.. code-block:: yaml

   !schema
     children:
       - !field.string
         name: first_name
         title: First Name
         description:  The person's given name(s), including middle initial or name.

.. TODO:

   ``default``
   ``missing``

Validators
----------

:mod:`reward` defines YAML constructors for the following validators:

- :class:`colander.Regex`

- :class:`colander.Email`

- :class:`colander.Range`

- :class:`colander.Length`

- :class:`colander.OneOf`

- :class:`colander.All`

- :class:`colander.Function`


Configuring Validators
++++++++++++++++++++++

The built-in validators can be configured directly using YAML.  E.g., to
configure a regular expression validator for a telephone number:

.. code-block:: yaml

   !schema
     children:
      - !field.string
        name: phone
        validator: !validator.regex
           regex: \d\d\d-\d\d\d-\d\d\d\d
           msg: Please supply area code and telephone number

or to configure a range validator for an integer field:

.. code-block:: yaml

   !schema
     children:
      - !field.integer
        name: rating
        validator: !validator.range
           min: 1
           max: 5
           min_err: Rating must be >= 1
           max_err: Rating must be <= 5

The :class:`colander.OneOf` validator allows you to specify a set of
allowed values for a field:

.. code-block:: yaml

   !schema
     children:
       !field.string
         name : favorite_color
         validator : !validator.one_of
           choices :
             - red
             - blue
             - green

You can combine multiple valdators using :class:`colander.All`:

.. code-block:: yaml

   !schema
     children:
       !field.string
         name : passcode
         validator : !validator.all
           validators :
             - !validator.regex
                regex: \w
             - !validator.length
                min: 8
                max: 14

The :class:`colander.Function` validator can be configured using the
YAML ``!!python/name`` constructor, which resolves the dotted name:

.. code-block:: yaml

   !schema
     children:
      - !field.float
          name : temperature
          validator : !validator.function
            function: !!python/name:your.package.validate_temp
            message: Too darn hot!

Custom Validators
+++++++++++++++++

You may write custom validator which takes parameters from the configuration
as a class:

.. code-block:: python

   from colander import Invalid

   class Zorba(object):
       """ Forbid setting a date value to a particular day of the week.
       """
       SUNDAY = 6
       never_on = SUNDAY
       msg = 'Never on a Sunday'

       def __call__(self, node, value):
           if value.weekday() == self.never_on:
               raise Invalid(node, self.msg)

Such class-based validators can be configured in YAML using the
``!!python/object`` constructor, passing the attributes to be overridden:

.. code-block:: yaml

   !schema
     children:
      - !field.date
        name: when
        validator: !!python/object
           # 6 is datetime module's version of Sunday
           never_on : 6
           msg : No fun on Sundays!

You may also write a configurable validator as a factory function:

.. code-block:: python

   from colander import Invalid
   SUNDAY = 6

   def zorba(never_on=SUNDAY, msg='Never on a Sunday'):
       """ Forbid setting a date value to a particular day of the week.
       """
       def _zorba(node, value):
           if value.weekday() == never_on:
               raise Invalid(node, msg)
       return _zorba

Such factory-based validators can be configured in YAML using the
``!!python/object/apply`` constructor:

.. code-block:: yaml

   !schema
     children:
      - !field.date
        name: when
        validator: !!python/object/apply:package.module.zorba
           kwds:
             # 6 is datetime module's version of Sunday
             never_on : 6
             msg : No fun on Sundays!
