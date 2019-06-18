from django import forms

class NumberFilter(forms.Form):
    lower_bound = forms.FloatField()
    upper_bound = forms.FloatField()
    equal = forms.FloatField()

class StringFilter(forms.Form):
    values = forms.CharField()


class DateFilter(forms.Form):
    start = forms.DateField()
    end = forms.DateField()