from datetime import datetime, date, timedelta
import random

from faker import Faker

class Helper:
    def get_current_time(self):
        return datetime.now().isoformat()

    def load_cookies(self, session):
        cookies = []
        for name, value in session.cookies.get_dict().items():
            cookies.append(name + "=" + value)
        return "; ".join(cookies)

    def gen_birth_date(self, format):
        random_number_of_days = random.randrange((date(2003, 5, 1) - date(1990, 1, 1)).days)
        random_date = date(1990, 1, 1) + timedelta(days=random_number_of_days)
        return random_date.strftime(format)

    def gen_password(self):
        chars = "abcdefghijklmnopqrstwuvwxyz1234567890_.!?"
        password = ""
        for _ in range(random.randint(10, 16)):
            if random.choice([True, False, False]):
                password += (random.choice(chars)).upper()
            else:
                password += random.choice(chars)
        return password

    def gen_first_name(self):
        return Faker().first_name()

    def gen_last_name(self):
        return Faker().last_name()

    def log(self, text, state="default"):
        if state == "default":
            print(f'[{datetime.now().strftime("%X")}] - {text}')
        elif state == "error":
            print(f'[{datetime.now().strftime("%X")}] - \033[91m{text}\033[0m')
        elif state == "success":
            print(f'[{datetime.now().strftime("%X")}] - \033[92m{text}\033[0m')
