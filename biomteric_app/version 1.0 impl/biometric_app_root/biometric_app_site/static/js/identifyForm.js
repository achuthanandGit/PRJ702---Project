/**
 * identifyForm.js
 * Author : Achuthanand
 * 
 * This js is used to manage the events and validation for the functionality of 
 * uploading the image and showing the results
 */

/**
 * Getting the components required for event tracking and validations
 */
var username_id = document.getElementById('id_username');
var image_id = document.getElementById('id_image');
var tank_id = document.getElementById('id_tank');
var required_error_id = document.getElementById('required_error_id');
var identify_btn_id = document.getElementById('identify_btn_id');
var formDiv = document.getElementById('form-id');
var form = document.getElementById('identify_form');
var resultDiv = document.getElementById('result-id');
var loadingDiv = document.getElementById('loading-id');
var dropZone = document.getElementById('drop-zone');
// var email_id = document.getElementById('id_email');
// var invalid_email_error_id = document.getElementById('invalid_email_error_id');

/**
 * Global variables required throught out the page actions
 */
var activeRequests = 0;
var isCtrlKey = false;
var isShiftKey = false;
var isRKey = false;

/**
 * to track the page reload/refresh
 */
window.onbeforeunload = function() {
    // checking whether any request is waiting for the response
    if(activeRequests !== 0){
        // If any requests pending show alert using modal
        $('#alert-modal').modal();
        // prevents the page from reload/refresh
        return 'not allowed';
    }
};

/**
 * to control the keys and shortcut user uses
 */
$(window).on('keydown', function(event) {
    if(event.ctrlKey)
        isCtrlKey = true;
    if(event.shiftKey)
        isShiftKey = true;
    if(event.keyCode == 82)
        isRKey = true;

    // Preventing the hard refresh (ctrl+sift+r) when pending requests exists
    if((isCtrlKey && isShiftKey && isRKey && activeRequests !==0) ||
        (event.keyCode == 116 && activeRequests !==0)){
        isCtrlKey = false;
        isShiftKey = false;
        isRKey = false;
        // If any requests pending show alert using modal
        $('#alert-modal').modal();
        // prevents the hard refresh
        return false;
    }
});


/**
 * TO trigger onchange event only when the getElementById value is not null or empty
 */
if(username_id) {
    username_id.onchange = function() {checkEmpty(username_id)};
}
if(tank_id) {
    tank_id.onchange = function() {checkEmpty(tank_id)};
}
if(image_id) {
    image_id.onchange = function() {upload_img()};
}

/*
 if(email_id) {
    email_id.onchange = function() {
        validateMailFormat()
    };
}
*/

/**
 * submit event will trigger when the user clicks identify button after providing required details
 */
$('#identify_form').on('submit', function(event) {
    event.preventDefault();
    // getting form data
    var formData = new FormData(form);
    // calling method to initiate the ajax request
    identifyFish(form, formData);
});

/**
 * upload_img will update the image view when the user upload image by clicking choose image button
 */
function upload_img() {
    // getting the uploaded image and setting the view
    if (image_id.files && image_id.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#img_id').attr('src', e.target.result);
        }
        reader.readAsDataURL(image_id.files[0]);
        document.getElementById('drop-zone').style.height = '50px';
        document.getElementById('drop-zone').style.lineHeight = '50px';
    }
    // throws required error if there was an image and then removed it
    if(0 == image_id.files.length)
        required_error_id.style.display = 'block';
    else
        required_error_id.style.display = 'none';
    // initiating enable/disable process of identify button according to the field values
    checkBtnAccess();
};

/**
 * checkEmpty is used to check whether the passed field value is empty or not
 * @param {string} field_id 
 */
function checkEmpty(field_id) {
    if(0 == field_id.value.length) 
        required_error_id.style.display = 'block';
    else 
        required_error_id.style.display = 'none';
    // initiate the enable/disable process of identify button according to the field values
    checkBtnAccess();
};


/**
 * checkBtnAccess will decide whether the identify needs to enable/diable
 */
function checkBtnAccess() {
    if((0 == username_id.value.length) || 
       // (0 == email_id.value.length) ||
        (0 == tank_id.value.length) ||
        (0 == image_id.files.length)) {
        enableIdentifyBtn(false);
    } else {
        enableIdentifyBtn(true);
    }
};

/**
 * enableIdentifyBtn will enable identify button if allFieldCheck is true else will diable the button
 * @param {boolean} allFieldCheck 
 */
function enableIdentifyBtn(allFieldCheck) {
    if(allFieldCheck) {
        identify_btn_id.classList.remove('disabled');
        identify_btn_id.removeAttribute('disabled');
    } else {
        identify_btn_id.classList.add('disabled');
        identify_btn_id.setAttribute('disabled', 'disabled');
    }
};

