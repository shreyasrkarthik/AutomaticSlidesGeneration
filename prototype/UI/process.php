<?php
    file_put_contents("processedStages.txt", "uploaded");

    $command = escapeshellcmd("cp ".$resource_file_path." ".$output_directory);
    exec($command);

    $target_text_file = $output_directory."convertedText.txt";

    if($resource_mime_type == $allowed_resource_extensions[0] ) // if PDF was uploaded
    {
        $command = '../parser/PdftoText.py -I '.$resource_file_path.' -O '.$target_text_file;
        if(!is_null($pages_selected))
            $command .= " -P ".$pages_selected;
        $command = escapeshellcmd($command);
        $pages_selected = explode(",", $pages_selected);
        for ($i=0; $i < count($pages_selected); $i++) { 
            $pages = explode("-", $pages_selected[$i]);
            $first_page = $pages[0];
            $last_page = $pages[1];
            $command = "pdftohtml -c -f ".$first_page." -l ".$last_page." ".$output_directory.$resource_file_name;
            $command = escapeshellcmd($command);
            shell_exec($command);
        }
        shell_exec("rm ".$output_directory."*.html");
    }
    else if($resource_mime_type == $allowed_resource_extensions[1] )// if text was uploaded
    {
        $command = escapeshellcmd('mv '. $resource_file_path." ".$target_text_file);
        $output = shell_exec($command);
    }
    chmod($target_text_file, 777);
    file_put_contents("processedStages.txt", "st1");

    $slides_path = $output_directory.$directory_name.".pptx";

    $command = "../src/driver.py -I ".$target_text_file." -O ".$slides_path." -T ".$main_slide_title;
    if(!is_null($main_slide_subtitle))
        $command .= " -S ".$main_slide_subtitle;
    if(!is_null($logo_mime_type))
        $command .= " -L ".$logo_file_path;
    if(!is_null($footer_text))
        $command .= " -F ".$footer_text;
    
    $command = escapeshellcmd($command);
    shell_exec($command);

    file_put_contents("processedStages.txt", "st3"); // marks that processing is done
?>