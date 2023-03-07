import base64
import secrets
import json


def gen_risk_data():
    fingerprint = base64.b64encode((secrets.token_hex(nbytes=46) + 'a').encode()).decode('utf-8')
    client_data = {
        "version": "1.0.0",
        "deviceFingerprint": f"{fingerprint}:40",
        "persistentCookie": []
    }

    client_data_bytes = json.dumps(client_data).encode()
    client_data_b64 = base64.b64encode(client_data_bytes).decode('utf-8')

    risk_data = {"clientData": client_data_b64}

    return risk_data


if __name__ == '__main__':
    print(gen_risk_data())
