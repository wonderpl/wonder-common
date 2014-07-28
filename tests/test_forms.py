import unittest
from wonder.common.forms import email_validator


class FormsTestCase(unittest.TestCase):

    def test_email_validator(self):
        email = 'test@example.com.'
        field = type('Field', (object,), dict(data=email))()
        with self.assertRaises(ValueError):
            email_validator()(None, field)
