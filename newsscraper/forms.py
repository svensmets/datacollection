from django import forms
from djng.forms import NgFormValidationMixin, NgForm
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from functools import partial

# add the angular datepicker to the date field
DateInput = partial(forms.DateInput, {'jqdatepicker': '', 'min': 'minDate', 'max': 'maxDate'})
SelectInput = partial(forms.Select, {'ng-change': 'changed()'})

class NewssiteArchiveSearchForm(NgFormValidationMixin, NgForm, Bootstrap3FormMixin):
    search_term = forms.CharField(label='Search term', required=True)
    start_date = forms.DateField(label='Start date', widget=DateInput())
    end_date = forms.DateField(label='End Date', widget=DateInput())
