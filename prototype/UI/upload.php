<?php
    try {
        $directory_name = $_POST["archiveName"];
        
        $input_directory = "uploads/".$directory_name;
        shell_exec("mkdir -m 777 ".$input_directory);
        $input_directory = $input_directory."/";
        
        $output_directory = "outputs/".$directory_name;
        shell_exec("mkdir -m 777 ".$output_directory);
        $output_directory = $output_directory."/";
        
        $resource_file_path = $resource_file_name = $resource_mime_type = null;
        $logo_file_path = $logo_file_name = $logo_mime_type = null;
        
        $pages_selected = null;
        if(isset($_POST["pagesSelected"]))
        {
            $pages_selected = $_POST["pagesSelected"];
            $pages_selected = str_replace(" ", "", $pages_selected);
        }

        $main_slide_title = $_POST["mainSlideTitle"];

        $main_slide_subtitle = null;
        if(isset($_POST["mainSlideSubtitle"])) 
        {
            $footer_text = $_POST["mainSlideSubtitle"];
        }

        $footer_text = null;
        if(isset($_POST["footerText"])) 
        {
            $footer_text = $_POST["footerText"];
        }

        $allowed_resource_extensions = array(
            'application/pdf', //pdf file
            'text/plain', //text file
        );
        $allowed_logo_extensions = array(
            'image/gif',
            'image/jpeg',
            'image/png',
            'image/x-icon'
        );

        ob_start();
        if(isset($_POST["resourceFile"])||isset($_FILES["resourceFile"]))
        {
            if(isset($_POST["resourceLinkChoosen"]))
            {
                $resource_url = $_POST["resourceFile"];
                $resource_file = file_get_contents($resource_url);
                $resource_file_name = explode("/", $resource_url);
                $resource_file_name = $resource_file_name[count($resource_file_name)-1];
                $resource_file_path = $input_directory.$resource_file_name;
                file_put_contents($resource_file_path, $resource_file);
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

                $resource_file_name = $_FILES['resourceFile']['name'];
                $resource_file_tmp_path = $_FILES["resourceFile"]["tmp_name"];
                $resource_file_path = $input_directory.$resource_file_name;

                if (!move_uploaded_file($resource_file_tmp_path, $resource_file_path)) 
                {
                    throw new RuntimeException("could not move resource file");
                }
            }
            $finfo_object = finfo_open(FILEINFO_MIME_TYPE);
            $resource_mime_type = finfo_file($finfo_object, $resource_file_path);
            if (!in_array($resource_mime_type, $allowed_resource_extensions))
            {
                throw new RuntimeException("wrong resource file format");
            }
            chmod($resource_file_path, 777);
        }

        if(isset($_POST["logoFile"])||isset($_FILES["logoFile"]))
        {
            if(isset($_POST["logoLinkChoosen"]))
            {
                $logo_url = $_POST["logoFile"];
                $logo_file = file_get_contents($logo_url);
                $logo_file_name = explode("/", $logo_url);
                $logo_file_name = $logo_file_name[count($logo_file_name)-1];
                $logo_file_path = $input_directory.$logo_file_name;
                file_put_contents($logo_file_path, $logo_file);
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

                $logo_file_name = $_FILES['logoFile']['name'];
                $logo_file_tmp_path = $_FILES["logoFile"]["tmp_name"];
                $logo_file_path = $input_directory.$logo_file_name;

                if (!move_uploaded_file($logo_file_tmp_path, $logo_file_path)) 
                {
                    throw new RuntimeException("could not move logo file");
                }
            }
            $finfo_object = finfo_open(FILEINFO_MIME_TYPE);
            $logo_mime_type = finfo_file($finfo_object, $logo_file_path);
            if (!in_array($logo_mime_type, $allowed_logo_extensions))
            {
                throw new RuntimeException("wrong logo file format");
            }
            chmod($logo_file_path, 777);
        }

        echo "success";
        ob_end_flush();
        flush();
        
        require "process.php";

    } catch (RuntimeException $e) {
        echo $e->getMessage();
    }
?>