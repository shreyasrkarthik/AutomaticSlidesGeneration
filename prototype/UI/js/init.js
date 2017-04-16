// Code to activate some features of framework. Required! DO NOT DELETE!!!
(function($){
  $(function(){
    $('.button-collapse').sideNav();
    $('.parallax').parallax();
    $('select').material_select();
    $("#logoLinkOrLocal").change(function() {
        if(this.checked){
            $("#logoDiv").removeClass("file-field");
            $("#logoField").html("<input type='url' id='logoFile' name='logoFile' class='validate'>"
                +"<label for='logoFile' data-error='error with link' data-success='valid'>"
                +"Enter link for logo which will be added to slides</label>");
        }
        else
        {
            $("#logoDiv").addClass("file-field");
            $("#logoField").html('<div class="btn">' +
                        '<span>Logo</span>' +
                        '<input name="logoFile" type="file">' +
                        '</div><div class="file-path-wrapper">'+
                        '<input class="file-path validate" type="text" placeholder="Click to select logo">'+
                        '</div>');
        }
    });
    $("#resourceLinkOrLocal").change(function() {
        if(this.checked){
            $("#resourceDiv").removeClass("file-field");
            $("#resourceField").html("<input type='url' id='resourceFile' name='resourceFile' class='validate'>"
                +"<label for='resourceFile' data-error='error with link' data-success='valid'>"
                +"Enter link for resource file based on which slides are generated</label>");
        }
        else
        {
            $("#resourceDiv").addClass("file-field");
            $("#resourceField").html('<div class="btn">' +
                        '<span>Resource File</span>' +
                        '<input name="resourceFile" type="file">' +
                        '</div><div class="file-path-wrapper">'+
                        '<input class="file-path validate" type="text" placeholder="Click to select resource file">'+
                        '</div>');
        }
    });
  }); // end of document ready
})(jQuery);// end of jQuery name space


function uploadPhaseDone(){
    $("#uploadPhaseIcon").html("done");
    $("#uploadPhaseButton").removeClass("pulse");
    $("#uploadPhaseButton").removeClass("brown");
}

function validateForm() {
    if ($("input[name='mainSlideTitle']").val() == "")
        alert("Please enter slide title.");
    if ($("input[name='archiveName']").val() == "")
        alert("Please enter a name for archive.");
    if ($("input[name='resourceFile']").val() == "")
        alert("Please select a resource file.");    
}

function enableDownload() {
    $("#processingMainIcon").html("done");
    $("#processingMainButton").removeClass("pulse");
    $("#downloadPhaseButton").removeClass("brown");
    $("#downloadPhaseButton").addClass("teal");
    $("#downloadPhaseButton").addClass("pulse");
    $("#downloadPhaseIcon").html("loop");
    var archiveName = $("#archiveName").val();
    var downloadUrl = window.location+"getArchive.php?archiveName="+archiveName;
    $("#downloadPhaseButton").attr("href",downloadUrl);
    $("#downloadPhaseIcon").html("cloud_done");
}

function initiateProcessPhaseCheck(event){
    $("#processingMainIcon").html("loop");
    $("#processingMainButton").removeClass("brown");
    $("#processingMainButton").addClass("pulse");
    $("#st1Icon").html("loop");
}


function updateProcessPhase(event) {
    $("#"+event.data).addClass("teal-text");
    $("#"+event.data+"Icon").html("done");
    if(event.data == "st3") 
    {
        eventSource.close();
        enableDownload();
    }
}

function errorWhileCheckingProgress(event) {
        var archiveName = $("#archiveName").val();
        var downloadUrl = window.location+"getArchive.php?archiveName="+archiveName;
        alert("Connection lost with server. Please use this link after few minutes to download your archive.\n"+downloadUrl);
        eventSource.close();
}

function checkStateOfProcessing(){
    var archiveName = $("#archiveName").val();
    eventSource = new EventSource("checkProcessingStatus.php?archiveName="+archiveName);
    eventSource.addEventListener("open", initiateProcessPhaseCheck);
    eventSource.addEventListener("message", updateProcessPhase);
    eventSource.addEventListener("error", errorWhileCheckingProgress);
}

function submissionResult(result) {
    if(result == "success")
    {
        uploadPhaseDone();
        setTimeout(checkStateOfProcessing,10);
    }
    else
        alert(result+"\nPlease try again with proper inputs.");
}


$("form#mainForm").submit(function() {

    validateForm();
    $("html,body").animate({
        scrollTop: $("#uploadPhaseButton").offset().top
    },500);
    $("#uploadPhaseButton").addClass("pulse");
    $("#uploadPhaseIcon").html("loop");

    var formData = new FormData(this);
    
    $.ajax({
        url: window.location+$(this).attr("action"),
        type: 'POST',
        data: formData,
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert("Status: " + textStatus); alert("Error: " + errorThrown); 
        },
        success: submissionResult,
        timeout: function(event){
            alert("Couldn't upload data. Check your internet connection.");
        }
    });

    return false;
});