```
yq '.. | select(.id? and .request.body?) | select(.request.body | contains("olympus/sequence_storage/abc/schema.py")) | .id' internal/query/testdata/test_case_4.yaml
yq '.. | select(.id? == 2272) | .request.body' internal/query/testdata/test_case_4.yaml | jq -r . | jq '.contents[] | .parts[] | .text | split("\n")[1]'
yq '.. | select(.id? == 2272) | .request.body' internal/query/testdata/test_case_4.yaml | jq -r . | jq '.contents[] | .parts[] | .text'
 yq '.. | select(.id? == 2272) | .response.body' internal/query/testdata/test_case_4.yaml | jq -r . | jq '.candidates[] | .content.parts[] | .text' | jq -r > response.json
 yq '.. | select(.id? == 2272) | .request.body' internal/query/testdata/test_case_4.yaml | jq -r . | jq > request.json
```
