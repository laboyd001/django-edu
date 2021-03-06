from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, \
                                      DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, \
                                       PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from django.forms.models import modelform_factory
from django.apps import apps
from django.db.models import Count
from django.views.generic.detail import DetailView


from .models import Course, Module, Content, Subject
from .forms import ModuleFormSet
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from students.forms import CourseEnrollForm


# ===================================================================================
# courses
# ===================================================================================

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

# ===================================================================================
# modules
# ===================================================================================

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



# ===================================================================================
# content
# ===================================================================================

class ContentCreateUpdateView(TemplateResponseMixin, View):
    '''view that handles creating or updating objects of any content model
    '''

    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        '''check if the model name is one of the 4 content types,
            obtain the class for given model name,
            if not valid return none
        '''

        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        '''builds dynamic form.  use exclude to specify common fields to exclude from the form,
        everything else is added automatically
        '''

        Form = modelform_factory(model, exclude=['owner',
                                                'order',
                                                'created',
                                                'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        '''recieves URL parameters and stores corresponding module, model, and content obj
        '''
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                        id=id,
                                        owner=request.user)
        return super(ContentCreateUpdateView,
                    self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        '''executed when GET is received.  Build the modelform or pass no instance to create new object
        '''

        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        '''executed when POST is received.  Build a modelform and pass any data submitted to it.
            validate it.
            if valid, create new object and assign request.user as owner
            if no ID, we know this is new object instead of updating existing one.
            if new object is created we also create content obj for given module
        '''

        form = self.get_form(self.model,
                            instance=self.obj,
                            data=request.POST,
                            files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                        item=obj)
            return redirect('module_content_list', self.module.id)

        return self.render_to_response({'form': form,
                                        'object': self.obj})

class ContentDeleteView(View):
    '''view for deleting content
    '''

    def post(self, request, id):
        '''retrieves content obj with given id,
            deletes related text, image, or video,
            then deletes the content object and
            redirect the user to a list of module contents
        '''

        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

# ===================================================================================
# Module and Content List View
# ===================================================================================

class ModuleContentListView(TemplateResponseMixin, View):
    '''view that displays all modules for a course and lists contents for a specific module
    '''

    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        '''method for getting the module obj with given id that belongs to current user and renders a template with the given module
        '''

        module = get_object_or_404(Module,
                                    id=module_id,
                                    course__owner=request.user)
        
        return self.render_to_response({'module': module})

# ===================================================================================
# ReOrder Modules and contents
# ===================================================================================

class ModuleOrderView(CsrfExemptMixin,
                    JsonRequestResponseMixin,
                    View):
    '''view that recieves the new order of modules' ID encoded in JSON
    '''
    
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                    course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin,
                    JsonRequestResponseMixin,
                    View):
    '''view that recieves the new order of content's ID encoded in JSON
    '''
    
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                        module__course__owner=request.user) \
                            .update(order=order)
        return self.render_json_response({'saved': 'OK'})

# ===================================================================================
# Course Catalog
# ===================================================================================

class CourseListView(TemplateResponseMixin, View):
    '''View that lists all available courses
    '''

    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        '''retrieve all subjects including the total number of courses for each
            retrieve all courses and the total number of modules for each
        '''

        subjects = Subject.objects.annotate(
                    total_courses=Count('courses'))
        courses = Course.objects.annotate(
                    total_modules=Count('modules'))
        if subject:
            # the slug is a URL parameter to retrieve the corresponding subject
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return self.render_to_response({'subjects': subjects,
                                        'subject': subject,
                                        'courses': courses})


class CourseDetailView(DetailView):
    '''detail view for a single course overview
    '''

    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        '''method that includes enrollment form in teh context for rendering templates
        '''

        context = super(CourseDetailView,
                        self).get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
                                   initial={'course':self.object})
        return context

