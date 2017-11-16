from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from django.forms.widgets import PasswordInput

create_staff_helper = FormHelper()
create_staff_helper.form_tag = False
create_staff_helper.form_class = ''
create_staff_helper.form_method = 'POST'
# create_staff_helper.form_show_labels = False
# create_staff_helper.label_class = 'col-sm-2 col-form-label'
create_staff_helper.layout = Layout(
    Div(
        Field('first_name', css_class='form-control', placeholder='First Name'),
        Field('last_name', css_class='form-control', placeholder='Last Name'),
        Field('username', css_class='form-control', placeholder='Username'),
        Field('email', css_class='form-control', placeholder='Email'),
        Field('alternate_email', css_class='form-control', placeholder='Alternate Email'),
        Field('password', css_class='form-control', placeholder='Password'),
        Field('contact_no', css_class='form-control', placeholder='Mobile Number'),
        Field('job_title', css_class='form-control', placeholder='Job Title'),
        Field('company_name', css_class='form-control', placeholder='Company Name'),
        # Field('is_staff', css_class='custom-control-input', placeholder='Allow Admin Rights?'),
        css_class="form-group row"
    ),

)

file_upload_helper = FormHelper()
file_upload_helper.form_tag = True
file_upload_helper.form_class = 'form-horizontal'
file_upload_helper.form_method = 'POST'
file_upload_helper.form_show_labels = False  # default = True
file_upload_helper.layout = Layout(
    Div(
        Div(
            Div(
                Field('file', css_class='form-control'),
                css_class="col-md-3"
            ),
            Div(
                FormActions(
                    Submit('Upload', value="Upload", css_class="btn-theme"),
                ),
                css_class="col-md-3"
            ),
            css_class="row"),
        css_class="container")
)

survey_helper = FormHelper()
survey_helper.form_tag = True
survey_helper.form_class = ''
survey_helper.form_method = 'POST'
survey_helper.label_class = 'col-sm-2 col-form-label'
survey_helper.layout = Layout(
    Div(
        Field('name', css_class='form-control'),
        Field('employee_group', css_class='form-control'),
        css_class="form-group row"
    )
)
