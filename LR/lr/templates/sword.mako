<?xml version="1.0" encoding='utf-8'?>
<service xmlns="http://www.w3.org/2007/app"
         xmlns:atom="http://www.w3.org/2005/Atom"
	 xmlns:sword="http://purl.org/net/sword/"
	 xmlns:dcterms="http://purl.org/dc/terms/">

 <sword:version>1.3</sword:version>
 <workspace>

   <atom:title>Main Site</atom:title>
   <collection
       href="http://www.myrepository.ac.uk/atom/geography-collection" >
     <atom:title>My Repository : Geography Collection</atom:title>
     <accept>application/zip</accept>
     <sword:collectionPolicy>Collection Policy</sword:collectionPolicy>
     <dcterms:abstract>Collection description</dcterms:abstract>
     <sword:acceptPackaging q="1.0">http://purl.org/net/sword-types/METSDSpaceSIP</sword:acceptPackaging>
     <sword:acceptPackaging q="0.8">http://purl.org/net/sword-types/bagit</sword:acceptPackaging>
   </collection>

 </workspace>
</service>

