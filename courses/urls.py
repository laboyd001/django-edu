from django.urls import path
from . import views


urlpatterns = [
    # course list
    path('mine/',
         views.ManageCourseListView.as_view(),
         name = 'manage_course_list'),
    # create courses
    path('create/',
         views.CourseCreateView.as_view(),
         name = 'course_create'),
    # edit courses
    path('<pk>/edit/',
         views.CourseUpdateView.as_view(),
         name = 'course_edit'),
    # delete courses
    path('<pk>/delete/',
         views.CourseDeleteView.as_view(),
         name = 'course_delete'),
    # update module
    path('<pk>/module/',
        views.CourseModuleUpdateView.as_view(),
        name = 'course_module_update'),
    # create content
    path('module/<int:module_id>/content/<model_name>/create/',
        views.ContentCreateUpdateView.as_view(),
        name = 'module_content_create'),
    # update content
    path('module/<int:module_id>/content/<model_name>/<id>/',
        views.ContentCreateUpdateView.as_view(),
        name = 'module_content_update'),
    # delete content
    path('content/<int:id>/delete/',
        views.ContentDeleteView.as_view(),
        name = 'module_content_delete'),
    # content list
    path('module/<int:module_id>/',
        views.ModuleContentListView.as_view(),
        name = 'module_content_list'),
    # reorder modules
    path('module/order/',
        views.ModuleOrderView.as_view(),
        name = 'module_order'),
    # reorder content    
    path('content/order/',
        views.ContentOrderView.as_view(),
        name = 'content_order'),
]