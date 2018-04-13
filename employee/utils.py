from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from rest_framework.views import exception_handler
from jsonfield import JSONField
import plotly.offline as opy
import plotly.graph_objs as go

geo_code_obj = Nominatim()


def get_lat_long(city_name=None):
    if city_name:
        try:
            geo_location = geo_code_obj.geocode(city_name)
            return {
                'lat': geo_location.latitude,
                'long': geo_location.longitude
            }
        except GeocoderTimedOut:
            return get_lat_long(city_name)


class CustomJSONField(JSONField):
    def value_from_object(self, obj):
        """Return the value of this field in the given model instance."""
        return getattr(obj, self.attname)

    def value_to_string(self, obj):
        return dict(self.value_from_object(obj))


def plot_graph(x=None, y=None, marker=None, mode="lines+markers", name='Trace', **kwargs):
    marker = marker if marker else {'color': '#bc8e76', 'size': "10"}
    title = kwargs.get("title", "Analysis of Response")
    graph_type = kwargs.get("graph_type", "bar")
    _traces = kwargs.get("traces", None)
    print(_traces)
    _layout = kwargs.get("layout", None)
    x_title = kwargs.get("x_title", "X axis")
    y_title = kwargs.get("y_title", "Y axis")
    if not _traces or not _layout:
        if graph_type == "bar":
            _traces = _traces if _traces else [go.Bar(x=x, y=y, name=name)]
            _layout = go.Layout(title=title, barmode='group',
                                xaxis={'title': x_title, 'tickformat': ',d'},
                                yaxis={'title': y_title, 'tickformat': ',d'})
        else:  # if graph_type == "scatter"
            _traces = _traces if _traces else [go.Scatter(x=x, y=y, marker=marker, mode=mode, name=name)]
            _layout = go.Layout(title=title, xaxis={'title': x_title}, yaxis={'title': y_title})
    data = go.Data(_traces)
    print(_traces)
    layout = _layout
    figure = go.Figure(data=_traces, layout=layout)
    div = opy.plot(figure, auto_open=False, output_type='div')
    return div


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
