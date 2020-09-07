import requests
import time
import json
import pandas as pd
from src.config.constants import user_agent, followers
from src.config.credentials import username, password
from src.config.endpoints import base_url, graph_url


def get_csrf_token():
    response = requests.get(base_url)
    return response.cookies["csrftoken"]


def login_instagram():
    csrf_token = get_csrf_token()

    session = requests.Session()
    session.headers.update(
        {
            "X-CSRFToken": csrf_token,
            "user-agent": user_agent,
            "Referer": base_url
        }
    )

    str_time = str(int(time.time()))
    login_data = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{str_time}:{password}"
    }

    response = session.post(
        f"{base_url}/accounts/login/ajax/",
        data=login_data,
        allow_redirects=True
    )
    content = json.loads(response.content)

    if not content["authenticated"]:
        print("Can not logged")
        raise Exception(f"Can not logged:{content}")

    print("Logado(a) com sucesso")

    session.headers.update({"X-CSRFToken": response.cookies["csrftoken"]})

    return session


def get_user_id():
    target_user = input("Digite o perfil alvo: ")

    response = requests.get(f"{base_url}/{target_user}/?__a=1")

    if response.status_code == 200:
        response = json.loads(response.content.decode("utf-8"))
        return response["graphql"]["user"]["id"]

    raise Exception("Can not find user")


def get_list_followers(id, session):
    variables = {
        "id": id,
        "include_reel": True,
        "fetch_mutual": True,
        "first": 24
    }
    payload = {
        "query_hash": followers,
        "variables": json.dumps(variables)
    }
    response = session.get(f"{graph_url}", params=payload)
    response = json.loads(response.content.decode("utf-8"))
    nodes = response["data"]["user"]["edge_followed_by"]["edges"]
    payload = [x["node"] for x in nodes]
    df = pd.DataFrame(payload)
    df = df.loc[~df["followed_by_viewer"]]

    i = 1
    while(
        response["data"]["user"]["edge_followed_by"][
            "page_info"]["has_next_page"]
    ):
        print(f"Consultando página {i}")
        variables.update(
            {
                "after": response["data"]["user"][
                    "edge_followed_by"]["page_info"]["end_cursor"]
            }
        )
        payload = {
            "query_hash": followers,
            "variables": json.dumps(variables)
        }
        response = session.get(f"{graph_url}", params=payload)
        response = json.loads(response.content.decode("utf-8"))
        nodes = response["data"]["user"]["edge_followed_by"]["edges"]
        payload = [x["node"] for x in nodes]
        user_df = pd.DataFrame(payload)
        user_df = user_df.loc[~user_df["followed_by_viewer"]]
        df = df.append(user_df, ignore_index=True)
        i += 1
        time.sleep(5)

    user_ids = df["id"].tolist()
    print(f"{len(user_ids)} aptos para serem seguidos")
    return user_ids


def follow(session, ids):

    for id in ids:
        session.post(f"{base_url}/web/friendships/{id}/follow/")
        print(f"Pessoa com id {id} seguida")
        time.sleep(3)


def follow_target_followers():
    id = get_user_id()
    session = login_instagram()
    user_ids = get_list_followers(id, session)
    follow(session, user_ids)
