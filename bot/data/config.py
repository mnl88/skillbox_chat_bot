import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

is_testing = False

BASE_DIRECTORY = Path(__file__).absolute().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIRECTORY / '.env')


@dataclass
class Admin:
    name: str
    id: int

@dataclass
class BotConfig:
    token: str
    chat_id: int
    admins: list[Admin]

@dataclass
class DBConfig:
    host: str
    port: int
    username: str
    password: str
    name: str
    drivername: str = 'postgresql+asyncpg'

    @property
    def to_dict(self) -> dict:
        return {
            'drivername': self.drivername,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'database': self.name,
            'query': {}
        }

    @property
    def postgresql_url(self) -> str:
        return f"{self.drivername}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


db_config = DBConfig(
    host=os.getenv("PGDB_HOST"),
    port=int(os.getenv("PGDB_PORT", default=5432)),
    username=os.getenv("PGDB_USER"),
    password=os.getenv("PGDB_PASS"),
    name=os.getenv("PGDB_NAME", default='postgres'),
)

bot_config = BotConfig(
    token=os.getenv("BOT_TOKEN"),
    chat_id=int(os.getenv("CHAT_TEST_ID") if is_testing else os.getenv("CHAT_MAIN_ID")),
    admins=[Admin(
        name='Nikita',
        id=int(os.getenv("Nikita_ID"))
    )]
)


if __name__ == '__main__':
    print(BASE_DIRECTORY)
    print(db_config.postgresql_url)
    print(bot_config)
