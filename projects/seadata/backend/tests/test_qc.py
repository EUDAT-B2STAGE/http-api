from restapi.tests import API_URI, BaseTests, FlaskClient


class TestApp(BaseTests):
    def test_01(self, client: FlaskClient) -> None:

        # GET /ingestion/<batch_id>/qc/<qc_name>
        # PUT /ingestion/<batch_id>/qc/<qc_name>
        # DELETE /ingestion/<batch_id>/qc/<qc_name>
        r = client.get(f"{API_URI}/ingestion/my_batch_id/qc/my_qc_name")
        assert r.status_code == 401

        r = client.put(f"{API_URI}/ingestion/my_batch_id/qc/my_qc_name")
        assert r.status_code == 401

        r = client.delete(f"{API_URI}/ingestion/my_batch_id/qc/my_qc_name")
        assert r.status_code == 401

        r = client.post(f"{API_URI}/ingestion/my_batch_id/qc/my_qc_name")
        assert r.status_code == 405

        r = client.patch(f"{API_URI}/ingestion/my_batch_id/qc/my_qc_name")
        assert r.status_code == 401
