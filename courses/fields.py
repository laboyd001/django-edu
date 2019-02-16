from django.db import models
from  django.core.exceptions import ObjectDoesNotExist



class OrderField(models.PositiveIntegerField):
    '''this is a custom field that inherits from PositiveIntegerField this will allow the app to define an ordr for objects
    
    Arguments:
        models {PositiveIntegerField} -- [easily specifies the order of objects]
    '''

    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self) .__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        # check to see if a value already exists in the model instance
        # self.attname is the attribute given to the field in the model
        # if the fields value is different than 'None' we calculate the
        # order it is given
        if getattr(model_instance, self.attname) is None:
            # no current value
            try:
                # build a queryset to retrieve all objects for field's model
                # we retrieve the model class the field belongs to with
                # 'self.model
                qs = self.model.objects.all()
                # we filter the queryset by the field's current value 
                # for the fields that are defined in 'for_fields' paramater
                # of the field, if any
                if self.for_fields:
                    # filter by objects with same field values
                    # for the fields in 'for_fields'
                    query = {field: getattr(model_instance, field)\
                    for field in self.for_fields}
                    qs = qs.filter(**query)
                # get the order of the last item
                # retrieve the object with the highest order with 'last_item'
                last_item = qs.latest(self.attname)
                # if an object is found we assume this is the highest order
                # found and add 1 to it
                value = last_item.order + 1
            except ObjectDoesNotExist:
                # if no object is found we assume this is the first one and assign 0 to it
                value = 0
            # assign the calculated order to the field's value using setattr
            # and return it
            setattr(model_instance, self.attname, value)
            return value
        else:
            # if the model instance has a value for the current field
            # we don't do anything
            return super(OrderField,
                         self) .pre_save(model_instance, add)


