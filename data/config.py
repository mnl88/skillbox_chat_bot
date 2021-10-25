import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

admins = [
    os.getenv("Nikita_ID"),
]

ip = os.getenv("ip")

COD_CHAT_ID = -341478688
BADMINTON_CHAT_ID = -579026259
TEST_BADMINTON_CHAT_ID = -679904856


# DATABASE
driver_name = 'postgres'
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

# PSN
PSN_EMAIL = os.getenv('PSN_EMAIL')
PSN_PASSWORD = os.getenv('PSN_PASSWORD')
PSN_USERNAME = os.getenv('PSN_USERNAME')


if __name__ == '__main__':
    print(admins)
    print(ip)
    print(BOT_TOKEN)
    print(PSN_EMAIL)
