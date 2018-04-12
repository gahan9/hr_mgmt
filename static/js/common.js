function setCSRF(xhr, settings) {
    xhr.setRequestHeader("Authorization", "Token " + user_token);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
}
function failureCallback(jqXHR, textStatus, errorThrown) {
    var error = (jqXHR.responseText).detail;
    console.log(error);
    return error
}

function doAjax(method, url, data, headers, successCallback, failureCallback) {
    $.ajax({
        type: method,
        url: url,
        data: data,
        headers: headers,
        beforeSend: setCSRF,
        success: successCallback,
        error: failureCallback,
        // complete: removeLoader
    });
}

function GetRequest(url) {
    var data;
    $.ajax({
        url: url,
        method: "GET",
        contentType: "application/json;charset=utf-8",
        beforeSend: setCSRF,
        success: function (responseObj) {
            console.log("GetRequest success!");
            console.log('sdsad',responseObj.results);
            data = responseObj.results;

        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log("some error " + String(errorThrown) + String(textStatus) + String(XMLHttpRequest.responseText));
            data = textStatus;
        }
    });
    return data
}


function CustomRequest(content) {
    $.ajax({
        url: content.url,
        method: content.method,
        data: JSON.stringify(content.data),
        contentType: "application/json;charset=utf-8",
        beforeSend: setCSRF,
        success: function (responseObj) {
            console.log("CustomRequest success!");
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log("some error " + String(errorThrown) + String(textStatus) + String(XMLHttpRequest.responseText));
        }
    });
}
