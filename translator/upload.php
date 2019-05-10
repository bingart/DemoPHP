<?php
/*
upload post for tran.
*/

# live
# curl -XPOST -H"Content-Type:application/json" http://heartnlung.com/upload.php -d"{\"title\": \"the title\", \"content\": \"the content\"}"

function _upload_post($req) {
	try {
		// load template
		$html = file_get_contents("template.html");
		$html = str_replace("{title}", $req->title, $html);
		$html = str_replace("{content}", $req->content, $html);
		
		$uid = uniqid();
		$len = strlen($uid);
		$prefix = substr($uid, $len - 1, 1);

		$dirPath = __DIR__."/".$prefix;
		if (!file_exists($dirPath)) {
			mkdir($dirPath, 0755, true);
		}

		$filePath = $dirPath.'/'.$uid.".html";
		$fileUrl = $_SERVER['REQUEST_SCHEME']."://".$_SERVER['HTTP_HOST'].str_replace("upload.php", "", $_SERVER['REQUEST_URI']).$prefix."/".$uid.".html";
		file_put_contents($filePath, $html);
		
		return array(
			"errorCode" => "OK",
			"errorMessage" => "",
			"url" => $fileUrl,
		);
	} catch (Exception $e) {
		return array(
			"errorCode" => "ERROR",
			"errorMessage" => $e->getMessage(),
			"url" => "",
		);
	}	
}

$entityBody = file_get_contents('php://input');
$req = json_decode($entityBody);
$result = _upload_post($req);
echo json_encode($result);	
?>
