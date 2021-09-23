from restapi.tests import API_URI, FlaskClient
from tests.custom import SeadataTests


class TestApp(SeadataTests):
    def test_01(self, client: FlaskClient) -> None:

        # GET /api/orders/my_order_id
        # PUT /api/orders/my_order_id
        r = client.get(f"{API_URI}/orders/my_order_id")
        assert r.status_code == 401

        r = client.put(f"{API_URI}/orders/my_order_id")
        assert r.status_code == 401

        r = client.post(f"{API_URI}/orders/my_order_id")
        assert r.status_code == 405

        r = client.patch(f"{API_URI}/orders/my_order_id")
        assert r.status_code == 405

        r = client.delete(f"{API_URI}/orders/my_order_id")
        assert r.status_code == 405

        # POST /api/orders
        # DELETE /api/orders
        r = client.post(f"{API_URI}/orders")
        assert r.status_code == 401

        r = client.delete(f"{API_URI}/orders")
        assert r.status_code == 401

        r = client.get(f"{API_URI}/orders")
        assert r.status_code == 405

        r = client.put(f"{API_URI}/orders")
        assert r.status_code == 405

        r = client.patch(f"{API_URI}/orders")
        assert r.status_code == 405

        # GET /api/orders/<order_id>/download/<ftype>/c/<code>
        r = client.get(f"{API_URI}/orders/my_order_id/download/my_ftype/c/my_code")
        assert r.status_code == 500
        assert self.get_content(r) == "Invalid file type my_ftype"

        r = client.post(f"{API_URI}/orders/my_order_id/download/my_ftype/c/my_code")
        assert r.status_code == 405

        r = client.put(f"{API_URI}/orders/my_order_id/download/my_ftype/c/my_code")
        assert r.status_code == 405

        r = client.patch(f"{API_URI}/orders/my_order_id/download/my_ftype/c/my_code")
        assert r.status_code == 405

        r = client.delete(f"{API_URI}/orders/my_order_id/download/my_ftype/c/my_code")
        assert r.status_code == 405

        headers = self.login(client)

        r = client.post(f"{API_URI}/orders", headers=headers)
        assert r.status_code == 400
        response = self.get_content(r)

        assert isinstance(response, dict)
        self.check_endpoints_input_schema(response)

        r = client.delete(f"{API_URI}/orders", headers=headers)
        assert r.status_code == 400
        response = self.get_content(r)

        assert isinstance(response, dict)
        self.check_endpoints_input_schema(response)
