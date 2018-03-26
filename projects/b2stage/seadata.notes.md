
* Swagger input JSON not possible (e.g. orders POST)
* Step 04: `/api/ingestion/<batch_id>/approve` as file_list
* Step 04: copy back files selected...
    * wait for container on rancher
- Call `API` with returns value (the same list + PIDs) - step 04/05 POST
    + add url in compose/configuration
    + use a common method with post and generic data
    + test it in approve ending
- Step 06: DELETE order/ticket?

---

`seadatacloud_api_calls_v8.docx`

http://importmanager.seadatanet.org/api_v1
function upload_datafiles_ready 

```json
{
    "request_id": 197,
    "edmo_code": 486,
    "datetime": "20180312T16:03:52",
    "version": "1",
    "api_function": "upload_datafiles_ready",
    "test_mode": "true",
    "parameters": {
        "batch_number": 197,
        "pids": [{}]
    }
}
```
