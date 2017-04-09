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
    $("#processingMainIcon").html("loop");
    $("#processingMainButton").removeClass("brown");
    $("#processingMainButton").addClass("pulse");
    $("#st1Icon").html("loop");
}

function validateForm() {
    if ($("input[name='mainSlideTitle']").val() == "")
        alert("Please enter slide title.");
    if ($("input[name='archiveName']").val() == "")
        alert("Please enter a name for archive.");
    if ($("input[name='resourceFile']").val() == "")
        alert("Please select a resource file.");    
}


function downloadArchive(){
    downloadData : {
        archiveName : $("#archiveName").val()
    }
    $.ajax({
        url: window.location.pathname+"getArchive.php",
        type: 'GET',
        async: true,
        data: downloadData,
        cache: false,
        contentType: false,
        processData: false
    });
    $("#downloadPhaseIcon").html("cloud_done");
}

function updateProcessPhase(result) {
    $("#"+result).addClass("teal-text");
    $("#"+result+"Icon").html("done");
    if(result != "download")
    {
        setTimeout(checkStageOfProcessing,100)
    }
    else
    {
        $("#processingMainIcon").html("done");
        $("#processingMainButton").removeClass("pulse");
        $("#downloadPhaseButton").removeClass("brown");
        $("#downloadPhaseButton").addClass("teal");
        $("#downloadPhaseButton").addClass("pulse");
        $("#downloadPhaseIcon").html("loop");
        //setTimeout(downloadArchive,1000);
    }
}

function checkStageOfProcessing(){
    $.ajax({
        url: window.location.pathname+"processedStages.txt",
        type: 'GET',
        async: true,
        success: updateProcessPhase,
        cache: false,
        contentType: false,
        processData: false
    });
}


function submissionResult(result) {
    switch(result) {
        case "success": 
                uploadPhaseDone();
                setTimeout(checkStageOfProcessing,100);
                break;
        default:
                uploadResult = result; 
                alert(result+"\nPlease try again with proper inputs.");
    }
}

$("form#mainForm").submit(function() {

    validateForm();

    $("#uploadPhaseButton").addClass("pulse");
    $("#uploadPhaseIcon").html("loop");

    var formData = new FormData(this);
    
    $.ajax({
        url: window.location.pathname+$(this).attr("action"),
        type: 'POST',
        data: formData,
        async: false,
        cache: false,
        contentType: false,
        processData: false,
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert("Status: " + textStatus); alert("Error: " + errorThrown); 
        },
        success: submissionResult,
        timeout: function() {
            alert("Timeout occured. Please check your internet connection.")
        }  
    });

    return false;
});