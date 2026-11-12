# from flask import Flask, request, jsonify
# from apify_client import ApifyClient
# from config import get_config
# import requests
# import html
# import json

# app = Flask(__name__)
# app.config.from_object(get_config())

# APIFY_TOKEN = app.config["APIFY_TOKEN"]
# APIFY_ACTOR_ID = app.config["APIFY_ACTOR_ID"]
# SF_INSTANCE_URL = app.config["SF_INSTANCE_URL"]
# SF_ACCESS_TOKEN = app.config["SF_ACCESS_TOKEN"]
# PROMPT_TEMPLATE_NAME = app.config["PROMPT_TEMPLATE_NAME"]
# SF_API_VERSION = app.config["SF_API_VERSION"]


# @app.route('/extract', methods=['POST'])
# def extract_leads():
#     data = request.json or {}
#     keyword = data.get('keyword')
#     date_posted = data.get('datePosted', 'r604800')

#     if not keyword:
#         return jsonify({"error": "Keyword is required"}), 400

#     date_mapping = {"r86400": "24h", "r604800": "week", "r2592000": "month"}
#     posted_limit = date_mapping.get(date_posted, "week")

#     client = ApifyClient(APIFY_TOKEN)
#     run_input = {
#         "searchQueries": [keyword],
#         "postedLimit": posted_limit,
#         "maxPosts": 10,
#     }

#     try:
#         run = client.actor(APIFY_ACTOR_ID).call(run_input=run_input)
#         items = list(client.dataset(run.default_dataset_id).iterate_items())
#     except Exception as e:
#         return jsonify({"error": f"Apify error: {str(e)}"}), 500

#     headers = {
#         "Authorization": f"Bearer {SF_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     created_count = 0
#     skipped_count = 0
#     duplicate_count = 0
#     failed_count = 0
#     total_scanned = len(items)

#     prompt_url = f"{SF_INSTANCE_URL}/services/data/{SF_API_VERSION}/einstein/prompt-templates/{PROMPT_TEMPLATE_NAME}/generations"
#     create_url = f"{SF_INSTANCE_URL}/services/data/{SF_API_VERSION}/sobjects/LinkedIn_Lead_Staging__c/"
#     query_url = f"{SF_INSTANCE_URL}/services/data/{SF_API_VERSION}/query/"

#     for item in items:
#         post_text = item.get('content', '')
#         if not post_text:
#             continue

#         author_name = item.get('author', {}).get('name', '') if isinstance(item.get('author'), dict) else ''
#         post_url = item.get('linkedinUrl', '')

#         # --- DUPLICATE CHECK ---
#         if post_url:
#             safe_url = post_url.replace("'", "\\'")
#             soql = f"SELECT Id FROM LinkedIn_Lead_Staging__c WHERE Post_URL__c = '{safe_url}' LIMIT 1"
#             try:
#                 check_resp = requests.get(f"{query_url}?q={requests.utils.quote(soql)}", headers=headers)
#                 if check_resp.status_code == 200 and check_resp.json().get('totalSize', 0) > 0:
#                     duplicate_count += 1
#                     continue
#             except Exception as e:
#                 print("Duplicate check error:", e)

#         prompt_payload = {
#             "isPreview": False,
#             "inputParams": {"valueMap": {"Input:PostContent": {"value": post_text[:2000]}}},
#             "additionalConfig": {"applicationName": "PromptBuilderPreview"}
#         }

#         try:
#             prompt_resp = requests.post(prompt_url, json=prompt_payload, headers=headers, timeout=30)

#             if prompt_resp.status_code not in (200, 201):
#                 print(f"PROMPT ERROR: {prompt_resp.status_code} - {prompt_resp.text}")
#                 failed_count += 1
#                 continue

#             ai_response = prompt_resp.json()
#             ai_text = ""
#             if 'generations' in ai_response and len(ai_response['generations']) > 0:
#                 ai_text = ai_response['generations'][0].get('text', '')

#             ai_text = html.unescape(ai_text)

