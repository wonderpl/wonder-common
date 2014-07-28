import wtforms
from .i18n import lazy_gettext as _


def email_validator():
    # Additional address validation for SES - doesn't like foo@bar.com. or foo@bar..com
    def _valid(form, field):
        if not field.data:
            return
        if field.data.endswith('.') or ' ' in field.data or '..' in field.data.rsplit('@', 1)[-1]:
            raise wtforms.ValidationError(_('Invalid email address.'))
    return _valid
