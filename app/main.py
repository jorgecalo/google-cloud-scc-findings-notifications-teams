import base64
import json
import os
import requests

from google.cloud import logging
from google.cloud import secretmanager

def get_secret(secret_id="sccnotifier-teams-bot-token", version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/[INSERT-PROJECT-ID]/secrets/{secret_id}/versions/{version_id}"
    request = secretmanager.AccessSecretVersionRequest(name=name)
    # print(client.access_secret_version(request=request).payload.data.decode("utf-8"))
    return client.access_secret_version(request=request).payload.data.decode("utf-8")


def message_post(data):
    # pprint.pprint(payload)
    token = str(get_secret("sccnotifier-teams-bot-token"))
    channel_id = "security-gcp-alerts"
    payload = data if type(data) is dict else json.loads(data)

    url = 'https://api.teams.microsoft.com/v2/conversations/' + channel_id + '/messages'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json; charset=utf-8'
    }
    try:
        with open("block_templates/finding-detail.json", "rt") as block_f:
            block_template = json.load(block_f)
        # template_content
        merge_template(block_template, payload)

        params = {
            "blocks": block_template,
            "text": "Alternate content from block content",
            "unfurl_links": "false"
        }
        r = requests.post(url, data=json.dumps(params), headers=headers)
        if r.status_code != 200:
            raise ValueError(f"Request to Teams returned error \
                {r.status_code}. Response is: {r.text}")
        # print(r.text)

    except Exception as e:
        print(f"Error occurred attempting to post message. Error is: {e}")

def merge_template(list_data, payload):
    finding = payload.get("finding")
    resource = payload.get("resource")
    props = finding.get("sourceProperties")

    org_id = finding.get("name").split("/")[1]
    finding_id = finding.get("name").split("/")[-1]
    source_id = finding.get("name").split("/")[3]
    severity = finding.get("severity")
    sev_emo = ":warning:" if "HIGH" in severity else ""

    url = "https://console.cloud.google.com/security/command-center/findings"
    url += f"?organizations/{org_id}/sources/{source_id}/"
    url += f"findings/{finding_id}=,true&orgonly=true"
    url += f"&organizationId={org_id}&supportedpurview=organizationId"
    url += "&view_type=vt_finding_type&vt_finding_type=All"
    url += f"&resourceId=organizations/{org_id}/sources/{source_id}/"
    url += f"findings/{finding_id}"
    # pprint.pprint(url)

    list_data[0]["text"]["text"] = list_data[0]["text"]["text"] \
        .replace("<SUBJECT>", finding.get("category")) \
        .replace("<WEB_LINK>", url)

    list_data[1]["text"]["text"] = list_data[1]["text"]["text"] \
        .replace("<PROJECT_ID>", str(resource.get("projectDisplayName"))) \
        .replace("<SEVERITY>", severity) \
        .replace("<SEV_EMO>", sev_emo) \
        .replace("<STATE>", finding.get("state")) \
        .replace("<TIMESTAMP>", finding.get("createTime"))

    list_data[1]["accessory"]["url"] = list_data[1]["accessory"]["url"] \
        .replace
