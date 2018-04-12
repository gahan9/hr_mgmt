function failureCallback(jqXHR, textStatus, errorThrown) {
    var error = (jqXHR.responseText).detail;
    console.log(error);
    console.log("some error " + String(errorThrown) + String(textStatus) + String(XMLHttpRequest.responseText));
    return error
}

function doAjax(method, url, data, headers, successCallback, failureCallback, setCSRF) {
    // console.log("doAjax...", method, url, data, headers);
    $.ajax({
        type: method,
        url: url,
        data: data,
        headers: headers,
        contentType: "application/json;charset=utf-8",
        beforeSend: setCSRF,
        success: successCallback,
        error: failureCallback,
        // complete: removeLoader
    });
}

function value_setter(value, location) {
    if (localStorage.getItem(value)) {
        if (localStorage.getItem(value) !== "undefined") {
            $(location).val(localStorage.getItem(value));
        }
    }
}

function DivChanger(flag) {
    if (flag === "reset") {
        var decide = document.getElementById("variable-div").classList.contains('col-lg-12');
        if (decide === true) {
            document.getElementById("variable-div").className = "col col-12 col-lg-6 col-md-6 text-center";
        }
    }
    else {
        document.getElementById("variable-div").className = "col col-12 col-lg-12 col-md-12 text-center";
    }
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
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
