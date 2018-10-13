<?php

$DELI = '____';

function _log($content, $theDeli) {
	$dt = new DateTime("now", new DateTimeZone('Asia/Shanghai'));
	$now = $dt->format('Y-m-d H:i:s');
	$fnow = $dt->format('Ymd');
	$filePath = '/var/www/html/logs/diabetes.'.$fnow.'.log';
echo $filePath;
	$fp = fopen($filePath, 'a');
	$line = $now.$theDeli.$content."\n";
	fwrite($fp, $line);
	fclose($fp);
}

try {
	$reqJson = file_get_contents('php://input');
	$req = json_decode($reqJson, true);
	$ua = $req['ua'];
	$url = $req['url'];
	$referrer = $req['referrer'];
	$ip = $_SERVER['REMOTE_ADDR'];
	$content = $ua.$DELI.$url.$DELI.$ip.$DELI.$referrer;
	_log($content, $DELI);
	echo 'OK';
} catch (Exception $e) {
	echo 'ERROR';
}

?>
