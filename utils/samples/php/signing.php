<?php
require_once 'Crypt/GPG.php';
require_once 'bencode.php';
function sign_file($filedata){
	
	$gpg = new Crypt_GPG();
	$gpg->addSignKey('wegrata@gmail.com');
	$signature = $gpg->sign($filedata, Crypt_GPG::SIGN_MODE_CLEAR);
	return $signature;
}
function import_key($key_url){	
	$gpg = new Crypt_GPG();
	$gpg->importKeyFile($key_url);
}
function normalize_data($data)
{
	if (is_null($data)){		
		return "null";
	} else if (is_numeric($data)){
		return strval($data);
	} else if (is_bool($data)){ 
		return $data ? "true" : "false";
	}else if(is_array($data)){
		foreach($data as $subKey => $subValue){
			$data[$subKey] = normalize_data($subValue);
		}
	}		
	return $data;
}
function format_data_to_sign($rawData){
    
	unset($rawData['digital_signature']);
	
	unset($rawData['_id']);
	unset($rawData['_rev']);
	
	unset($rawData['doc_ID']);
	unset($rawData['publishing_node']);
	unset($rawData['update_timestamp']);
	unset($rawData['node_timestamp']);
	unset($rawData['create_timestamp']);
	
	$rawData = normalize_data($rawData);
	$encoder = new bencoding();
	$data = utf8_encode($encoder->encode($rawData));
	$hash = hash('SHA256',$data);
	return $hash;	
}
function verify_file($filedata, $signature){
	$gpg = new Crypt_GPG();
	$results = $gpg->verify( $signature);	
	return $results;
}
function read_file($filename){
	$handle = fopen($filename,'r');
	$data = fread($handle,filesize($filename));
	fclose($handle);
	return $data;
}
function write_file($filename,$data){
	$handle = fopen($filename,'w');
	fwrite($handle,$data);
	fclose($handle);
}
function get_hash_from_signature($signature){
	$parts = preg_split('[\r|\n]',$signature);	
	return $parts[3];
}
function test_verify($filename){
	$data = read_file($filename);
	$json = json_decode($data, true);
	import_key($json['digital_signature']['key_location'][0]);
	$signature = $json['digital_signature']['signature'];
	$testHash = get_hash_from_signature($signature);
	$signData = format_data_to_sign($json);
	if($signData == $testHash){
		$resultList = verify_file($data, $signature);
		$result = $resultList[0];
		if( $result->isValid()){
			echo "Valid", "\n";
		}
	}
}
function test_signing($filename,$outfile){
	$data = read_file($filename);
	$json = json_decode($data, true);
	$signData = format_data_to_sign($json);
	$signature = sign_file($signData);	
	$json['digital_signature'] = array(
		'key_location' => array('http://12.109.40.15/resource_data/key/key.asc'),
		'signature' => $signature,
		'key_owner' => 'wegrata@gmail.com',
		'signing_method' => 'LR-PGP.1.0'
	);
	$jsonString = json_encode($json);
	write_file($outfile,$jsonString);
}

$testFile = '2011-02-28Metadata10.json';
$signedFile = 'signedOutput.json';
test_signing($testFile,$signedFile);
test_verify($signedFile);
?>

