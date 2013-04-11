import unittest


class Test_configure_loader(unittest.TestCase):

    def _callFUT(self, loader):
        from sweetpotatopie.parsers import configure_loader
        return configure_loader(loader)

    def test_constructors_registered_only_on_loader_instance(self):
        from yaml import Loader
        from .._compat import StringIO
        loader = self._callFUT(Loader(StringIO()))
        for name in [
            '!field.string',
            '!field.integer',
            '!field.float',
            '!field.decimal',
            '!field.boolean',
            '!field.datetime',
            '!field.date',
            '!field.tuple',
            '!field.sequence',
            '!field.mapping',
            '!validator.function',
            '!validator.regex',
            '!validator.email',
            '!validator.range',
            '!validator.length',
            '!validator.one_of',
            '!validator.all',
            '!schema',
            ]:
            # *Don't* populate the class-level registry, only the instance.
            self.assertFalse(name in Loader.yaml_constructors)
            self.failUnless(name in loader.yaml_constructors)


class SchemaParserTests(unittest.TestCase):

    def _getTargetClass(self):
        from sweetpotatopie.parsers import SchemaParser
        return SchemaParser

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IParser(self):
        from zope.interface.verify import verifyClass
        from sweetpotatopie.parsers import IParser
        verifyClass(IParser, self._getTargetClass())

    def test_instance_conforms_to_IParser(self):
        from zope.interface.verify import verifyObject
        from sweetpotatopie.parsers import IParser
        verifyObject(IParser, self._makeOne())

    def test_optional_string_field(self):
        import colander
        PATTERN = r"\d\d\d-\d\d\d-\d\d\d\d"
        TEXT = '\n'.join([
            "!field.string",
            "  name : phone",
            "  missing : ''",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 0)
        self.failUnless(isinstance(schema.typ, colander.String))
        self.assertEqual(schema.name, 'phone')
        self.assertEqual(schema.missing, '')

    def test_string_field_with_regex_validator(self):
        import colander
        PATTERN = r"\d\d\d-\d\d\d-\d\d\d\d"
        TEXT = '\n'.join([
            "!field.string",
            "  name : phone",
            "  validator : !validator.regex ",
            "    regex: %s" % PATTERN,
            "    msg: Invalid phone number",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 0)
        self.failUnless(isinstance(schema.typ, colander.String))
        self.assertEqual(schema.name, 'phone')
        validator = schema.validator
        self.failUnless(isinstance(validator, colander.Regex))
        self.assertEqual(validator.match_object.pattern, PATTERN)
        self.assertEqual(validator.msg, 'Invalid phone number')

    def test_string_field_with_email_validator(self):
        import colander
        TEXT = '\n'.join([
            "!field.string",
            "  name : phone",
            "  validator : !validator.email ",
            "    msg: Invalid email",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 0)
        self.failUnless(isinstance(schema.typ, colander.String))
        self.assertEqual(schema.name, 'phone')
        validator = schema.validator
        self.failUnless(isinstance(validator, colander.Email))
        self.assertEqual(validator.msg, 'Invalid email')

    def test_string_field_with_length_validator(self):
        import colander
        TEXT = '\n'.join([
            "!field.string",
            "  name : favorites",
            "  validator : !validator.length",
            "    min: 0",
            "    max: 4",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 0)
        self.failUnless(isinstance(schema.typ, colander.String))
        self.assertEqual(schema.name, 'favorites')
        validator = schema.validator
        self.failUnless(isinstance(validator, colander.Length))
        self.assertEqual(validator.min, 0)
        self.assertEqual(validator.max, 4)

    def test_string_field_with_choices(self):
        import colander
        PATTERN = r"\w*"
        TEXT = '\n'.join([
            "!field.string",
            "  name : favorite_color",
            "  validator : !validator.one_of",
            "    choices :",
            "      - red",
            "      - blue",
            "      - green",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 0)
        self.failUnless(isinstance(schema.typ, colander.String))
        self.assertEqual(schema.name, 'favorite_color')
        validator = schema.validator
        self.failUnless(isinstance(validator, colander.OneOf))
        choices = validator.choices
        self.assertEqual(list(choices), ['red', 'blue', 'green'])

    def test_string_field_with_both_regex_and_length_validators(self):
        import colander
        PATTERN = r"\w*"
        TEXT = '\n'.join([
            "!field.string",
            "  name : passcode",
            "  validator : !validator.all",
            "    validators : ",
            "      - !validator.regex ",
            "         regex: %s" % PATTERN,
            "      - !validator.length",
            "         min: 8",
            "         max: 14",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 0)
        self.failUnless(isinstance(schema.typ, colander.String))
        self.assertEqual(schema.name, 'passcode')
        validator = schema.validator
        self.failUnless(isinstance(validator, colander.All))
        regex, length = validator.validators
        self.failUnless(isinstance(regex, colander.Regex))
        self.assertEqual(regex.match_object.pattern, PATTERN)
        self.failUnless(isinstance(length, colander.Length))
        self.assertEqual(length.min, 8)
        self.assertEqual(length.max, 14)

    def test_integer_field_with_range_validator(self):
        import colander
        TEXT = '\n'.join([
            "!schema",
            " children: ",
            "  - !field.integer",
            "    name : rating",
            "    validator : !validator.range",
            "      min: 1",
            "      max: 5",
            "      min_err: Rating must be >= 1",
            "      max_err: Rating must be <= 5",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 1)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(schema.children[0].name, 'rating')
        self.failUnless(isinstance(schema.children[0].typ, colander.Integer))
        validator = schema.children[0].validator
        self.failUnless(isinstance(validator, colander.Range))
        self.assertEqual(validator.min, 1)
        self.assertEqual(validator.max, 5)
        self.assertEqual(validator.min_err, "Rating must be >= 1")
        self.assertEqual(validator.max_err, "Rating must be <= 5")

    def test_float_field_with_function_validator(self):
        import colander
        global dummy
        def dummy(*args, **kw):
            """ """
        TEXT = '\n'.join([
            "!schema",
            " children:",
            "  - !field.float",
            "    name : temperature",
            "    validator : !validator.function",
            "      function: !!python/name:sweetpotatopie.tests.test_parsers.dummy",
            "      message: Too darn hot!",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 1)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(schema.children[0].name, 'temperature')
        self.failUnless(isinstance(schema.children[0].typ, colander.Float))
        validator = schema.children[0].validator
        self.failUnless(isinstance(validator, colander.Function))
        self.failUnless(validator.function is dummy)
        self.assertEqual(validator.message, "Too darn hot!")

    def test_decimal_field(self):
        import colander
        TEXT = '\n'.join([
            "!schema",
            " children:",
            "  - !field.decimal",
            "    name : price",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 1)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(schema.children[0].name, 'price')
        self.failUnless(isinstance(schema.children[0].typ, colander.Decimal))

    def test_boolean_field(self):
        import colander
        TEXT = '\n'.join([
            "!schema",
            " children:",
            "  - !field.boolean",
            "    name : member",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 1)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(schema.children[0].name, 'member')
        self.failUnless(isinstance(schema.children[0].typ, colander.Boolean))

    def test_datetime_field(self):
        import colander
        TEXT = '\n'.join([
            "!schema",
            " children:",
            "  - !field.datetime",
            "    name : expires",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 1)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(schema.children[0].name, 'expires')
        self.failUnless(isinstance(schema.children[0].typ, colander.DateTime))

    def test_date_field(self):
        import colander
        TEXT = '\n'.join([
            "!schema",
            " children:",
            "  - !field.date",
            "    name : joined",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.assertEqual(len(schema.children), 1)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(schema.children[0].name, 'joined')
        self.failUnless(isinstance(schema.children[0].typ, colander.Date))

    def test_date_field_with_custom_class_validator(self):
        import colander
        import datetime
        global Zorba
        class Zorba(object):
            """ Forbid setting a date value to a particular day of the week.
            """
            SUNDAY = 6
            never_on = SUNDAY
            msg = 'Never on a Sunday'

            def __call__(self, node, value):
                if value.weekday() == self.never_on:
                    raise colander.Invalid(node, self.msg)
        TEXT = '\n'.join([
            "!schema",
            " children:",
            "  - !field.date",
            "    name : when",
            "    validator: !!python/object:sweetpotatopie.tests.test_parsers.Zorba",
            "      never_on: 5",
            "      msg: No plane on Saturday!",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(len(schema.children), 1)
        when = schema.children[0]
        self.assertEqual(when.name, 'when')
        self.failUnless(isinstance(when.typ, colander.Date))
        validator = when.validator
        self.failUnless(isinstance(validator, Zorba))
        self.assertEqual(validator.never_on, 5)
        self.assertEqual(validator.msg, "No plane on Saturday!")
        self.assertRaises(colander.Invalid, validator, None,
                          datetime.date(1,1,6))

    def test_date_field_with_custom_factory_validator(self):
        from datetime import date
        import colander
        global zorba
        SUNDAY = 6
        def zorba(never_on=SUNDAY, msg = 'Never on a Sunday'):
            def _zorba(node, value):
                if value.weekday() == never_on:
                    raise colander.Invalid(node, msg)
            return _zorba
        TEXT = '\n'.join([
            "!schema",
            " children:",
            "  - !field.date",
            "    name : when",
            "    validator: " +
                   "!!python/object/apply:sweetpotatopie.tests.test_parsers.zorba",
            "      kwds:",
            "        never_on: 0",
            "        msg: No plane on Monday!",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(len(schema.children), 1)
        when = schema.children[0]
        self.assertEqual(when.name, 'when')
        self.failUnless(isinstance(when.typ, colander.Date))
        validator = when.validator
        self.failUnless(isinstance(validator, type(zorba)))
        self.assertRaises(colander.Invalid, validator, object(),
                          date(2010, 8, 16))

    def test_multiple_fields(self):
        import colander
        TEXT = '\n'.join([
            "!schema",
            "  name: schema",
            "  children:",
            "   - !field.string",
            "     name : first_name",
            "   - !field.string",
            "     name : last_name",
            "   - !field.date",
            "     name : birth_date",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(len(schema.children), 3)
        self.assertEqual(schema.children[0].name, 'first_name')
        self.failUnless(isinstance(schema.children[0].typ, colander.String))
        self.assertEqual(schema.children[1].name, 'last_name')
        self.failUnless(isinstance(schema.children[1].typ, colander.String))
        self.assertEqual(schema.children[2].name, 'birth_date')
        self.failUnless(isinstance(schema.children[2].typ, colander.Date))

    def test_tuple_field(self):
        import colander
        TEXT = '\n'.join([
            "!field.tuple",
            "  name : statistics ",
            "  children : ",
            "    - !field.float ",
            "      name : min ",
            "    - !field.float ",
            "      name : max ",
            "    - !field.float ",
            "      name : mean ",
            "    - !field.float ",
            "      name : median ",
            "    - !field.float ",
            "      name : stddev ",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.failUnless(isinstance(schema.typ, colander.Tuple))
        self.assertEqual(schema.name, 'statistics')
        elements = schema.children
        self.assertEqual(len(elements), 5)
        for i, name in enumerate(('min', 'max', 'mean', 'median', 'stddev')):
            self.assertEqual(elements[i].name, name)
            self.assertEqual(elements[i].typ.__class__, colander.Float)

    def test_sequence_field(self):
        import colander
        TEXT = '\n'.join([
            "!field.sequence",
            "  name : contacts ",
            "  children : ",
            "    - !field.mapping",
            "        children : ",
            "        - !field.string ",
            "          name : nickname ",
            "        - !field.string ",
            "          name : phone",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.failUnless(isinstance(schema.typ, colander.Sequence))
        self.assertEqual(schema.name, 'contacts')
        self.failUnless(isinstance(schema.typ, colander.Sequence))
        children = schema.children
        self.assertEqual(len(children), 1)
        child = children[0]
        self.failUnless(isinstance(child.typ, colander.Mapping))
        self.assertEqual(len(child.children), 2)
        self.assertEqual(child.children[0].name, 'nickname')
        self.failUnless(isinstance(child.children[0].typ, colander.String))
        self.assertEqual(child.children[1].name, 'phone')
        self.failUnless(isinstance(child.children[1].typ, colander.String))

    def test_mapping_field(self):
        import colander
        TEXT = '\n'.join([
            "!field.mapping",
            "  name : statistics ",
            "  children : ",
            "    - !field.float ",
            "      name : min ",
            "    - !field.float ",
            "      name : max ",
            "    - !field.float ",
            "      name : mean ",
            "    - !field.float ",
            "      name : median ",
            "    - !field.float ",
            "      name : stddev ",
        ])
        parser = self._makeOne()
        schema = parser(TEXT)
        self.failUnless(isinstance(schema.typ, colander.Mapping))
        self.assertEqual(schema.name, 'statistics')
        elements = schema.children
        self.assertEqual(len(elements), 5)
        for i, name in enumerate(('min', 'max', 'mean', 'median', 'stddev')):
            self.assertEqual(elements[i].name, name)
            self.assertEqual(elements[i].typ.__class__, colander.Float)
