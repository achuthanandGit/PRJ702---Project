/**
 * identifyList.js
 * Author : Achuthanand
 * 
 * This js is used to manage the events of the table view of uploaded data
 */

 /**
  * global variables requried throught out the page actions
  */
 var matchResult = [];
 var defaultPosition = 0;
 var rowData = [];

 // to make use to DataTable API
 var table = $('#table-identify-list').DataTable();
 

/**
 * To get the table row values when a row is clicked by user
 */
$('#table-identify-list tbody').on( 'click', 'tr', function () {
    rowData = table.row(this).data();
    GetMatchData(rowData);
} );

/**
 * GetMatchData is used to initiate the ajax request to get the match data
 * @param {object} rowData 
 */
function GetMatchData(rowData) {
    var csrftoken = Cookies.get('csrftoken');
    // initaiting ajax request
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        url : 'get-match-data/',
        type : 'POST',
        data : {'imageId':rowData[0]},
        
        // handling ajax success
        success : function(response) {
            matchResult = [];
            matchResult = response;
            showMatchResult(matchResult);
        },
        // handling ajax error
        error : function(xhr,errmsg,err) {
            showAjaxError(xhr, errmsg, err)
        }
    });
    
};

/**
 * showMatchResult is used to show the matching results when a row is clicked
 * @param {object} matchResult 
 */
function showMatchResult(matchResult) {
    defaultPosition = 0
    // clearing previous data
    $('.carousel-inner,.carousel-indicators').empty()
    // clearing previous resuly error
    RemoveResultChild('modal-result');
    // clearing previous match results
    RemoveResultChild('match-details');
    // Showing result according to matchResult
    if(matchResult.length == 0) {
        $("#table-match-data tr").remove(); 
        $('#modal-result').html("<div class='alert-box alert radius' data-alert>Sorry. There is no match data available.</div>");
        $('#re-check-button').show();
    } else {
        $('#re-check-button').hide();
        // Adding match details 
        $('#match-details').html('<h6 style="color: blue;">Total matches = '+matchResult.length+'</h6>');
        // adding match images to carousel
        for(i=0; i<matchResult.length; i++) {
            $('<div class="carousel-item"><img src="'+matchResult[i]['imagePath']+'" width="100%"></div>').appendTo('.carousel-inner');
            $('<li data-target="#carousel" data-slide-to="'+i+'"></li>').appendTo('.carousel-indicators');
        }
        // setting 1st image as active one
        $('.carousel-item').first().addClass('active');
        $('.carousel-indicators > li').first().addClass('active');
        $('#carousel').carousel();
        UpdateMatchData('');
    }
    // prevents the modal to close when clicked outside the modal
    PreventModalCloseWhenActive();

    // display the modal with resultant data
    $('#details-modal').modal();
};

/**
 * RemoveResultChild is used to remove the error result when match data is displayed
 * @param {string} divId 
 */
function RemoveResultChild(divId) {
    var resultListDiv = document.getElementById(divId);
    if(resultListDiv && resultListDiv.firstChild){
        resultListDiv.removeChild(resultListDiv.firstChild);
    }
};

/**
 * PreventModalCloseWhenActive is used to prevent bootstrap modal to close when clicked outside modal
 * when model is active
 */
function PreventModalCloseWhenActive() {
    // to avoid closing the modal when clicked outside
    $('#details-modal').modal({
        backdrop: 'static',
        keyboard: false
    });
}

/**
 * showAjaxError is used to show the ajax error message
 * @param {object} xhr 
 * @param {string} errmsg 
 * @param {string} err 
 */
function showAjaxError(xhr, errmsg, err) {
    // clearing previous data
    $('.carousel-inner,.carousel-indicators').empty()
    RemoveResultChild('match-details');
    RemoveResultChild('modal-result');
    // adding error to dom
    $('#modal-result').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
    "Reload and try again.</div>");
    $('#details-modal').modal();
    // adding more info about the error to the console
    if(xhr && err) 
        console.log(xhr.status + ": " + xhr.responseText); 
};

/**
 * used to manage the previous view in carousel
 */
$('.prev').click(function(){
    if(defaultPosition > 0){
        defaultPosition--;
        UpdateMatchData('prev');
    }
});

/**
 * used to manage the next view in carousel
 */
$('.next').click(function(){
    if(defaultPosition != matchResult.length - 1){
        defaultPosition++;
        UpdateMatchData('next');
    }   
});

/**
 * UpdateMatchData is used to update the match data and image view according to slidePosition parameter
 * @param {string} slidePosition 
 */
function UpdateMatchData(slidePosition) {
    var dataToUpdate = {};
    // clearing the table data
    $("#table-match-data tr").remove(); 
    if(slidePosition)
        $('#carousel').carousel(slidePosition);
    dataToUpdate = matchResult[defaultPosition];
    // putting match data to the table
    $('#table-match-data').html('<tbody>'+
    '<tr><td> Name </td><td>'+ dataToUpdate['name']+'</td></tr>'+
    '<tr><td> Tag </td><td>'+ dataToUpdate['tag']+'</td></tr>'+
    '<tr><td> Population </td><td>'+ dataToUpdate['population']+'</td></tr>'+
    '<tr><td> Tank </td><td>'+ dataToUpdate['tank']+'</td></tr>'+
    '<tr><td> Date </td><td>'+ dataToUpdate['date']+'</td></tr></tbody>');
};

/**
 * trigger the identification process when clicked re-check button
 */
$('#re-check-button').click(function(event) {
    $('#modal-result').html("<div class='alert-box alert radius' data-alert>This will take a while. Please wait.</div>");
    $('#re-check-button').hide();
    TryAgain();
});

/**
 * TryAgain will evaluate the uploaded data which has no match results when analyzed previously
 */
function TryAgain() {
    var csrftoken = Cookies.get('csrftoken');
    // initiating ajax request
    $.ajax({
        headers: { "X-CSRFToken": csrftoken },
        url : 'try-again/',
        type : 'POST',
        data : {'imageId':rowData[0]},
        
        // handling ajax success
        success : function(response) {
            matchResult = [];
            matchResult = response;
            // closes the modal
            $('#details-modal').modal('hide');
            // displays the new match result
            showMatchResult(matchResult);
        },
        // handling ajax error
        error : function(xhr,errmsg,err) {
            showAjaxError(xhr, errmsg, err)
        }
    });
};