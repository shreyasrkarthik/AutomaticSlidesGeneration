<?php

$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin
   1 => array("pipe", "w"),  // stdout
   2 => array("pipe", "w"),  // stderr
);

if($mime_type_detected == $allowed_resource_extensions[0] ) // if PDF was uploaded
{
    $command = escapeshellcmd('../parser/PdftoText.py '. $resource_file_target_path. ' convertedText.txt');
    $output = shell_exec($command);
}
else // if text was uploaded
{
    $command = escapeshellcmd('mv '. $resource_file_target_path. ' convertedText.txt');
    $output = shell_exec($command);
}

$command = escapeshellcmd('../src/driver.py convertedText.txt');
$output = shell_exec($command);

$process = proc_open(' python ../src/driver.py ../UI/convertedText.txt', $descriptorspec, $pipes, dirname(__FILE__), null);

$stdout = stream_get_contents($pipes[1]);
fclose($pipes[1]);

$stderr = stream_get_contents($pipes[2]);
fclose($pipes[2]);

echo "stdout : \n";
var_dump($stdout);

echo "stderr :\n";
var_dump($stderr);

file_put_contents("processedStages.txt", "download"); // marks that processing is done


?>	