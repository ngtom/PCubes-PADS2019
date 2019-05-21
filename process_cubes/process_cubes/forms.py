from django import forms
from import_xes.models import ProcessCube

class CubeForm(forms.ModelForm):

    class Meta:
        model = ProcessCube
        fields = ('name',)