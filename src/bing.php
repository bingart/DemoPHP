<?php

/*
	Bing Search Service.
*/

$opts = array(
  'http'=>array(
    'method'=>"GET",
    'header'=>"Accept-language: en\r\n"
  )
);
$context = stream_context_create($opts);

if (isset($_GET['q']) && isset($_GET['token'])) {
	$q = $_GET['q'];
	$token = $_GET['token'];
	if ($token != "bingart") {
		echo "{'errorCode':'invalid token'}";
	} else {
		$url = "https://www.bingapis.com/api/v4/search?appid=&mkt=en-US&count=20&offset=0&q=" . $q;
		$response = file_get_contents($url, false, $context);
		$jsonobj = json_decode($response);
		echo $response;
	}
} else {
	echo "{}";	
}

?>