#             try:
#                 lead_data = json.loads(ai_text)
#                 if not lead_data.get("is_lead", False):
#                     skipped_count += 1
#                     continue
#             except Exception as e:
#                 print(f"JSON PARSE ERROR: {e}")
#                 failed_count += 1
#                 continue

#             staging_record = {
#                 "Post_Text__c": post_text[:2000],
#                 "Author_Name__c": author_name,
#                 "Post_URL__c": post_url,
#                 "Status__c": "Pending",
#                 "Extracted_Lead_Data__c": ai_text
#             }

#             create_resp = requests.post(create_url, json=staging_record, headers=headers, timeout=30)
#             if create_resp.status_code in (200, 201):
#                 created_count += 1
#             else:
#                 print(f"SF CREATE ERROR: {create_resp.text}")
#                 failed_count += 1

#         except Exception as e:
#             print("EXCEPTION:", str(e))
#             failed_count += 1

#     # Determine a human-friendly message for the frontend
#     if total_scanned == 0:
#         message = f"No LinkedIn posts found for '{keyword}'. Try a broader keyword or a longer date range."
#         status = "no_posts"
#     elif created_count == 0 and duplicate_count > 0 and skipped_count == 0:
#         message = f"All {duplicate_count} matching posts were already processed earlier."
#         status = "all_duplicates"
#     elif created_count == 0 and skipped_count > 0:
#         message = f"Scanned {total_scanned} posts but AI found none matching your ideal lead profile."
#         status = "no_leads"
#     elif created_count == 0:
#         message = "Extraction completed, but no new leads were added."
#         status = "no_leads"
#     else:
#         message = f"Successfully added {created_count} new lead{'s' if created_count != 1 else ''} to your staging queue."
#         status = "success"

#     return jsonify({
#         "status": status,
#         "message": message,
#         "leads_created": created_count,
#         "skipped": skipped_count,
#         "duplicates_found": duplicate_count,
#         "failed": failed_count,
#         "total_scanned": total_scanned
#     })


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)


from flask import Flask, request, jsonify
from apify_client import ApifyClient
from config import get_config
import requests
import html
import json
import os

app = Flask(__name__)
app.config.from_object(get_config())

APIFY_TOKEN = app.config["APIFY_TOKEN"]
APIFY_ACTOR_ID = app.config["APIFY_ACTOR_ID"]
SF_INSTANCE_URL = app.config["SF_INSTANCE_URL"]
PROMPT_TEMPLATE_NAME = app.config["PROMPT_TEMPLATE_NAME"]
SF_API_VERSION = app.config["SF_API_VERSION"]


SF_CLIENT_ID = os.environ.get("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.environ.get("SF_CLIENT_SECRET")

def get_salesforce_token():
    """Salesforce se OAuth Client Credentials Flow ke through fresh token fetch karta hai."""
    token_url = f"{SF_INSTANCE_URL}/services/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": SF_CLIENT_ID,
        "client_secret": SF_CLIENT_SECRET
    }
    
    print(f"DEBUG: Fetching token from {token_url}")
    print(f"DEBUG: Client ID exists? {bool(SF_CLIENT_ID)}, Secret exists? {bool(SF_CLIENT_SECRET)}")
    
    response = requests.post(token_url, data=payload)
    
    print(f"DEBUG: Salesforce Auth Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Salesforce Token Error: {response.text}")

