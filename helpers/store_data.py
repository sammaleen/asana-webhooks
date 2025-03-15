import mysql.connector
import logging

logger = logging.getLogger(__name__)

#  get env vars
from helpers.config import (
    db_user,
    db_host,
    db_pass,
    database
    )


# helper to establish DB connection
def get_db_conn():
    
    return mysql.connector.connect(
        user = db_user,
        password = db_pass,
        host = db_host,
        database = database,
        charset='utf8mb4'
        )
    
    
# store newely created webhook_gid
def store_webhook(webhook_gid, resource_gid, status="pending"):
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO webhooks (webhook_gid, resource_gid, x_hook_secret, status)
            VALUES(%s, %s, %s, %s)
            """,
            (webhook_gid, resource_gid, "", status)
        )
        conn.commit()
        logger.info(f"Asana webhook {webhook_gid} with status {status} saved to DB")
        return True
    
    except mysql.connector.Error as err:
        logger.error(f"[WARNING] -> {err} DB error while storing webhook {webhook_gid}")
        return False
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
            
            
# get pending webhook data
def get_pending_wb():
    
    conn = None
    cursor = None
    
    try: 
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT *
            FROM webhooks
            WHERE status = 'pending'
            LIMIT 1
            """
        )
        
        result = cursor.fetchone()
        if result:
            return result
        else:
            return None
        
    except mysql.connector.Error as err:
        logger.error(f"[WARNING] -> {err} DB error while extracting pending webhook")
        return None
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        
    
# update handshake secret from null to actual value
def update_secret(webhook_gid, x_hook_secret, new_status="active"):
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE webhooks
            SET x_hook_secret = %s, status = %s
            WHERE webhook_gid = %s
            """,
            (x_hook_secret, new_status, webhook_gid)
        )
        conn.commit()
        logger.info(f"Asana webhook {webhook_gid} updated with new secret, status changed to active")
        return True
    
    except mysql.connector.Error as err:
        logger.error(f"[WARNING] -> {err} DB error while updating secret for webhook {webhook_gid}")
        return False
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
     
            
# get webhook secret from DB
def get_wb_secret(webhook_gid):
    
    conn = None
    cursor = None
    
    try: 
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT x_hook_secret
            FROM webhooks
            WHERE webhook_gid = %s
            LIMIT 1
            """,
            (webhook_gid,)
        )
        
        result = cursor.fetchone()
        if result:
            return result.get("x_hook_secret")
        else:
            return None
        
    except mysql.connector.Error as err:
        logger.error(f"[WARNING] -> {err} DB error while extracting webhook {webhook_gid}")
        return None
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        