from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from django.forms.widgets import PasswordInput

create_company_helper = FormHelper()
create_company_helper.form_tag = False
create_company_helper.form_class = ''
create_company_helper.form_method = 'POST'
# create_staff_helper.form_show_labels = False
# create_staff_helper.label_class = 'col-sm-2 col-form-label'
create_company_helper.layout = Layout(
    Div(
        Field('contact_number', css_class='form-control', placeholder='Mobile Number (used as Username)'),
        Field('profile_image', css_class='form-control', placeholder='Company Logo'),
        Field('name', css_class='form-control', placeholder='Company Name'),
        Field('country', css_class='form-control', placeholder='Country'),
        Field('first_name', css_class='form-control', placeholder='Owner First Name'),
        Field('last_name', css_class='form-control', placeholder='Owner Last Name'),
        Field('email', css_class='form-control', placeholder='Email'),
        Field('alternate_email', css_class='form-control', placeholder='Alternate Email'),
        Field('alternate_contact_no', css_class='form-control', placeholder='Mobile Number'),
        Field('password', css_class='form-control', placeholder='Password'),
        Field('role', css_class='custom-control-input', placeholder='Specify user role?'),
        css_class="form-group row"
    ),
)


create_hr_helper = FormHelper()
create_hr_helper.form_tag = False
create_hr_helper.form_class = ''
create_hr_helper.form_method = 'POST'
create_hr_helper.layout = Layout(
    Div(
        Field('contact_number', css_class='form-control', placeholder='Primary Mobile Number (for username)'),
        Field('profile_image', css_class='form-control', placeholder='Company Logo'),
        Field('first_name', css_class='form-control', placeholder='First Name'),
        Field('last_name', css_class='form-control', placeholder='Last Name'),
        Field('email', css_class='form-control', placeholder='Email'),
        Field('password', css_class='form-control', placeholder='Password'),
        Field('alternate_contact_no', css_class='form-control', placeholder='Mobile Number'),
        Field('alternate_email', css_class='form-control', placeholder='Alternate Email'),
        Field('job_title', css_class='form-control', placeholder='Job Title'),
        Field('street', css_class='form-control', placeholder='Street'),
        Field('zip_code', css_class='form-control', placeholder='Zip Code'),
        Field('city', css_class='form-control', placeholder='City'),
        Field('country', css_class='form-control', placeholder='Country'),
        Field('role', css_class='form-control select', placeholder='Specify user role?'),
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
            Field('file', css_class='form-control'),
            Field('category', css_class='form-control', placeholder="Employee Group/Region"),
            css_class="col-md-3"
        ),
        Div(
            FormActions(Submit('Upload', value="Upload", css_class="btn-theme"),),
            css_class="col-md-3"
        ),
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

edit_user_helper = FormHelper()
edit_user_helper.form_tag = False
edit_user_helper.form_class = ''
edit_user_helper.form_method = 'POST'
edit_user_helper.layout = Layout(
    Div(
        Field('contact_number', css_class='form-control', placeholder='Primary Mobile Number (for username)', readonly=True),
        Field('profile_image', css_class='form-control', placeholder='Company Logo'),
        Field('first_name', css_class='form-control', placeholder='First Name'),
        Field('last_name', css_class='form-control', placeholder='Last Name'),
        Field('email', css_class='form-control', placeholder='Email'),
        Field('password', css_class='form-control', placeholder='Password'),
        Field('role', css_class='form-control select', placeholder='Specify user role?'),
        css_class="form-group row"
    ),
)

edit_employee_data_helper = FormHelper()
edit_employee_data_helper.form_tag = False
edit_employee_data_helper.form_class = ''
edit_employee_data_helper.form_method = 'POST'
edit_employee_data_helper.layout = Layout(
    Div(
        Field('user', css_class='form-control', placeholder='user', disabled=True),
        Field('company_name', css_class='form-control', placeholder='company', disabled=True),
        Field('alternate_contact_no', css_class='form-control', placeholder='Mobile Number'),
        Field('alternate_email', css_class='form-control', placeholder='Alternate Email'),
        Field('job_title', css_class='form-control', placeholder='Job Title'),
        Field('street', css_class='form-control', placeholder='Street'),
        Field('zip_code', css_class='form-control', placeholder='Zip Code'),
        Field('city', css_class='form-control', placeholder='City'),
        Field('country', css_class='form-control', placeholder='Country'),
        css_class="form-group row"
    ),
)
