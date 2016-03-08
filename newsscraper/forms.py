from django import forms
from djng.forms import NgModelFormMixin, NgForm

NEWS_SITE_CHOICES = (
    ("standaard", "De Standaard"),
    ("hln", "Het Laatste Nieuws"),
    ("dm", "De Morgen"),
)


class NewssiteArchiveSearchForm(NgModelFormMixin, NgForm):
    news_site = forms.MultipleChoiceField(label='News site', required=True, widget=forms.Select, choices=NEWS_SITE_CHOICES)
    search_term = forms.CharField(label='Search term')
    start_date = forms.DateField(label='Start date', widget=forms.DateInput)
    end_date = forms.DateField(label='End Date', widget=forms.DateInput)
