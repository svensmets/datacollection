from django import forms

#forms to look for profile information


class AddNamesForm(forms.Form):
    '''
    form to add names to list of twitter usernames the user wants to use for the search action
    '''
    name = forms.CharField(widget=forms.TextInput)


class NamesTextAreaForm(forms.Form):
    names = forms.CharField(widget=forms.Textarea(attrs={'rows': 20,'cols': 50}))


class SearchOptionsForm(forms.Form):
    PROFILE_INFORMATION_CHOICES = (
        ('1', 'Friends'),
        ('2', 'Followers'),
    )
    friends_count = forms.CharField(label='friends count', required=False, widget=forms.NumberInput(attrs={'min':1, 'max':10000000}))
    search_choices = forms.MultipleChoiceField(label="Search options", required=True, widget=forms.CheckboxSelectMultiple(), choices=PROFILE_INFORMATION_CHOICES )

