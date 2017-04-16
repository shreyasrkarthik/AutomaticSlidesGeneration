<?php
    try {

        $directory_name = $_POST["archiveName"];
        $directory_name = str_replace(" ", "_", $directory_name);

        $input_directory = "uploads/$directory_name";
        shell_exec("mkdir -m 777 ".$input_directory);
        $input_directory = $input_directory."/";

        $output_directory = "outputs/$directory_name";
        shell_exec("mkdir -m 777 $output_directory");
        $output_directory = "$output_directory/";

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
            $main_slide_subtitle = $_POST["mainSlideSubtitle"];
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
            chmod($resource_file_path, 0777);
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
            chmod($logo_file_path, 0777);
        }

        ignore_user_abort(true);
        ob_start();
        echo "success";
        $buffer_size = ob_get_length();
        session_write_close();
        header("Content-Encoding: none");
        header("Content-Length: $buffer_size");
        header("Connection: close");
        ob_end_flush();
        ob_flush();
        flush();

        sleep(2);
        ob_start();

        $command = escapeshellcmd("cp $resource_file_path $output_directory");
        exec($command);

        $target_text_file = $output_directory."convertedText.txt";

        if($resource_mime_type == $allowed_resource_extensions[0] ) // if PDF was uploaded
        {
            $command = "../parser/PdftoText.py -I $resource_file_path -O $target_text_file";
            if(!is_null($pages_selected))
                $command .= " -P $pages_selected";
            $command = escapeshellcmd($command);
            shell_exec($command);
            $pages_selected = explode(",", $pages_selected);
            for ($i=0; $i < count($pages_selected); $i++) { 
                $pages = explode("-", $pages_selected[$i]);
                $first_page = $pages[0];
                $last_page = $pages[1];
                $command = "pdftohtml -c -f $first_page -l $last_page $output_directory"."$resource_file_name";
                $command = escapeshellcmd($command);
                shell_exec($command);
            }
            shell_exec("rm $output_directory*.html");
        }
        else if($resource_mime_type == $allowed_resource_extensions[1] )// if text was uploaded
        {
            $command = escapeshellcmd("mv $resource_file_path $target_text_file");
            $output = shell_exec($command);
        }
        chmod($target_text_file, 0777);

        $process_status_file = $output_directory."processedStages.txt";
        file_put_contents($process_status_file, "st1");
        chmod($process_status_file, 0777);
        sleep(2);

        $slides_path = $output_directory.$directory_name;

        $command = "../src/driver.py -P $process_status_file -I $target_text_file -O $slides_path -T '".$main_slide_title."'";
        if(!is_null($main_slide_subtitle))
            $command .= " -S '".$main_slide_subtitle."'";
        if(!is_null($logo_mime_type))
            $command .= " -L ".$logo_file_path;
        if(!is_null($footer_text))
            $command .= " -F '".$footer_text."'";
        $command = escapeshellcmd($command);
        shell_exec($command);

        $command = "mv $target_text_file $output_directory/data.txt";
        shell_exec(escapeshellcmd($command));

        sleep(2);

    } catch (RuntimeException $e) {
        ob_start();
        echo $e->getMessage();
        ob_end_flush();
        flush();
    }
?>