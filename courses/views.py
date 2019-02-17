from django.urls import reverse_lazy
from django.views.generic.list import ListView
from djnago.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Course


class ManageCourseListView(ListView):
    '''inherits from django's generic ListView to get the list of
        courses only the current user has access to edit, delete, update
    
    Arguments:
        ListView  -- [generic django class]
    
    Returns:
        [queryset] -- [prevents users from editing, updating, or deleting courses they didnt't create]
    '''

    model = Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        '''overriding the get_queryset method
        
        Returns:
            [courses] -- [only those created by the current user]
        '''

        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerMixin(object):
    '''this class can be used for views that interact with any model that contains the owner attribute.
    '''

    def get_queryset(self):
        '''get the base queryset
        
        Returns:
            filters objects by the owner to retrieve objects that belong to the current user
        '''

        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        '''anytime we use a form we are going to set the owner to the current user
        '''

        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(OwnerMixin):
    '''inherits OwnerMixin and provides the Course model for querysets
    '''

    model = Course


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    '''use the model fields to build the forms CreateView and UpdateView
      success_url used by CreateView and UpdateView to redirect user after successful form submission
    '''

    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_coure_list')
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    '''lists the courses created by the user
    '''

    template_name = 'courses/manage/course/list.html'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    '''uses a modelform to create a new course object, uses the fields from OwnerCourseEditMixin to build a model form and subclasses CreateView
    '''

    pass


class CoureUpdateView(OwnerCourseEditMixin, UpdateView):
    '''allows editing an existing course object.  Inherits from OwnerCourseEditMixin and UpdateView
    '''

    pass


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    '''inherits from OwnerCourseMixin and generic DeleteView.  Defines success url for redirect
    '''

    template_name = 'course/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')


