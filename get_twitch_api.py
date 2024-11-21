import requests


def get_access_token(client_id, client_secret):
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    try:
        response = requests.post(url, data=payload)
        data = response.json()
        return data.get('access_token')
    except Exception as e:
        print("Error occurred:", e)
        return None


def get_user(username, access_token, client_id, endpoint, param):
    url = "https://api.twitch.tv/helix/" + endpoint
    params = {param: username}
    headers = {"Authorization": f"Bearer {access_token}", "Client-Id": client_id}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None