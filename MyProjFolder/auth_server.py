from flask import Flask, request
import msal
import requests
import os
from dotenv import load_dotenv
from flask import redirect, url_for
load_dotenv()

app = Flask(__name__)

client_id=os.getenv("AZURE_CLIENT_ID"),
client_secret=os.getenv("AZURE_CLIENT_SECRET"),
tenant_id=os.getenv("AZURE_TENANT_ID")
REDIRECT_URI = "http://localhost:8550/oauth_callback"



@app.route("/oauth_callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return "No authorization code found in request", 400

    app_msal = msal.ConfidentialClientApplication(
        client_id,
        authority="https://login.microsoftonline.com/common",
        client_credential=client_secret
    )

    scopes = ["User.Read"] 
    result = app_msal.acquire_token_by_authorization_code(
        code,
        scopes=scopes,
        redirect_uri=REDIRECT_URI
    )


    if "access_token" in result:
        access_token = result["access_token"]
        user_info = requests.get("https://graph.microsoft.com/v1.0/me", headers={
            "Authorization": f"Bearer {access_token}"
        })

        if user_info.status_code == 200:
            return f"Login successful!<br>User info:<br>{user_info.json()}"
        else:
            return f"Token OK, but Graph call failed: {user_info.status_code}"

    else:
        return f"Token exchange failed: {result.get('error_description', result)}"
    
@app.route("/login")
def login():
    app_msal = msal.ConfidentialClientApplication(
        client_id,
        authority="https://login.microsoftonline.com/common",
        client_credential=client_secret
    )

    auth_url = app_msal.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=REDIRECT_URI
    )
    return f'<a href="{auth_url}">Click here to log in with Microsoft</a>'

@app.route('/')
def index():
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(port=8550)
