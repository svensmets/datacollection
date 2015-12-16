from django import template
register = template.Library()


@register.filter(name='addcss')
def add_css(field, css):
    '''
    filter to add css in template to fields in forms
    otherwise the css would have to be added in form definition
    usage: {{field|addcss:"form-control"}} in template
    http://vanderwijk.info/blog/adding-css-classes-formfields-in-django-templates/
    :param field: the field to add the css to
    :param css: the css that has to be added to the field
    :return the field with css added to it
    '''
    return field.as_widget(attrs={"class": css})


