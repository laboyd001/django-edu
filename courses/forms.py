from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

ModuleFormSet = inlineformset_factory(Course,
                                     Module,
                                    # fields included in each formset
                                     fields=['title',
                                             'description'],
                                    # number of empty extra forms to display
                                     extra=2,
                                    # boolean field rendered as checkbox for marking
                                    # objects you want to delete
                                     can_delete=True)