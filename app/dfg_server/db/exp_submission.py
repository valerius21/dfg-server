import http.client
import json


def exp_is_uuid_private(uuid: str) -> bool:
    """
    Temporary solution due to PyGQL bugs
    :param uuid:
    :return:
    """
    conn = http.client.HTTPSConnection("c102-226.cloud.gwdg.de")

    payload = '{"query":"query GetPkFromSet($bruh: uuid!) {\\n  public(where: {id: {_eq: $bruh}}) {\\n    id\\n  ' \
              '}\\n  private(where: {id: {_eq: $bruh}}) {\\n    id\\n  }\\n}\\n","variables":{' \
              '"bruh":"xx"}} '.replace('xx', uuid)

    headers = {
        'content-type': 'application/json'
    }

    conn.request("POST", "/v1/graphql", payload, headers)

    res = conn.getresponse()

    data = res.read()
    data = json.loads(data.decode("utf-8"))['data']
    is_private = bool(data['private'])

    return is_private


if __name__ == '__main__':
    exp_is_uuid_private('762779f4-0a32-473f-a11a-c671b1c9e89a')
