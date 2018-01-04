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

>Authorization:Token 6dff9272440827751408a84a25ba679db1ddc820

>Content-Type:application/json

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

>Authorization:Token 6dff9272440827751408a84a25ba679db1ddc820

>Content-Type:application/json

>method: GET

```json
{
            "url": "http://0.0.0.0:8889/api/survey/33/",  // url of survey
            "id": 33,  // id of survey
            "name": "GENERAL EXPRESSION",  // survey name
            "employee_group": "North",  // employee group
            "question": [  // lists all the question objects linked to the survey
                {
                    "url": "http://192.168.5.9:8889/api/question_database/68/",
                    "id": 68,  // question id
                    "question": "status?",  // question title
                    "answer_type": 0,  // answer type (0- MCQ, 1- Rating, 2- Text)
                    "content_type": 13,  // N/A 
                    "content_object": {
                        "url": "http://192.168.5.9:8889/api/answers/mcq/17/",
                        "id": 17,
                        "option": "['done', 'to be done']"  // get_option from here if it is mcq (if answer type == 0)
                    },
                    "asked_by": [
                        31  // N/A db id of user/HR who used this question 
                    ],
                    "object_id": 17  // N/A id of object in database
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

>authentication_require: Yes

>Authorization:Token 6dff9272440827751408a84a25ba679db1ddc820

>Content-Type:application/json

>method: POST

```json
{
    "related_survey": null,  // id of survey
    "related_user": null,  // id of user (given in login api- depend on authentication_requirement)
    "answers": "",  // a list
    "complete": false  // check True if completed all question
}
```

