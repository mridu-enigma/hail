import logging
import asyncio
import pytest
import aiohttp

from hailtop.config import get_deploy_config
from hailtop.auth import service_auth_headers
from hailtop.tls import in_cluster_ssl_client_session
import hailtop.utils as utils

pytestmark = pytest.mark.asyncio

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def test_billing_monitoring():
    deploy_config = get_deploy_config()
    monitoring_deploy_config_url = deploy_config.url('monitoring', '/api/v1alpha/billing')
    headers = service_auth_headers(deploy_config, 'monitoring')
    async with in_cluster_ssl_client_session(
            raise_for_status=True,
            timeout=aiohttp.ClientTimeout(total=60)) as session:

        async def wait_forever():
            data = None
            while data is None:
                resp = await utils.request_retry_transient_errors(
                    session, 'GET', f'{monitoring_deploy_config_url}', headers=headers)
                data = await resp.json()
                await asyncio.sleep(5)
            return data

        data = await asyncio.wait_for(wait_forever(), timeout=30 * 60)
        assert data['cost_by_service'] is not None, data
