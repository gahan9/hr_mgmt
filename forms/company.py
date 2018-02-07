# from dal import autocomplete
# from django import forms
#
# from employee.models import QuestionDB
#
#
# class PersonForm(forms.ModelForm):
#     birth_country = forms.ModelChoiceField(
#         queryset=QuestionDB.objects.all(),
#         widget=autocomplete.ModelSelect2(url='country-autocomplete')
#     )
#
#     class Meta:
#         model = QuestionDB
#         fields = ('__all__', )
