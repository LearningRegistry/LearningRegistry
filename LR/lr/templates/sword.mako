<?xml version="1.0" encoding='utf-8'?>
<service xmlns="http://www.w3.org/2007/app"
         xmlns:atom="http://www.w3.org/2005/Atom"
	 xmlns:sword="http://purl.org/net/sword/"
	 xmlns:dcterms="http://purl.org/dc/terms/">

 <sword:version>1.3</sword:version>
 <sword:verbose>true</sword:verbose>
 <sword:noOp>true</sword:noOp>
 <workspace>
   <atom:title>${c.community_name}</atom:title>
   <collection href="${c.collection_url}" >
     <atom:title>${c.node_name}</atom:title>
     <accept>application/json</accept>
     <sword:mediation>true</sword:mediation>
     % if c.node_description is not None:
     <dcterms:abstract>${c.node_description}</dcterms:abstract>
     % endif
     <sword:collectionPolicy>${c.tos_url}</sword:collectionPolicy>
   </collection>
 </workspace>
</service>

