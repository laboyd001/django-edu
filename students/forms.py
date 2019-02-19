from django import forms
from courses.models import Course


class CourseEnrollForm(forms.Form):
    '''form used for student enrollment
    '''

    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)