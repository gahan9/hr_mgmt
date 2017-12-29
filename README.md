Login API
===
### Validate user
>url: http://0.0.0.0:8889/api-token-auth/

> method: POST

##### POST DATA:
```json
{
	"username":"123",  // contact number of user
	"password":"r@123456"  // password
}
```

##### Response:
###### Success:
```json
{
    "token": "62029f285675b98d380096ca9c14917cced77bfc"
}
```
###### Failure:
```json
{
    "non_field_errors": [
        "Unable to log in with provided credentials."
    ]
}
```

Survey API Doc
======
### Get list of available surveys
>url: http://0.0.0.0:8889/api/survey/

>authentication_require: Yes

>method: GET

##### Response: json
```json
{
    "count": 1,  // total number of survey page available
    "next": null,  // url to next page
    "previous": null,  // url to previous page
    "results": [  // contains entries of all survey in current page result
        {
            "url": "http://0.0.0.0:8889/api/survey/33/",  // url of survey
            "id": 33,  // id of survey
            "name": "GENERAL EXPRESSION",  // survey name
            "employee_group": "North",  // employee group
            "question": [  // lists all the question objects linked to the survey
            ],
            "steps": 5,  // N/A steps completed in survey
            "complete": true,  // N/A
            "start_date": "2017-12-28T23:59:00Z",  //  N/A not to start survey before this time
            "end_date": "2018-01-01T23:59:00Z",  //  N/A deadline to complete survey
            "created_by": {}  //  N/A
        }
    ]
}
```
-----
### Get detail of survey
>url: http://0.0.0.0:8889/api/survey/

>authentication_require: Yes

>method: GET

```json
{
            "url": "http://0.0.0.0:8889/api/survey/33/",  // url of survey
            "id": 33,  // id of survey
            "name": "GENERAL EXPRESSION",  // survey name
            "employee_group": "North",  // employee group
            "question": [  // lists all the question objects linked to the survey
                {
                    "url": "http://0.0.0.0:8889/api/question_database/62/",  // url to the question (only for HR/admin)
                    "id": 62,  // id of question
                    "question": "Express you thought about company",  // question title
                    "answer_type": 2,  // question's answer type
                    "content_type": {},  //  N/A Handled in Backend
                    "asked_by": []  //  N/A Handled in Backend
                }
            ],
            "steps": 5,  // N/A steps completed in survey
            "complete": true,  // N/A
            "start_date": "2017-12-28T23:59:00Z",  //  N/A not to start survey before this time
            "end_date": "2018-01-01T23:59:00Z",  //  N/A deadline to complete survey
            "created_by": {}  // N/A
        }
```
-----
### Post response of survey
>url: http://0.0.0.0:8889/api/survey/response/

>authentication_require: to be discuss later (for now NO)

>method: POST

```json
{
    "related_survey": null,  // id of survey
    "related_user": null,  // id of user (given in login api- depend on authentication_requirement)
    "answers": "",  // a list
    "complete": false  // check True if completed all question
}
```

