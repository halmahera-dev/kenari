from ibm_watsonx_orchestrate.client.local_service_instance import LocalServiceInstance
from ibm_watsonx_orchestrate.client.credentials import Credentials
from ibm_watsonx_orchestrate.client.client import Client
from unittest.mock import patch

@patch("ibm_watsonx_orchestrate.client.local_service_instance.LocalServiceInstance._get_user_auth_token",
               return_value="111")
@patch("ibm_watsonx_orchestrate.client.local_service_instance.LocalServiceInstance.get_default_tenant",
                   return_value={"id": "tenant-x"})
@patch("ibm_watsonx_orchestrate.client.local_service_instance.LocalServiceInstance._get_tenant_token",
                   return_value="1111")
def test(mock1, mock2, mock3):
    credentials = Credentials(url="http://localhost", api_key="2")
    client = Client(credentials)
    service_instance = LocalServiceInstance(client)
    assert  True

