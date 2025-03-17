import requests
import logging

from helpers.store_data import (
    store_webhook
)

from helpers.config import (
    asana_token,
    wb_server_url
    )

target_url = f"{wb_server_url}/receive_webhook"

logger = logging.getLogger(__name__)


# delete asana webhook
def delete_webhook(asana_token, webhook_gid):
    
    headers = {'Authorization': f'Bearer {asana_token}'}
    url = f"https://app.asana.com/api/1.0/webhooks/{webhook_gid}"
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        logging.info(f"Successfully deleted webhook: {webhook_gid}")
        return True
    
    except requests.exceptions.RequestException as err:
        logging.info(f"[WARNING] -> network error: {err} deleting asana webhook: {webhook_gid}")
        return False
        

# create asana webhook
def create_webhook(asana_token, target_url, resource_gid, action_filter, resource_type):
    
    headers = {'Authorization': f'Bearer {asana_token}'}
    url = "https://app.asana.com/api/1.0/webhooks"
    
    data = {
        "data": {
            "resource": resource_gid,
            "target": target_url,
            "filters": [{
                "action": action_filter,
                "resource_type": resource_type
                }], 
        }
    }
    
    try: 
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        response_json = response.json()
        webhook_gid = response_json.get('data', {}).get('gid')
        
        if webhook_gid:
            store_webhook(
                webhook_gid=webhook_gid,
                resource_gid=resource_gid,
                status="pending"
            )        
        
        logging.info(f"Created new asana webhook: {webhook_gid}\nWebhook creation response: {response_json}")
        return webhook_gid
 
    except requests.exceptions.RequestException as err:
        logging.error(f"[WARNING] -> network error: {err} creating new asana webhook")
        return None
    
    
# creating specific webhooks
# event - when new task is added/created in project 'In'

create_webhook(
    asana_token,
    target_url,
    resource_gid="1209545941169722", # project_gid of the project 'In'
    action_filter="added",
    resource_type="task"
)
    