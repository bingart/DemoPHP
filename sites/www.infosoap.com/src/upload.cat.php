<?php
/* ********************************************** */
/* This file is used to upload page html files */
/* ********************************************** */

// ##########################################
// ########### ROOT PATH ####################
// ##########################################
$rootPath = "E:/Site";

// $body = file_get_contents('php://input');
$body = '';
$fh   = @fopen('php://input', 'r');
if ($fh)
{
  while (!feof($fh))
  {
    $s = fread($fh, 1024);
    if (is_string($s))
    {
      $body .= $s;
    }
  }
  fclose($fh);
}
//echo 'body=' . $body . '\r\n';
$array = explode(';', $body);
$name = $array[0];
$base64 = $array[1];

$content = base64_decode($base64);
echo 'name=' . $name . '\r\n';
echo 'content.len=' . strlen($content) . '\r\n';

$s0 = substr($name, 0, 1);
$s1 = substr($name, 1, 1);
$s2 = substr($name, 2, 1);

$folder = $rootPath . '/' . $s0 . '/' . $s1 . '/' . $s2;
$folder = $rootPath;
echo 'folder=' . $folder . '\r\n';
if (!file_exists($folder)) {
	mkdir($folder, 0777, true);
}

$path = $folder . '/' . $name;
echo 'path=' . $path . '\r\n';

$fp = fopen($path, 'w');
fwrite($fp, $content);
fclose($fp);

echo "OK";

?>