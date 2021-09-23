from restapi.tests import API_URI, FlaskClient
from tests.custom import SeadataTests


class TestApp(SeadataTests):
    def test_01(self, client: FlaskClient) -> None:

        # GET /api/ingestion/my_batch_id
        # POST /api/ingestion/my_batch_id
        r = client.get(f"{API_URI}/ingestion/my_batch_id")
        assert r.status_code == 401

        r = client.post(f"{API_URI}/ingestion/my_batch_id")
        assert r.status_code == 401

        r = client.put(f"{API_URI}/ingestion/my_batch_id")
        assert r.status_code == 405
        r = client.delete(f"{API_URI}/ingestion/my_batch_id")
        assert r.status_code == 405
        r = client.patch(f"{API_URI}/ingestion/my_batch_id")
        assert r.status_code == 405

        # DELETE /api/ingestion
        r = client.delete(f"{API_URI}/ingestion")
        assert r.status_code == 401

        r = client.get(f"{API_URI}/ingestion")
        assert r.status_code == 405

        r = client.post(f"{API_URI}/ingestion")
        assert r.status_code == 405

        r = client.put(f"{API_URI}/ingestion")
        assert r.status_code == 405

        r = client.patch(f"{API_URI}/ingestion")
        assert r.status_code == 405

        headers = self.login(client)

        # POST - missing parameters
        r = client.post(f"{API_URI}/ingestion/my_batch_id", headers=headers)
        assert r.status_code == 400
        response = self.get_content(r)

        assert isinstance(response, dict)
        self.check_endpoints_input_schema(response)

        r = client.delete(f"{API_URI}/ingestion", headers=headers)
        assert r.status_code == 400
        response = self.get_content(r)

        assert isinstance(response, dict)
        self.check_endpoints_input_schema(response)

        # GET - invalid batch
        r = client.get(f"{API_URI}/ingestion/my_batch_id", headers=headers)
        assert r.status_code == 404

        error = "Batch 'my_batch_id' not enabled or you have no permissions"
        assert self.get_seadata_response(r) == [error]

        # POST - with no files to be downloaded
        data = self.get_input_data()
        r = client.post(f"{API_URI}/ingestion/my_batch_id", headers=headers, data=data)
        # The request is accepted because no input validation is implemented.
        # The errors will be raised by celery
        assert r.status_code == 202

        # Even if the previous batch request was empty, the batch has been created
        # But the batch can be executed again
        r = client.post(f"{API_URI}/ingestion/my_batch_id", headers=headers, data=data)
        # The request is accepted because no input validation is implemented.
        # The errors will be raised by celery
        assert r.status_code == 202
