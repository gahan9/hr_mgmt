from django import template
register = template.Library()


@register.filter
def message_filter(msg, **kwargs):
    if msg.message.lower().startswith("error"):
        return 'alert-danger'
        # return 'class=row alert-danger'
    else:
        return 'class=row alert-success'


@register.filter
def get_display(arg, **kwargs):
    print(arg)
    return arg
