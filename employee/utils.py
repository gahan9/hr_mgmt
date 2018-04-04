from rest_framework.views import exception_handler
from jsonfield import JSONField


class CustomJSONField(JSONField):
    def value_from_object(self, obj):
        """Return the value of this field in the given model instance."""
        return getattr(obj, self.attname)

    def value_to_string(self, obj):
        return str(self.value_from_object(obj))


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    try:
        errors = ["{} : {}".format(field, value) for field, value in response.data.items()]
        error_string = ", ".join(errors)
    except Exception as e:
        error_string = "Unknown Exception: {}".format(e)

    if response is not None:
        # add the HTTP status code to the response.
        response.data['status'] = response.status_code
        if "non_field_errors" in response.data:
            # merge any non_field_errors in response
            response.data['detail'] = ", ".join(response.data['non_field_errors'])
        else:
            response.data['detail'] = error_string
    return response
