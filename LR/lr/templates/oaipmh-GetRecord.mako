# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?> 
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>${c.datetime_now | x}</responseDate>
  <request verb="GetRecord" identifier="${c.doc["doc_ID"] | x}"
           metadataPrefix="${c.metadataPrefix | x}">${c.path_url | x}</request>
  <GetRecord>
   <record> 
    <header>
      <identifier>${c.doc["doc_ID"] | x}</identifier> 
      <datestamp>${c.doc["create_timestamp"] | x}</datestamp>
    </header>
    <metadata>
      ${c.doc["resource_data"] | n}
    </metadata>
  </record>
 </GetRecord>
</OAI-PMH>