/**
 * identifyFish will initiate the ajax request to the server to process
 * @param {object} form 
 * @param {object} formData 
 */
function identifyFish(form, formData) {
    // actions to perform when waiting for the response
    /* formDiv.style.display = 'none';
     dropZone.style.display = 'none';
     loadingDiv.style.display = 'block';
     resultDiv.style.display = 'block';
    */
    // reseting the form for next entry
    form.reset();
    // incrementing the active request to track pending requests
    activeRequests++;

    // initaiting ajax request
    $.ajax({
        url : 'identify-fish/',
        type : 'POST',
        data : formData,
        contentType :  false,
        processData : false,
        success : function(response) {
            // decrementing the active request since got the response
            activeRequests--;
            
            // actions to perform when waiting for result
            /* enableIdentifyBtn(false);
            form.reset();
            showResult(response);
            */
        },
        error : function(xhr,errmsg,err) {
            // decrementing the active request since got the response
            activeRequests--;
            showAjaxError(xhr, errmsg, err)
        }
    });
    // showing the modal to inform the user that the request is submitted and is in under process
    $('#submit-modal').modal();
};

/**
 * showAjaxError is used to show the ajax error message
 * @param {object} xhr 
 * @param {string} errmsg 
 * @param {string} err 
 */
function showAjaxError(xhr, errmsg, err) {
    // adding error to dom
    $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
    "Reload and try again.</div>");
    // adding more info about the error to the console
    if(xhr && err) 
        console.log(xhr.status + ": " + xhr.responseText); 
};

/**
 * showResult is used to load the ajax response
 * @param {object} resultSet 
 */
function showResult(resultSet) {
    var resultType;
    var result;
    loadingDiv.style.display = 'none';
    resultDiv.style.display = 'block';
    result = resultSet["matching_image_list"][0];
    resultType = resultSet['type'];
    // showing the result according to the resultType
    if('success' == resultType) {
        $('#result-list').html("<li class='list-group-item list-group-item-success'> Name: "+ result['name']+"</li>"+
        "<li class='list-group-item list-group-item-success'> Population: "+ result['population']+"</li>"+
        "<li class='list-group-item list-group-item-success'> Date: "+ result['date']+"</li>");
    } else {
        $('#result-list').html("<li class='list-group-item list-group-item-danger'>"+ result['message']+"</li></ul>");
    }
};

/**
 * to enable the user to upload next image when try_again buton is clicked
 */
$('#try_again_id').on('click', function(event) {
    LoadUploadForm();
});

/**
 * LoadUploadForm is used to load fresh form to upload new data
 */
function LoadUploadForm() {
    // removes the result div of previous submission
    RemoveResultChild();
    // resets the form to input new data
    form.reset();
    // showing required div and hiding others
    loadingDiv.style.display = 'none';
    formDiv.style.display = 'block';
    dropZone.style.display = 'block';
    //document.getElementById('drop-zone').style.height = '200px';
    //document.getElementById('drop-zone').style.lineHeight = '200px';
    resultDiv.style.display = 'none';
};

/**
 * RemoveResultChild will clear and hide the result div when try again button is clicked
 */
function RemoveResultChild() {
    var resultListDiv = document.getElementById('result-list');
    while(resultListDiv.firstChild){
        resultListDiv.removeChild(resultListDiv.firstChild);
    }
};

// condition to check whether the drop zone is ready to upload
if(dropZone) {
    /**
     * ondrop will initiate the process to load the image view when the user dropped 
     * the image in the upload area
     */
    dropZone.ondrop = function(e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';
        startUpload(e.dataTransfer.files)
    }

    /**
     * ondragover will add the class to show that the drop area is enabled when user 
     * dragged the image over the upload area
     */
    dropZone.ondragover = function() {
        this.className = 'upload-drop-zone drop';
        return false;
    }

    /**
     * ondragleave is used to remove the class which shows that the drop area is enabled
     */
    dropZone.ondragleave = function() {
        this.className = 'upload-drop-zone';
        return false;
    }
}


/**
 * startUpload will update the image when user dropped the image in the upload area
 * @param {object} files 
 */
var startUpload = function(files) {
    // upadting the form with dropped image
    var reader = new FileReader();
    reader.onload = function (e) {
        $('#img_id').attr('src', e.target.result);
    }
    image_id.files = files;
    reader.readAsDataURL(files[0]);
    // enable/disable identify button according to the image uploaded
    checkBtnAccess();
    // updating the upload area view size when uploaded image view is enabled
    document.getElementById('drop-zone').style.height = '50px';
    document.getElementById('drop-zone').style.lineHeight = '50px';
}

