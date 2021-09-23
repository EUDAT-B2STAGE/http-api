from restapi.tests import API_URI, BaseTests, FlaskClient


class TestApp(BaseTests):
    def test_01(self, client: FlaskClient) -> None:

        # POST /api/ingestion/my_batch_id/approve
        r = client.post(f"{API_URI}/ingestion/my_batch_id/approve")
        assert r.status_code == 401
        r = client.get(f"{API_URI}/ingestion/my_batch_id/approve")
        assert r.status_code == 405
        r = client.put(f"{API_URI}/ingestion/my_batch_id/approve")
        assert r.status_code == 405
        r = client.delete(f"{API_URI}/ingestion/my_batch_id/approve")
        assert r.status_code == 405
        r = client.patch(f"{API_URI}/ingestion/my_batch_id/approve")
        assert r.status_code == 405
