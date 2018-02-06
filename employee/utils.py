from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    try:
        errors = ["{} : {}".format(field, ", ".join(value)) for field, value in response.data.items()]
        error_string = ", ".join(errors)
        # response_dict = {'detail': ", ".join(errors)}
        # print("--------------------", response_dict)
    except Exception as e:
        error_string = "Unknown Exception: {}".format(e)
    # Now add the HTTP status code to the response.

    if response is not None:
        response.data['status'] = response.status_code
        if "non_field_errors" in response.data:
            response.data['detail'] = ", ".join(response.data['non_field_errors']) + ", " + error_string
        else:
            response.data['detail'] = error_string
    return response
