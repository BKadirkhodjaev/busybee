from typing import List
from folio_mods import Module, Okapi
import requests
import uuid


def deploy_module_to_http_loc(okapi_url, module: Module):
    if module.descriptor_json is None and not type(module) is Okapi:
        raise Exception(f'module is probably not registered: {module}')

    if type(module) is Okapi:
        print('Okapi does not need to be deployed')
        return

    module_id = module.descriptor_json['id']
    deploy_url = f"http://localhost:{module.http_port}"
    deploy_payload = {
        "instId": str(uuid.uuid4()),
        "srvcId":  module_id,
        "url": deploy_url}

    print(f'setting module({module_id}) deployment to url: {deploy_url}')
    resp = requests.post(
        f"{okapi_url}/_/discovery/modules",
        json=deploy_payload,
        headers={"X-Okapi-Tenant": "supertenant"})

    if resp.status_code != 201:
        raise Exception(f"Could not set deployment location: {resp.text}")


def enable_modules_for_tenant(okapi_url, tenant_id, modules: List[Module]):
    print('###############')
    print('ENABLING MODULES TO TENANT')
    print('###############')
    # deploy minimal modules to the tenant
    for module in modules:
        if type(module) is Okapi:
            continue

        print(f"enabling module({module.descriptor_json['id']}) for tenant({tenant_id})")
        resp = requests.post(f"{okapi_url}/_/proxy/tenants/{tenant_id}/install",
                             json=[{"id": module.descriptor_json['id'], "action": "enable"}],
                             params={"deploy": "false",
                                     "tenantParameters": "loadReference%3dtrue%2cloadSample%3dtrue"},
                             headers={"X-Okapi-Tenant": "supertenant"})
        if resp.status_code != 201 and resp.status_code != 200 and 'has no launchDescriptor' not in resp.text:
            raise Exception(
                f"could not create enable module({module.descriptor_json['id']}) for tenant({tenant_id}): {resp.text}")