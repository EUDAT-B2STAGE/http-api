from restapi.tests import API_URI, FlaskClient
from tests.custom import SeadataTests


class TestApp(SeadataTests):
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

        headers = self.login(client)

        r = client.post(f"{API_URI}/ingestion/my_batch_id/approve", headers=headers)
        assert r.status_code == 400
        response = self.get_content(r)

        assert "api_function" in response
        assert "Missing data for required field." in response["api_function"]

        assert "datetime" in response
        assert "Missing data for required field." in response["datetime"]

        assert "edmo_code" in response
        assert "Missing data for required field." in response["edmo_code"]

        assert "parameters" in response
        assert "Missing data for required field." in response["parameters"]

        assert "request_id" in response
        assert "Missing data for required field." in response["request_id"]

        assert "test_mode" in response
        assert "Missing data for required field." in response["test_mode"]

        assert "version" in response
        assert "Missing data for required field." in response["version"]
