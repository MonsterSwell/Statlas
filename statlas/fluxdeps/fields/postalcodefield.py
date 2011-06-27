from django.db.models import CharField
from django.core import validators
from django.utils.translation import ugettext as _

class PostalcodeField(CharField):
    default_error_messages = {
        'invalid': _(u'Enter a valid postalcode.'),
    }
    default_validators = [validators.RegexValidator('[1-9][0-9]{3}[A-Z]{2}')]

    def __init__(self, *args, **kwargs):
        super(PostalcodeField, self).__init__(max_length=6, *args, **kwargs)

    def to_python(self, value):
        return value.replace(' ', '').upper()

    def widget_attrs(self, widget):
        """
            Set the maxlength of a postalcode is 6; but the user might add 
            a space between digits and alphas which we will remove during clean.
            Allow the user to add this space by having a maxlength of 7
    
            .. todo::
                Fix that django calls this function. Don't know why it doesnt :-/
        """
        return {'maxlength': 7}
