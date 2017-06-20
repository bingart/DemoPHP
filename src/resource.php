<?php

$mysqli = new mysqli('localhost', 'root', '', 'art');
if ($mysqli->connect_errno) {
    echo "Error: Failed to make a MySQL connection, here is why: \n";
    echo "Errno: " . $mysqli->connect_errno . "\n";
    echo "Error: " . $mysqli->connect_error . "\n";
    exit;
}

$sql = 'SELECT * FROM tb_resource';
if (!$result = $mysqli->query($sql)) {
    echo "Error: Our query failed to execute and here is why: \n";
    echo "Query: " . $sql . "\n";
    echo "Errno: " . $mysqli->errno . "\n";
    echo "Error: " . $mysqli->error . "\n";
	exit;
}

if ($result->num_rows === 0) {
    echo "We could not find result.";
    exit;
}

$urlItemList = array ();
$i = 0;
while ($row = $result->fetch_row()) {
	$url = $row[1];
	$loadTime = $row[2];
	$urlItemList[$i] = array ("url" => $url, "loadExpiredTime" => $loadTime);
	$i++;
}

$result->free();
$mysqli->close();

$data = array(
    "errorCode" => "OK",
    "urlItemList" => $urlItemList
);

$json = json_encode($data);
echo $json;

?>