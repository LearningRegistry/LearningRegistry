# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>${c.error.datetime_now | x}</responseDate>
  % if hasattr(c.error, 'verb'):
  <request verb="${c.error.verb | x}">${c.error.path_url | x}</request>
  % else:
  <request>${c.error.path_url | x}</request>
  % endif
  <error code="${c.error.code | x}">${c.error.msg | x}</error>
</OAI-PMH>