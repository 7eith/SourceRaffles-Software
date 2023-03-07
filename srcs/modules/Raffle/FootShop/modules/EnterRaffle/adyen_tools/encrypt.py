from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from os import urandom
import pytz
import json
import base64


class Encryptor:
    def __init__(self, key):
        self.public_key = self._decode_adyen_public_key(key)

    def encrypt_card_data(self, name=None, number=None, cvc=None, expiry_month=None, expiry_year=None, bin_value=None):
        plain_card_data = self._generate_card_data_json(
            holderName=name,
            number=number,
            cvc=cvc,
            expiryMonth=expiry_month,
            expiryYear=expiry_year,
            binValue=bin_value
        )

        card_data_string = json.dumps(plain_card_data, sort_keys=True)

        aes_key = AESCCM.generate_key(256)
        nonce = urandom(12)

        encrypted_card_data = self._encrypt_with_aes_key(
            aes_key, nonce, bytes(card_data_string, encoding='utf8'))
        encrypted_card_component = nonce + encrypted_card_data

        encrypted_aes_key = self._encrypt_with_public_key(aes_key)

        encrypted_aes_data = "{}_{}${}${}".format("adyenjs", "0_1_25", (base64.standard_b64encode(
            encrypted_aes_key)).decode("utf-8"), (base64.standard_b64encode(encrypted_card_component)).decode("utf-8"))

        return encrypted_aes_data

    @staticmethod
    def _generate_card_data_json(**kwargs):
        generation_time = datetime.now(tz=pytz.timezone(
            'UTC')).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        card_data = {}
        for kwarg in kwargs.items():
            if kwarg[1] is not None:
                card_data[kwarg[0]] = kwarg[1]
        card_data["generationtime"] = generation_time

        return card_data

    @staticmethod
    def _encrypt_with_aes_key(aes_key, nonce, plaintext):
        cipher = AESCCM(aes_key, tag_length=8)
        ciphertext = cipher.encrypt(nonce, plaintext, None)
        return ciphertext

    @staticmethod
    def _decode_adyen_public_key(encoded_public_key):
        backend = default_backend()
        key_components = encoded_public_key.split("|")
        public_number = rsa.RSAPublicNumbers(
            int(key_components[0], 16), int(key_components[1], 16))
        return backend.load_rsa_public_numbers(public_number)

    def _encrypt_with_public_key(self, plaintext):
        ciphertext = self.public_key.encrypt(plaintext, padding.PKCS1v15())
        return ciphertext


if __name__ == '__main__':
    e = Encryptor("10001|EA3BAFD90ABF8CB6A9055C3081C01F20B978B64CA9A8F7256D251417CDB9CBFBA552BE30C6A6928673404D62CF878BAFA5DE80BD77E53546F68317FF13D1649CA2A1CE7F1B6FE3F314B01DC7DE62EE16E94D2C4313F29F4578026FBF349B1E1BD6F0F0BEDB3B32FDC1149F40D59BDD989972EFF8DEC42EFCCCEFD586A24175443AF5915EFB39558D333553F56BF34BEB5DA36EECC6527F21FD7A608595E9696C876315FBCF85AD9CF59B019682738882C42E25CBAE3A5A808F20E9F4A0D3C60994581A78A18295CFCC6119B4C3B5E142814A92D0457B78FE17B89C8DC0B359765865988B37674863EC0FE2E240427667FA58866196635DB93A0E1D0B3AA84907")

    cc = {
        "number": "4111111145551142",
        "cvc": "737",
        "mm": "03",
        "yyyy": "2030",
    }
    cc['bin'] = cc['number'][:6]

    card_encrypted = e.encrypt_card_data(number=cc['number'])
    cvc_encrypted = e.encrypt_card_data(cvc=cc['cvc'])
    mm_encrypted = e.encrypt_card_data(expiry_month=cc['mm'])
    yyyy_encrypted = e.encrypt_card_data(expiry_year=cc['yyyy'])
    bin_encrypted = e.encrypt_card_data(bin_value=cc['bin'])

    """ print(f"{card_encrypted=}")
    print(f"{cvc_encrypted=}")
    print(f"{mm_encrypted=}")
    print(f"{yyyy_encrypted=}")
    print(f"{bin_encrypted=}") """
