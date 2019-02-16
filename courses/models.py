from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return self.title

