> DOMAIN : http://192.168.5.47

Login API
=========
### Validate user
> url: <DOMAIN>/api-token-auth/
> > method: POST

##### POST DATA:
```json
{
	"username":"9898989898",  // contact number of user
	"password":"c4ca4238a0b923820dcc509a6f75849b"  // password (hash of plaintext)
}
```

##### Response:
###### Success:
```json
{
    "contact_number": "9898989898",  // Primary Contact Number/ Phone number of user
    "id": 8, // ID of user/employee 
    "first_name": "oliver",  // First Name of user
    "last_name": "queen",  // Last Name of user
    "profile_image": "http://192.168.5.47:8889/files/media/uploads/temp_l5hdp4b.jpeg",  // User's profile image
    "role": 3,  // Role of user - By default all employee role will be 3
    "hr_name": "Bruce",  // Name of HR 
    "hr_id": 6,  // Id of HR
    "hr_profile_image": "", // HR profile image empty string if profile_image not available
    "token": "962cfc6f0d49e3cf91081ca378f6c9a803cb95d8"  // Token for user

}
```
###### Failure:
```json
{
    "non_field_errors": [
        "Unable to log in with provided credentials."
    ],
    "status": 400,
    "detail": "Unable to log in with provided credentials."
}
```

Survey API Doc
==============
### Get list of available surveys
>url: <DOMAIN>/api/survey/

>authentication_require: Yes

>Authorization:Token 6dff9272440827751408a84a25ba679db1ddc820

>Content-Type:application/json

>method: GET

##### Response: json
```json
{
    "count": 4,  // total number of surveys
    "next": "http://192.168.5.9:8889/api/v1/survey/?limit=2&offset=2",  // url to next page
    "previous": null,  // url to previous page
    "results": [  // contains entries of all survey in current page result
        {
            "url": "http://192.168.5.9:8889/api/survey/1/",  // url of survey
            "id": 1,  // id of survey
            "name": "General",  // survey name
            "employee_group": "gotham",  // employee group
            "question": [  // lists all the question objects linked to the survey
            ],
            "steps": 5,  // N/A steps completed in survey
            "complete": true,  // N/A
            "start_date": "2017-12-28T23:59:00Z",  //  N/A not to start survey before this time
            "end_date": "2018-01-01T23:59:00Z",  //  N/A deadline to complete survey
            "created_by": {},  //  N/A
            "start_time": "1514764800",  // start epoch time
            "end_time": "1517443140",  // end_epoch time
            "current_time": 1515571139.2649748,  // current epoch time
            "total_question": 2,
            "responded": false
        }
    ]
}
```
-----
### Get detail of survey
>url: http://192.168.5.9:8889/api/survey/1/

>authentication_require: Yes

>Authorization:Token 6dff9272440827751408a84a25ba679db1ddc820

>Content-Type:application/json

>method: GET

```json
{
    "url": "http://192.168.5.9:8889/api/survey/1/",  // url of survey
    "id": 1,  // id of survey
    "name": "General",  // survey name
    "employee_group": "gotham",  // employee group
    "question": [  // lists all the question objects linked to the survey
        {
            "url": "http://192.168.5.9:8889/api/question_database/1/",  // N/A
            "question_id": 1,  // question_id
            "question_title": "How was your day today?",  // question_title
            "answer_type": 1,  // N/A for now.. 1 means rating type
            "options": 5,  // maximum rate_scale_value
            "asked_by": [ // N/A
                6
            ]
        },
        {
            "url": "http://192.168.5.9:8889/api/question_database/2/",  // N/A
            "question_id": 2,
            "question_title": "How was your experience with clients?",
            "answer_type": 1,
            "options": 7,  // maximum rate_scale_value
            "asked_by": [  // N/A
                6
            ]
        }
    ],
    "steps": 5,  // N/A steps completed in survey
    "complete": true,  // N/A
    "start_date": "2017-12-28T23:59:00Z",  //  N/A not to start survey before this time
    "end_date": "2018-01-01T23:59:00Z",  //  N/A deadline to complete survey
    "created_by": {},  //  N/A
    "start_time": "1514764800",  // start epoch time
    "end_time": "1517443140",  // end_epoch time
    "current_time": 1515571139.2649748,  // current epoch time
    "total_question": 2,
    "responded": false
}
```
-----
### Post response of survey
>url: http://0.0.0.0:8889/api/survey/response/

>authentication_require: Yes

>Authorization:Token 6dff9272440827751408a84a25ba679db1ddc820

>Content-Type:application/json

>method: POST

```json
{
    "survey_id": 1,  // id of survey
    "answers": {
        "1": {  // key is question id
            "r": 2  // rated value by user
        },
        "2": {  // key is question id
            "m": "user entered message",  // optional message
            "r": 2  // rated value by user
        }
    },
    "complete": true  // show status if survey is completed
}
```


Running Test
============
Selenium Test
-------------
**Login with fixture**
```
python manage.py test main.tests.LoginTestWithFixture
```
**Login without fixture**
```
python manage.py test main.tests.LoginTestWithoutFixture
```