<?php
    function Zip($source, $destination)
    {
        if (!extension_loaded('zip') || !file_exists($source)) {
            return false;
        }

        $zip = new ZipArchive();
        if (!$zip->open($destination, ZIPARCHIVE::CREATE)) {
            return false;
        }

        $source = str_replace('\\', '/', realpath($source));

        if (is_dir($source) === true)
        {
            $files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($source), RecursiveIteratorIterator::SELF_FIRST);

            foreach ($files as $file)
            {
                $file = str_replace('\\', '/', $file);

                // Ignore "." and ".." folders
                if( in_array(substr($file, strrpos($file, '/')+1), array('.', '..')) )
                    continue;

                $file = realpath($file);

                if (is_dir($file) === true)
                {
                    $zip->addEmptyDir(str_replace($source . '/', '', $file . '/'));
                }
                else if (is_file($file) === true)
                {
                    $zip->addFromString(str_replace($source . '/', '', $file), file_get_contents($file));
                }
            }
        }
        else if (is_file($source) === true)
        {
            $zip->addFromString(basename($source), file_get_contents($source));
        }

        return $zip->close();
    }

    $folderName = $_GET["archiveName"];
    $outputFolderPath = "outputs/$folderName";

    $outputFolderPath = realpath($outputFolderPath);
    $retval = unlink("$outputFolderPath/processedStages.txt");

    $command = "mv $outputFolderPath/convertedText.txt $outputFolderPath/data.txt";
    shell_exec(escapeshellcmd($command));

    $zipname = "$folderName.zip";
    $outputZipFilePath = "outputs/$zipname";

    shell_exec(escapeshellcmd($outputFolderPath));

    Zip($outputFolderPath, $outputZipFilePath);

    header('Content-Type: application/zip');
    header('Content-disposition: attachment; filename='.$outputZipFilePath);
    header('Content-Length: ' . filesize($outputZipFilePath));
    readfile($outputZipFilePath);
?>