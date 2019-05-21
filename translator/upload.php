<?php
/*
Get Post.
*/

# live

function _upload_post($req) {
	try {
		// load template
		$html = file_get_contents("template.html");
		$html = str_replace("{title}", $req->title, $html);
		$html = str_replace("{content}", $req->content, $html);
		
		$uid = md5($req->url);
		$len = strlen($uid);
		$prefix = substr($uid, 0, 1);

		$dirPath = __DIR__."/".$prefix;
		if (!file_exists($dirPath)) {
			mkdir($dirPath, 0755, true);
		}

		$filePath = $dirPath.'/'.$uid.".html";
#echo 'filePath='.$filePath;
		$fileUrl = $_SERVER['REQUEST_SCHEME']."://".$_SERVER['HTTP_HOST'].str_replace("upload.php", "", $_SERVER['REQUEST_URI']).$prefix."/".$uid.".html";
		file_put_contents($filePath, $html);
		
		return array(
			"errorCode" => "OK",
			"errorMessage" => "",
			"url" => $req->url,
			"fileUrl" => $fileUrl,
		);
	} catch (Exception $e) {
		return array(
			"errorCode" => "ERROR",
			"errorMessage" => $e->getMessage(),
			"url" => $req->url,
			"fileUrl" => "",
		);
	}	
}

$entityBody = file_get_contents('php://input');
$req = json_decode($entityBody);
$result = _upload_post($req);
echo json_encode($result);	
?>