@app.route('/extract', methods=['POST'])
def extract_leads():
    data = request.json or {}
    keyword = data.get('keyword')
    date_posted = data.get('datePosted', 'r604800')

    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    date_mapping = {"r86400": "24h", "r604800": "week", "r2592000": "month"}
    posted_limit = date_mapping.get(date_posted, "week")

    client = ApifyClient(APIFY_TOKEN)
    run_input = {
        "searchQueries": [keyword],
        "postedLimit": posted_limit,
        "maxPosts": 10,
    }

    try:
        run = client.actor(APIFY_ACTOR_ID).call(run_input=run_input)
        items = list(client.dataset(run.default_dataset_id).iterate_items())
    except Exception as e:
        return jsonify({"error": f"Apify error: {str(e)}"}), 500

    # Salesforce Token fetch karo
    try:
        sf_token = get_salesforce_token()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    headers = {
        "Authorization": f"Bearer {sf_token}",
        "Content-Type": "application/json"
    }

    created_count = 0
    skipped_count = 0
    duplicate_count = 0
    failed_count = 0
    total_scanned = len(items)

    prompt_url = f"{SF_INSTANCE_URL}/services/data/{SF_API_VERSION}/einstein/prompt-templates/{PROMPT_TEMPLATE_NAME}/generations"
    create_url = f"{SF_INSTANCE_URL}/services/data/{SF_API_VERSION}/sobjects/LinkedIn_Lead_Staging__c/"
    query_url = f"{SF_INSTANCE_URL}/services/data/{SF_API_VERSION}/query/"

    for item in items:
        post_text = item.get('content', '')
        if not post_text:
            continue

        author_name = item.get('author', {}).get('name', '') if isinstance(item.get('author'), dict) else ''
        post_url = item.get('linkedinUrl', '')

        # --- DUPLICATE CHECK ---
        if post_url:
            safe_url = post_url.replace("'", "\\'")
            soql = f"SELECT Id FROM LinkedIn_Lead_Staging__c WHERE Post_URL__c = '{safe_url}' LIMIT 1"
            try:
                check_resp = requests.get(f"{query_url}?q={requests.utils.quote(soql)}", headers=headers)
                if check_resp.status_code == 200 and check_resp.json().get('totalSize', 0) > 0:
                    duplicate_count += 1
                    continue
            except Exception as e:
                print("Duplicate check error:", e)

        prompt_payload = {
            "isPreview": False,
            "inputParams": {"valueMap": {"Input:PostContent": {"value": post_text[:2000]}}},
            "additionalConfig": {"applicationName": "PromptBuilderPreview"}
        }

        try:
            prompt_resp = requests.post(prompt_url, json=prompt_payload, headers=headers, timeout=120)

            if prompt_resp.status_code not in (200, 201):
                print(f"PROMPT ERROR: {prompt_resp.status_code} - {prompt_resp.text}")
                failed_count += 1
                continue

            ai_response = prompt_resp.json()
            ai_text = ""
            if 'generations' in ai_response and len(ai_response['generations']) > 0:
                ai_text = ai_response['generations'][0].get('text', '')

            ai_text = html.unescape(ai_text)

            try:
                lead_data = json.loads(ai_text)
                if not lead_data.get("is_lead", False):
                    skipped_count += 1
                    continue
            except Exception as e:
                print(f"JSON PARSE ERROR: {e}")
                failed_count += 1
                continue

            staging_record = {
                "Post_Text__c": post_text[:2000],
                "Author_Name__c": author_name,
                "Post_URL__c": post_url,
                "Status__c": "Pending",
                "Extracted_Lead_Data__c": ai_text
            }

            create_resp = requests.post(create_url, json=staging_record, headers=headers, timeout=30)
            if create_resp.status_code in (200, 201):
                created_count += 1
            else:
                print(f"SF CREATE ERROR: {create_resp.text}")
                failed_count += 1

        except Exception as e:
            print("EXCEPTION:", str(e))
            failed_count += 1

    # Human-friendly message
    if total_scanned == 0:
        message = f"No LinkedIn posts found for '{keyword}'. Try a broader keyword or a longer date range."
        status = "no_posts"
    elif created_count == 0 and duplicate_count > 0 and skipped_count == 0:
        message = f"All {duplicate_count} matching posts were already processed earlier."
        status = "all_duplicates"
    elif created_count == 0 and skipped_count > 0:
        message = f"Scanned {total_scanned} posts but AI found none matching your ideal lead profile."
        status = "no_leads"
    elif created_count == 0:
        message = "Extraction completed, but no new leads were added."
        status = "no_leads"
    else:
        message = f"Successfully added {created_count} new lead{'s' if created_count != 1 else ''} to your staging queue."
        status = "success"

    return jsonify({
        "status": status,
        "message": message,
        "leads_created": created_count,
        "skipped": skipped_count,
        "duplicates_found": duplicate_count,
        "failed": failed_count,
        "total_scanned": total_scanned
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)