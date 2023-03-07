from requests import Session
from uuid import uuid4


def get_card_brand(session: Session, encrypted_bin, supported_brands, live_key):
    data = {
        "supportedBrands": supported_brands,
        "encryptedBin": encrypted_bin,
        "requestId": str(uuid4())
    }

    r = session.post(f"https://checkoutshopper-live.adyen.com/checkoutshopper/v2/bin/binLookup?token={live_key}", json=data)
    if r.status_code != 200:
        print(r.text)
        raise Exception(f"Status code: {r.status_code}.")

    if 'brands' not in r.json():
        raise Exception(f"This card brand is not supported.")
    elif not r.json()['brands'][0]['supported']:
        raise Exception(f"This card brand is not supported.")

    return r.json()['brands'][0]


if __name__ == '__main__':
    from encrypt import Encryptor
    e = Encryptor("10001|EA3BAFD90ABF8CB6A9055C3081C01F20B978B64CA9A8F7256D251417CDB9CBFBA552BE30C6A6928673404D62CF878BAFA5DE80BD77E53546F68317FF13D1649CA2A1CE7F1B6FE3F314B01DC7DE62EE16E94D2C4313F29F4578026FBF349B1E1BD6F0F0BEDB3B32FDC1149F40D59BDD989972EFF8DEC42EFCCCEFD586A24175443AF5915EFB39558D333553F56BF34BEB5DA36EECC6527F21FD7A608595E9696C876315FBCF85AD9CF59B019682738882C42E25CBAE3A5A808F20E9F4A0D3C60994581A78A18295CFCC6119B4C3B5E142814A92D0457B78FE17B89C8DC0B359765865988B37674863EC0FE2E240427667FA58866196635DB93A0E1D0B3AA84907")

    print(get_card_brand(Session(), e.encrypt_card_data(bin_value="459654"), ["amex", "diners", "mc", "visa"], "live_7G47GNRX4BCCJEX7VCJY6MHE7UVIUGIZ"))
    # print(get_card_brand(Session(), e.encrypt_card_data(bin_value="411111"), ["amex", "diners", "mc", "visa"], "live_7G47GNRX4BCCJEX7VCJY6MHE7UVIUGIZ"))
