curl -v -H "Content-Type: application/json" -X POST  -d '{"documents" : [{"name":"test1"},{"name":"test2"},{"name":"test3"}]}' http://localhost/publish > publish.htm && firefox publish.htm
