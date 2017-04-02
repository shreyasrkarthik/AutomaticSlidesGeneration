<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
echo "The file ". basename( $_FILES["fileToUpload"]["name"]). " has been uploaded.";
$command = escapeshellcmd('../parser/PdftoText.py '. $target_file. ' convertedText.txt');
$output = shell_exec($command);
// echo $output;

?>	