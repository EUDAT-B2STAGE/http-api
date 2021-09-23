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
