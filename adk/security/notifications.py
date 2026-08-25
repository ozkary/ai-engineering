import urllib.request
import json
import os

def send_google_chat_notification(webhook_url: str, metadata: dict) -> bool:
    """
    Sends a rich card approval request to a Google Chat Space using webhooks.
    """
    if not webhook_url:
        print("⚠️ [Notification] Webhook URL not provided. Skipping Google Chat notification.")
        return False
        
    table_name = metadata.get("table_name", "unknown")
    source_uri = metadata.get("source_uri", "unknown")
    
    # Resolve the active API server or serverless hosting URL
    agent_host_url = (
        os.getenv("AGENT_HOST_API") 
        or os.getenv("AGENT_SERVERLESS_URL") 
        or "https://<YOUR_AGENT_HOST_API_OR_SERVERLESS_URL>"
    )
    
    # Construct a Google Chat Card V2 JSON payload
    payload = {
        "cardsV2": [
            {
                "cardId": "hitl_approval_request",
                "card": {
                    "header": {
                        "title": "🛡️ Security HITL Approval Request",
                        "subtitle": f"Target: {table_name}",
                        "imageUrl": "https://fonts.gstatic.com/s/i/short-term/release/googleg/shield/default/24px.svg"
                    },
                    "sections": [
                        {
                            "header": "Resource Ingestion Details",
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": f"<b>Table Name:</b> {table_name}<br><b>Source URI:</b> <code>{source_uri}</code>"
                                    }
                                },
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Review & Approve",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": f"{agent_host_url.rstrip('/')}/approve?table={table_name}"
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                print(f"✅ [Notification] Sent Google Chat notification for table: {table_name}")
                return True
    except Exception as e:
        print(f"❌ [Notification] Failed to send Google Chat message: {e}")
        
    return False
