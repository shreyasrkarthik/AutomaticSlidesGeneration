<?php
    
  header("Content-Type: text/event-stream");
  header("Cache-Control: no-cache");
  header("Access-Control-Allow-Origin: *");

  $lastEventId = floatval(isset($_SERVER["HTTP_LAST_EVENT_ID"]) ? $_SERVER["HTTP_LAST_EVENT_ID"] : 0);
  if ($lastEventId == 0) {
    $lastEventId = floatval(isset($_GET["lastEventId"]) ? $_GET["lastEventId"] : 0);
  }
  $file_name = "outputs/".$_GET["archiveName"]."/processedStages.txt";

  $old_time = filemtime($file_name);
  clearstatcache();

  echo ":" . str_repeat(" ", 2048) . "\n"; // 2 kB padding for IE
  echo "retry: 2000\n";

  // event-stream
  $i = $lastEventId;
  $c = $i + 100;
  while (++$i < $c) {
    $new_time = filemtime($file_name);
    clearstatcache();
    if($new_time > $old_time)
    {
      $contents = file_get_contents($file_name);
      echo "id: " . $i . "\n";
      echo "data: " . $contents . "\n\n";
      ob_flush();
      flush();
      $old_time = $new_time;
    }
    sleep(1);
  }

?>