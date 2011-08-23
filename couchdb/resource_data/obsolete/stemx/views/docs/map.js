function (doc) {
	if (doc._id && doc._id.indexOf("_design/") == -1) {
		emit(null, doc);
	}
}