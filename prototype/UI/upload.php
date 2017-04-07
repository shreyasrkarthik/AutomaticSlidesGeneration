<?php
try {

    $output_file_name = $_POST["archiveName"];
    $target_dir = "uploads/".$output_file_name;
    mkdir($target_dir);
    $target_dir = $target_dir."/";
    $resource_file_target_path = null;
    $resource_file_name = null;
    $logo_file_target_path = null;
    $logo_file_name = null;

    ob_start();
    if(isset($_POST["resourceLinkChoosen"]))
    {
        $resource_url = $_POST["resourceFile"];
        $resource_file = file_get_contents($resource_url);
        $resource_file_name = explode("/", $resource_url);
        $resource_file_name = $resource_file_name[count($resource_file_name)-1];
        $resource_file_target_path = $target_dir.$resource_file_name;
        file_put_contents($resource_file_target_path, $resource_file);
    }
    else
    {   
        if (
            !isset($_FILES['resourceFile']['error']) ||
            is_array($_FILES['resourceFile']['error'])
        ) {
          throw new RuntimeException("wrong parameters");
        }

        switch ($_FILES['resourceFile']['error']) {
            case UPLOAD_ERR_OK:
                break;
            case UPLOAD_ERR_NO_FILE:
                throw new RuntimeException("no resource file sent");
            default:
                throw new RuntimeException("unknown errors");
        }

        $allowed_resource_extensions = array(
                'application/pdf', //pdf file
                'text/plain', //text file
            );

        $resource_file_name = $_FILES['resourceFile']['name'];
        $resource_file_tmp_path = $_FILES["resourceFile"]["tmp_name"];
        $resource_file_target_path = $target_dir.$resource_file_name;

        $finfo_object = finfo_open(FILEINFO_MIME_TYPE);
        $mime_type_detected = finfo_file($finfo_object, $resource_file_tmp_path);
        if (!in_array($mime_type_detected, $allowed_resource_extensions))
        {
            throw new RuntimeException("wrong resource file format");
        }
        if (!move_uploaded_file($resource_file_tmp_path, $resource_file_target_path)) 
        {
            throw new RuntimeException("could not move resource file");
        }
    }

    if(isset($_POST["logoLinkChoosen"]))
    {
        $logo_url = $_POST["logoFile"];
        $logo_file = file_get_contents($logo_url);
        $logo_file_name = explode("/", $logo_url);
        $logo_file_name = $logo_file_name[count($logo_file_name)-1];
        $logo_file_target_path = $target_dir.$logo_file_name;
        file_put_contents($logo_file_target_path, $logo_file);
    }
    else
    {   
        if (
            !isset($_FILES['logoFile']['error']) ||
            is_array($_FILES['logoFile']['error'])
        ) {
          throw new RuntimeException("wrong parameters");
        }

        switch ($_FILES['logoFile']['error']) {
            case UPLOAD_ERR_OK:
                break;
            case UPLOAD_ERR_NO_FILE:
                throw new RuntimeException("no logo sent");
            default:
                throw new RuntimeException("unknown errors");
        }

        $allowed_logo_extensions = array(
                'image/gif',
                'image/jpeg',
                'image/png',
                'image/x-icon'
            );

        $logo_file_name = $_FILES['logoFile']['name'];
        $logo_file_tmp_path = $_FILES["logoFile"]["tmp_name"];
        $logo_file_target_path = $target_dir.$logo_file_name;

        $finfo_object = finfo_open(FILEINFO_MIME_TYPE);
        $mime_type_detected = finfo_file($finfo_object, $logo_file_tmp_path);
        if (!in_array($mime_type_detected, $allowed_logo_extensions))
        {
            throw new RuntimeException("wrong logo file format");
        }

        if (!move_uploaded_file($logo_file_tmp_path, $logo_file_target_path)) 
        {
            throw new RuntimeException("could not move logo file");
        }
    }

    echo "success";

    ob_end_flush();
    flush();

    file_put_contents("processedStages.txt", "st1"); //let it be st1
    // // require "process.php"; 
    
} catch (RuntimeException $e) {
    echo $e->getMessage();
}
?>