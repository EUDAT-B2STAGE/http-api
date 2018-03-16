
- Step 04
    - `POST` on `/api/ingestion/<batch_id>/approve` as file_list @above
    - Call the Maris `API` with returns value of the same list + PIDs
- Step 05/06
    - Order `POST`: Call the Maris `API` at the end of the file zipped
    - Order `PUT`: Create the URL for the ticket code in GET
        + iticket ls with pdonorio/prc?
    - Order `GET`: Download the URL, check the counts, check expiration

---

Example call to notify after move to production:

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
        "pids": [{
            "temp_id": "00486_ODV_45409341_V1.txt",
            "pid": "pidpid",
            "format_n_code": "3994177",
            "data_format_l24": "ODV",
            "version": "1"
        }, {
            "temp_id": "00486_ODV_45511746_V1.txt",
            "pid": "pidpid",
            "cdi_n_code": "2449339",
            "format_n_code": "4119694",
            "data_format_l24": "ODV",
            "version": "1"
        }]
    }
}
