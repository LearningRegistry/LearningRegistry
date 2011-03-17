function (key, values, rereduce) {
	if (rereduce == false) {
		var urlMap = {};
		for (var i=0; i<values.length; i++) {
			urlMap[values[i]] = true;
		}
		var urlSet = [];
		for (url in urlMap) {
			urlSet[urlSet.length] = url;
		}
		return urlSet;
	} else {
		var urlMap = {}
		for (var i=0; i<values.length; i++) {
			for (var j=0; j<values[i].length; j++) {	
				urlMap[values[i][j]] = true;
			}
		}
		var urlSet = [];
		for (url in urlMap) {
			urlSet[urlSet.length] = url;
		}
		return urlSet;
	}
}