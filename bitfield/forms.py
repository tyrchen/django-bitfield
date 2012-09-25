from django.forms import CheckboxSelectMultiple, IntegerField, ValidationError
from django.utils.encoding import force_unicode

from .types import BitHandler


class BitFieldCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if not choices and getattr(value, 'keys', None):
            choices = tuple(value.iteritems())
        if isinstance(value, BitHandler):
            value = [k for k, v in value if v]
        return super(BitFieldCheckboxSelectMultiple, self).render(
          name, value, attrs=attrs, choices=choices)


    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if initial != data:
            return True
        initial_set = set([force_unicode(value) for value in initial])
        data_set = set([force_unicode(value) for value in data])
        return data_set != initial_set


class BitFormField(IntegerField):
    """
    'choices' should be a flat list of flags (just as BitField
    accepts them).
    """
    def __init__(self, choices=(), widget=BitFieldCheckboxSelectMultiple, *args, **kwargs):
        self.widget = widget
        self.choices = self.widget.choices = choices
        super(BitFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value:
            return 0

        if isinstance(value, int):
            result = BitHandler(value, [k for k, v in self.choices])
        else:
            result = BitHandler(0, [k for k, v in self.choices])
            for k in value:
                try:
                    setattr(result, str(k), True)
                except AttributeError:
                    raise ValidationError('Unknown choice: %r' % str(k))
        return int(result)
