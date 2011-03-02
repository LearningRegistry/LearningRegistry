function (doc) {
	/*
	 * map that creates a view of filtering keys for metadata only.  allows us to figure out what we can
	 * search by.
	 */
	if (doc.resource_data_type && doc.resource_data_type === "metadata" && doc.filtering_keys) {
		used = {};
		for (i=0; i<doc.filtering_keys.length; i++) {
			if (!used[doc.filtering_keys[i]]) {
				used[doc.filtering_keys[i]] = true;
				emit(doc.filtering_keys[i], doc);
			}
		}
	}
	
}