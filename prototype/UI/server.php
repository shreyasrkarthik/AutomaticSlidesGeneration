<?php
// $target_dir = "uploads/";
// $target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
// move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
// echo "The file ". basename( $_FILES["fileToUpload"]["name"]). " has been uploaded.";
// $command = escapeshellcmd('../parser/PdftoText.py '. $target_file. ' convertedText.txt');
// $output = shell_exec($command);

// $command = escapeshellcmd('../src/driver.py convertedText.txt');
// $output = shell_exec($command);
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin
   1 => array("pipe", "w"),  // stdout
   2 => array("pipe", "w"),  // stderr
);

exec('cd ../src/');
// echo getcwd()
$process = proc_open(' python ../src/driver.py ../UI/convertedText.txt', $descriptorspec, $pipes, dirname(__FILE__), null);

$stdout = stream_get_contents($pipes[1]);
fclose($pipes[1]);

$stderr = stream_get_contents($pipes[2]);
fclose($pipes[2]);

echo "stdout : \n";
var_dump($stdout);

echo "stderr :\n";
var_dump($stderr);

// echo $output;

?>	