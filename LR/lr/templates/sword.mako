<?xml version="1.0" encoding='utf-8'?>
<service xmlns="http://www.w3.org/2007/app"
         xmlns:atom="http://www.w3.org/2005/Atom"
	 xmlns:sword="http://purl.org/net/sword/"
	 xmlns:dcterms="http://purl.org/dc/terms/">

 <sword:version>1.3</sword:version>
 <workspace>
   <atom:title>Learning Registry</atom:title>
   <collection
       href="${c.collectino_url}" >
     <atom:title>Learning Registry</atom:title>
     <accept>application/json</accept>
     <sword:collectionPolicy>${c.tos_url}</sword:collectionPolicy>
     <dcterms:abstract>Learning Registry</dcterms:abstract>
   </collection>
 </workspace>
</service>

