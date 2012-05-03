try{
    if (!window["exports"]) {
        window["exports"] = {};
    }
} catch (e) {
    window["exports"] = {};
}

exports.mock_couchdb = (function() {
    
    function MockEmit() {
        this.emitted = [];
        this.cur_doc = null;
        this.cur_doc_id = null;
    };

    MockEmit.prototype.clear = function() {
        this.emitted = [];
        this.cur_doc = null;
        this.cur_doc_id = null;
    };

    MockEmit.prototype.setDoc = function(doc, with_doc) {
        if (with_doc) {
            this.cur_doc = doc;
        }
        this.cur_doc_id = doc._id;

    };

    MockEmit.prototype.emit = function(key, value){
        var obj = {"key": key, "value": value};
        if (this.cur_doc) {
            obj["doc"] = this.cur_doc;
        }
        if (this.cur_doc_id) {
            obj["id"] = this.cur_doc_id;
        }
        this.emitted.push(obj);
    };

    var mock_emit = new MockEmit();
    var emit = function (key, value) {
        mock_emit.emit(key, value);
    }

    return {
        mock_emit: mock_emit,
        emit: emit
    };

})();