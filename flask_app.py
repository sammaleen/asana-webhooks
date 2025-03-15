from flask import Flask, jsonify, request, make_response
import json
import logging
import hmac
import hashlib

# get helper functions
from helpers.store_data import (
    get_pending_wb,
    update_secret,
    get_wb_secret
    )

# get env vars
from helpers.config import (
    asana_token,
    wb_server_url,
    db_user,
    db_host,
    db_pass,
    database
    )

# set up logger
logging.basicConfig(
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# set up flask
app = Flask(__name__)


# ---------------------

# verification for x-hook-signature from asana
def verify_signature(request_body: bytes, signature: str, secret: str) -> bool:
    
    if isinstance(request_body, str):
        request_body = request_body.encode("utf-8")
        
    hash_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=request_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(hash_signature, signature)


# callback route to handle intial webhook creation and futher event processing
@app.route("/receive_webhook", methods=["POST"])

def receive_webhook():
    
    # INITIAL HANDSHAKE
    # get secret from asana handshake request
    x_hook_secret = request.headers.get("X-Hook-Secret")
    
    if x_hook_secret:
        
        pending = get_pending_wb() # get pending webhook from DB (only can be one at a time)
        
        if pending:
            pending_gid = pending["webhook_gid"]
            update_secret(
                webhook_gid=pending_gid,
                x_hook_secret=x_hook_secret,
                new_status="active"
            )
        
        # return response to asana to confirm hansshake
        response = make_response("", 200)
        response.headers["X-Hook-Secret"] = x_hook_secret
        logger.info(f"Successful webhook handshake with Asana for webhook {pending_gid}")
        return response
    
    # WB EVENTS PROCESSING
    # processing subsequent webhook events delivery
    signature = request.headers.get("X-Hook-Signature")
    
    if not signature:
        logger.error("[WARNING] -> asana request missing x-hook-signature")
        return jsonify({"error": "Missing signature"}), 400
    
    # get secret for incoming event
    current_webhook_gid = "example_webhook_gid"
    secret_from_db = get_wb_secret(current_webhook_gid)
    
    if not secret_from_db:
        logger.error(f"[WARNING] -> no secret found in DB for webhook: {current_webhook_gid}")
        return jsonify({"error": "No secret in DB for the webhook"}), 400
    
    # signature verification
    request_body = request.get_data()
    
    if not verify_signature(request_body, signature, secret_from_db):
        logger.error("[WARNING] -> webhook signatures don't match")
        return jsonify({"error": "Invalid signature"}), 400
    
    # if verification passed, parse json content from request body
    try:
        payload = json.loads(request_body.decode("utf-8"))
    except ValueError:
        logger.error("[WARNING] -> failed to parse json content")
        return jsonify({"error": "Invalid JSON"}), 400
    
    # get and process webhook events
    events = payload.get("events", [])
    
    if not events:
        logger.info("Empty events webhook call")
        return jsonify({"status": "ok", "message": "No events in payload"}), 200
    
    for event in events:
        logger.info(f"Recieved event: {event}")
    
    return jsonify({"status": "ok"}), 200
    