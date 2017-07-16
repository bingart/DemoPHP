<?php
/* ********************************************** */
/* This file is used to upload page html files */
/* ********************************************** */

$name = $_POST["name"];
$base64 = $_POST["content"];
$content = base64_decode($base64);
echo 'name=' . $name . '\r\n';
echo 'base64=' . $base64 . '\r\n';

$s0 = substr($name, 0, 1);
$s1 = substr($name, 1, 1);
$s2 = substr($name, 2, 1);
$rootPath = "E:/Site";

$folder = $rootPath . '/' . $s0 . '/' . $s1 . '/' . $s2;
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