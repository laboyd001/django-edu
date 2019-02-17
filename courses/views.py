from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View


from .models import Course
from .forms import ModuleFormSet


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


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    '''inherits OwnerMixin and provides the Course model for querysets
    '''

    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    '''use the model fields to build the forms CreateView and UpdateView
      success_url used by CreateView and UpdateView to redirect user after successful form submission
    '''

    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    '''lists the courses created by the user
    '''

    template_name = 'courses/manage/course/list.html'


class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    '''uses a modelform to create a new course object, uses the fields from OwnerCourseEditMixin to build a model form and subclasses CreateView
    '''

    permission_required = 'courses.add_course'


class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
    '''allows editing an existing course object.  Inherits from OwnerCourseEditMixin and UpdateView
    '''

    permission_required = 'courses.change_course'


class CourseDeleteView(PermissionRequiredMixin, 
                       OwnerCourseMixin, 
                       DeleteView):
    '''inherits from OwnerCourseMixin and generic DeleteView.  Defines success url for redirect
    '''

    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    '''handles the formset to add, update, and delete modules for a specific course.  this views inherits from mixins and views

    args:
    TemplateResponseMixin -- takes charge of rendering templates and returning HTTP response
    View -- basic class based view provided by Django
    '''

    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        '''avoids repeating the code to build the formset
        '''

        return ModuleFormSet (instance=self.course,
                                            data=data)

    def dispatch(self, request, pk):
        '''takes HTTP request, delegates to lowercase method either get or post
        '''

        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super(CourseModuleUpdateView,
                    self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        '''executed for get requests.  Builds an empty formset
        '''

        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        '''builds a moduleformset, execute is valid method, if it is valid we save any changes made and then redirect to manage_course_list
        '''

        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})






