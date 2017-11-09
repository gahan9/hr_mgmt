from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

file_upload_helper = FormHelper()
file_upload_helper.form_tag = True
file_upload_helper.form_class = 'form-horizontal'
file_upload_helper.form_method = 'POST'
file_upload_helper.form_show_labels = True  # default = True
file_upload_helper.layout = Layout(
    Div(
        Div(
            Div(
                Field('file', css_class='form-control'),
                css_class="col-md-3"
            ),
            Div(
                FormActions(
                    Submit('Upload', value="Upload", css_class="btn btn-theme"),
                ),
                css_class="col-md-3"
            ),
            css_class="row"),
        css_class="container")
)
