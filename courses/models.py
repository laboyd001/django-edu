from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import OrderField



class Subject(models.Model):
    '''the blueprints for an e-learning subject
    '''
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Course(models.Model):
    '''the blueprints for an e-learning course
    '''

    # instructor that created the course
    owner = models.ForeignKey(User,
                              related_name='courses_created',
                              on_delete=models.CASCADE)
    # subject tha the course belong to
    subject = models.ForeignKey(Subject,
                              related_name='courses',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    # used in URLS
    slug = models.SlugField(max_length=200, unique=True)
    # overview of the course
    overview = models.TextField()
    # date and time when course was created
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title

class Module(models.Model):
    '''the blueprints for an e-learning module
    '''
    course = models.ForeignKey(Course,
                              related_name='modules',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # field is named order and is calculated with respect to the 
    # course by setting 'for_fields=['course']
    # this means that the order for a new module will be assigned adding 1 to the module
    # of the last module of the same course
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)


class Content(models.Model):
    '''represents the modules' contents and defines a generic relation to associate any kind of content
    '''

    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                    # limit_choices limits ContentType that can be used
                                    # model__in is a field lookup to filter the query to ContentType objects
                                     limit_choices_to={'model__in':(
                                                                                            'text',
                                                                                            'video',
                                                                                            'image',
                                                                                            'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    # order is calculated with respect to the module field
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']



class ItemBase(models.Model):
    '''abstract model that other classes can inherit from
    '''

    owner = models.ForeignKey(User,
                              related_name='%(class) s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

class Text(ItemBase):
    '''stores text content
    '''

    content = models.TextField()


class File(ItemBase):
    '''stores files like PDFs
    '''

    file = models.FileField(upload_to='files')

class Image(ItemBase):
    '''stores image files
    '''

    file = models.FileField(upload_to='images')

class Video(ItemBase):
    '''stores videos, we'll use urls to embed videos
    '''

    url = models.URLField()


