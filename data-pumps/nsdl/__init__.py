

#ALL_METADATA_URL_NSDL_DC = "http://www.dls.ucar.edu/dds_se/services/oai2-0?verb=ListRecords&metadataPrefix=nsdl_dc&set=ncs-NSDL-COLLECTION-000-003-112-016"
ALL_METADATA_URL_NSDL_DC = "http://www.dls.ucar.edu/dds_se/services/oai2-0"

LR_NSDL_DC_NAMESPACES = {
    'oai': 'http://www.openarchives.org/OAI/2.0/',
    'nsdl_dc':"http://ns.nsdl.org/nsdl_dc_v1.02/", 
    'ieee':"http://www.ieee.org/xsd/LOMv1p0",
    'dct':"http://purl.org/dc/terms/",
    'dc':"http://purl.org/dc/elements/1.1/",
    'xsi':"http://www.w3.org/2001/XMLSchema-instance" 
}

LR_NSDL_DC_FIELDS = {
    'payload_locator_id' : ('textList', 'oai:header/oai:identifier/text()'),
    'resource_timestamp': ('textList', 'oai:header/oai:datestamp/text()'),
    'resource_locator': ( 'textList', 'nsdl_dc:nsdl_dc/dc:identifier/text()' ),
    'resource_title': ( 'textList', 'nsdl_dc:nsdl_dc/dc:title/text()' ),
    'resource_subject': ( 'textList', 'nsdl_dc:nsdl_dc/dc:subject/text()'),                     # list
    'resource_language': ( 'textList', 'nsdl_dc:nsdl_dc/dc:language/text()' ),                  # list
    'resource_education_level': ( 'textList', 'nsdl_dc:nsdl_dc/dct:educationLevel/text()' ),    
    'resource_type': ( 'textList', 'nsdl_dc:nsdl_dc/dc:type/text()'),
    'resource_description': ( 'textList', 'nsdl_dc:nsdl_dc/dc:description/text()' ),
    'resource_owner': ( 'textList', 'nsdl_dc:nsdl_dc/dc:publisher/text()' ),
    'resource_rights': ( 'textList', 'nsdl_dc:nsdl_dc/dc:rights/text()'),
}


NSDL_TO_LR_MAP = {

    "active":                       { "type": "boolean", "fields": []},                   ## true or false
    "doc_ID":                       { "type": "string", "fields": []},                    ## CouchDb ID
    "doc_type":                     { "type": "const", "const": "resource_data", "fields": []},
    "doc_version":                  { "type": "const", "const": "0.10.0", "fields": []},
    "first_timestamp":              { "type": "string", "fields": []},                   ## time when first published into the network
    "frbr_level":                   { "type": "string", "fields": []},                 ## work, expression, manifestation, copy
    "payload_placement":            { "type": "string", "fields": []},                   ## inline, linked, attached
    "payload_schema":               { "type": "[string]", "fields": []},              ## payload format
    "publish_timstamp":             { "type": "string", "fields": []},                   ## time when published into the network
    "publishing_node":              { "type": "string", "fields": []},                   ## node id where first injected into the network
    "resource_data":                { "type": "string", "fields": []},                   ## inline payload data
    "resource_data_type":           { "type": "string", "fields": []},              ## metadata, paradata, resource
    "resource_descripton":          { "type": "string", "fields": ["resource_description"]},
    "resource_distribution_rights": { "type": "string", "fields": []},
    "resource_format":              { "type": "[string]", "fields": []},
    "resource_language":            { "type": "[string]", "fields": ["resource_language"]},
    "resource_licence_url":         { "type": "string", "fields": []},
    "resource_license_hint":        { "type": "string", "fields": []},
    "resource_locator":             { "type": "string", "fields": ["resource_locator"]},                   ## unique owner
    "resource_owner":               { "type": "string", "fields": ["resource_owner"]},
    "resource_preview":             { "type": "string", "fields": []},
    "resource_pricing":             { "type": "string", "fields": []},
    "resource_rights":              { "type": "[string]", "fields": ["resource_rights"]},
    "resource_subject":             { "type": "[string]", "fields": ["resource_subject", "resource_education_level"]},
    "resource_title":               { "type": "string", "fields": ["resource_title"]},
    "resource_type":                { "type": "string", "fields": ["resource_type"]},
    "submission_TOS":               { "type": "string", "fields": []},                   ## agreed tos by submitter
    "submitter":                    { "type": "string", "fields": []},                 ## identity of the submitter
    "submitter_timestamp":          { "type": "string", "fields": ["resource_timestamp"]},                ## anonymous, user, agent
    "submitter_type":               { "type": "string", "fields": []},                ## anonymous, user, agent

}


LR_NSDL_PREFIX = 'nsdl_dc'