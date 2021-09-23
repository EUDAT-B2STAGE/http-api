from restapi.tests import API_URI, BaseTests, FlaskClient


class TestApp(BaseTests):
    def test_01(self, client: FlaskClient) -> None:

        # GET /api/pidcache
        r = client.get(f"{API_URI}/pidcache")
        assert r.status_code == 401

        r = client.post(f"{API_URI}/pidcache")
        assert r.status_code == 405

        r = client.put(f"{API_URI}/pidcache")
        assert r.status_code == 405

        r = client.patch(f"{API_URI}/pidcache")
        assert r.status_code == 405

        r = client.delete(f"{API_URI}/pidcache")
        assert r.status_code == 405

        # POST /api/pidcache/my_batch
        r = client.post(f"{API_URI}/pidcache/my_batch")
        assert r.status_code == 401

        r = client.get(f"{API_URI}/pidcache/my_batch")
        assert r.status_code == 405

        r = client.put(f"{API_URI}/pidcache/my_batch")
        assert r.status_code == 405

        r = client.patch(f"{API_URI}/pidcache/my_batch")
        assert r.status_code == 405

        r = client.delete(f"{API_URI}/pidcache/my_batch")
        assert r.status_code == 405
