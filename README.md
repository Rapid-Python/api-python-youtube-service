# api-python-youtube

> Requirements

1. Python 3.7 or higher
2. Install the requirements.txt
3. Register your application with Google so that it can use the OAuth 2.0 protocol to authorize access to user data.
4. To use OAuth 2.0 steps with this script, you'll need to create a client_secrets.json file that contains information from the API Console. The file should be in the same directory as the script.
  
  {
      "web": {
        "client_id": "[[INSERT CLIENT ID HERE]]",
        "client_secret": "[[INSERT CLIENT SECRET HERE]]",
        "redirect_uris": [],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
      }
    }


5. Run `run.py` file using `python run.py` command.
