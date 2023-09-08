import asyncio
import logging
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, Boolean, TIMESTAMP
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from utils.b4u_parser.b4u_script import stat_parser

DeclarativeBase = declarative_base()

load_dotenv()

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

test_accounts = [
    {"id": 530331399, "is_bot": False, "first_name": "Кристина"},
    {"id": 202181776, "is_bot": False, "first_name": "Nikita", "username": "MaN1Le", "language_code": "ru"},
    {"id": 35259859, "is_bot": False, "first_name": "Svetlana", "username": "svetlana_mnk"},
    {"id": 951683409, "is_bot": False, "first_name": "Konstantin", "last_name": "Zelenevskii"},
    {"id": 77873373, "is_bot": False, "first_name": "Alexander", "last_name": "Rakita", "username": "Alexander_Rakita"},
    {"id": 394097575, "is_bot": False, "first_name": "КсениЯ"}
]


class TG_Account(DeclarativeBase):
    __tablename__ = 'tg_accounts'

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    id = Column('id', Integer, primary_key=True)
    username: Column = Column(String(100))
    is_bot = Column('is_bot', Boolean, default=False)
    first_name = Column('first_name', String(100))
    last_name = Column('last_name', String(100))
    language_code = Column('language_code', String(50))
    created_at = Column('created_at', TIMESTAMP, default=datetime.now())
    modified_at = Column('modified_at', TIMESTAMP, default=datetime.now())

    badminton_player = relationship("Badminton_player", back_populates="tg_account", uselist=False)

    def __repr__(self):
        return "<TG_Account: (id: '%s', username: '%s', first_name: '%s')>" % (self.id, self.username, self.first_name)

    async def is_exists_by_id(self, db_engine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(TG_Account).where(TG_Account.id == self.id))
            user = result.scalars().one_or_none()
            if user:
                logger.info(f'Запись {self} найдена в БД')
                return True
            else:
                logger.info(f'Запись {self} не найдена в БД')
                return False

    async def update(self, db_engine):
        """Обновляем запись об аккаунте в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                stmt = update(TG_Account).where(TG_Account.id == self.id).values(
                    username=self.username,
                    is_bot=self.is_bot,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    language_code=self.language_code,
                    modified_at=datetime.now(),
                ).execution_options(synchronize_session="fetch")
                await session.execute(stmt)
                await session.commit()
                logger.info(f'Обновление записи {self} прошло успешно!')
        return self

    async def read_by_id(self, db_engine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(TG_Account).where(TG_Account.id == self.id))
            row = result.scalars().one_or_none()
            logger.info(f'Получена запись {row}')
            return row

    async def create(self, db_engine):
        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                try:
                    session.add(self)
                    await session.commit()
                    logger.info(f'Запись {self} успешно внесена в БД!')
                except Exception as err:
                    # await session.rollback()
                    logger.error(f'Ошибка! Внести запись в БД не получилось. {err}')

    async def delete(self, db_engine):
        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                try:
                    await session.delete(self)
                    await session.commit()
                    logger.info(f'Запись {self} успешно удалена!')
                except Exception as err:
                    logger.error(f'Ошибка! удалить запись {self} в БД не получилось. {err}')





class B4U_Account(DeclarativeBase):
    __tablename__ = 'b4u_accounts'

    id = Column('id', Integer, primary_key=True)
    username: Column = Column('username', String(100))
    single_rating = Column('single_rating', Integer)
    single_rating_date_of_calc = Column('single_rating_date_of_calc', String(100))
    double_rating = Column('double_rating', Integer)
    double_rating_date_of_calc = Column('double_rating_date_of_calc', String(100))
    created_at = Column('created_at', TIMESTAMP, default=datetime.now())
    modified_at = Column('modified_at', TIMESTAMP, default=datetime.now())

    badminton_player = relationship("Badminton_player", back_populates="b4u_account", uselist=False)

    def __repr__(self):
        return "<B4U_Account: (id: '%s', username: '%s')>" % (self.id, self.username)

    async def fetch(self, engine: AsyncEngine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(B4U_Account).where(B4U_Account.id == self.id))
            return result.scalars().one_or_none()

    async def is_exists_by_id(self, db_engine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(B4U_Account).where(B4U_Account.id == self.id))
            user = result.scalars().one_or_none()
            if user:
                logger.info(f'Запись {self} найдена в БД')
                return True
            else:
                logger.info(f'Запись {self} не найдена в БД')
                return False

    async def update_all(self, db_engine):
        """Обновляем запись об аккаунте в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                stmt = update(B4U_Account).where(B4U_Account.id == self.id).values(
                    username=self.username,
                    single_rating=self.single_rating,
                    single_rating_date_of_calc=self.single_rating_date_of_calc,
                    double_rating=self.double_rating,
                    double_rating_date_of_calc=self.double_rating_date_of_calc,
                    modified_at=datetime.now(),
                ).execution_options(synchronize_session="fetch")
                await session.execute(stmt)
                await session.commit()
                logger.info(f'Обновление записи {self} прошло успешно!')
        return self

    async def update(self, db_engine, **kwargs):
        """Обновляем запись об аккаунте в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                stmt = update(B4U_Account).where(B4U_Account.id == self.id).\
                    values(kwargs, modified_at=datetime.now()).execution_options(synchronize_session="fetch")
                await session.execute(stmt)
                await session.commit()
                logger.info(f'Обновление записи {self} прошло успешно! {kwargs}')
        return self

    async def read_by_id(self, db_engine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""
        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(B4U_Account).where(B4U_Account.id == self.id))
            row = result.scalars().one_or_none()
            logger.info(f'Получена запись {row}')
            return row

    async def create(self, db_engine):
        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                try:
                    session.add(self)
                    await session.commit()
                    logger.info(f'Запись {self} успешно внесена в БД!')
                except Exception as err:
                    # await session.rollback()
                    logger.error(f'Ошибка! Внести запись в БД не получилось. {err}')

    async def delete(self, db_engine):
        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                try:
                    await session.delete(self)
                    await session.commit()
                    logger.info(f'Запись {self} успешно удалена!')
                except Exception as err:
                    logger.error(f'Ошибка! удалить запись {self} в БД не получилось. {err}')

    async def get_from_site_by_id(self):
        stat = await stat_parser(player_id=self.id)
        if stat:
            b4u_account = B4U_Account(**stat)
            return b4u_account

    # получаем экземпляр B4U_Account. Если в БД нет, указанного id, то создаём.
    # получаем дату последнего обновления, если обновление было менее чем n минут назад, парсим статистику, сохраняем в БД
    # если статистика не парсится, то удаляем профиль с указанным id
    async def smart_get(self, db_engine, minutes_for_update=2.00):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""
        row = await self.read_by_id(db_engine)
        b4u_form_site = await self.get_from_site_by_id()
        if not row:
            if b4u_form_site:
                await b4u_form_site.create(db_engine)
            else:
                logger.error(f'По указанному ID нет записи в базе данных, спарсить такой аккаунт тоже не получается')
        else:
            if not row.modified_at:
                delta_minutes = minutes_for_update
            else:
                delta_minutes = (datetime.now()-row.modified_at).total_seconds()/60
            if b4u_form_site:
                if delta_minutes >= minutes_for_update:
                    await b4u_form_site.update_all(db_engine)

        return await self.read_by_id(db_engine)


class Badminton_player(DeclarativeBase):
    __tablename__ = "badminton_players"

    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    # todo: добавить для vk_id и b4u_id unique=True и прописать везде валидацию
    tg_id = Column(Integer, ForeignKey('tg_accounts.id'), unique=False, nullable=False)
    vk_id = Column(Integer, unique=False)
    b4u_id = Column(Integer, ForeignKey('b4u_accounts.id'), unique=False)

    # id на сайте федерации бадминтона РФ http://www.info.badm.spb.ru/profile/1281
    fed_badm_id = Column(Integer, unique=False)

    created_at = Column('created_at', TIMESTAMP, default=datetime.now())
    modified_at = Column('modified_at', TIMESTAMP, default=datetime.now())

    tg_account = relationship("TG_Account", back_populates="badminton_player")
    b4u_account = relationship("B4U_Account", back_populates="badminton_player")

    def __repr__(self):
        return "<Badminton_player: (id: '%s', nickname: '%s',tg_id: '%s', b4u_id: '%s')>" % (
            self.id, self.nickname, self.tg_id, self.b4u_id)

    # Проверяем, есть ли запись с таким tg_id в БД
    async def is_already_exists(self, engine: AsyncEngine):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(Badminton_player).where(
                    Badminton_player.tg_id == self.tg_id))
                user = result.scalars().first()
                if user:  # если такой уже есть в нашей базе данных...
                    return True
                else:
                    return False

    # Возвращает экземпляр класса Badminton_player с указанным tg_id из БД
    async def fetch_by_tg_id(self, engine: AsyncEngine):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(Badminton_player).where(
                    Badminton_player.tg_id == self.tg_id))
                return result.scalars().one()

    async def is_exists_by_id(self, db_engine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(Badminton_player).where(Badminton_player.id == self.id))
            user = result.scalars().one_or_none()
            if user:
                logger.info(f'Запись {self} найдена в БД')
                return True
            else:
                logger.info(f'Запись {self} не найдена в БД')
                return False

    async def is_exists_by_tg_id(self, db_engine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(Badminton_player).where(Badminton_player.tg_id == self.tg_id))
            user = result.scalars().one_or_none()
            if user:
                logger.info(f'Запись {self} найдена в БД')
                return True
            else:
                logger.info(f'Запись {self} не найдена в БД')
                return False

    async def update(self, db_engine, **kwargs):
        """Обновляем запись об аккаунте в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                stmt = update(Badminton_player).where(Badminton_player.id == self.id).values(kwargs). \
                    execution_options(synchronize_session="fetch")
                await session.execute(stmt)
                await session.commit()
                logger.info(f'Обновление записи {self} прошло успешно! {kwargs}')
        return self

    async def update_all(self, db_engine):
        """Обновляем запись об аккаунте в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                stmt = update(Badminton_player).where(Badminton_player.id == self.id).values(
                    username=self.username,
                    is_bot=self.is_bot,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    language_code=self.language_code,
                    modified_at=datetime.now(),
                ).execution_options(synchronize_session="fetch")
                await session.execute(stmt)
                await session.commit()
                logger.info(f'Обновление записи {self} прошло успешно!')
        return self

    async def read_by_id(self, db_engine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(Badminton_player).where(Badminton_player.id == self.id))
            row = result.scalars().one_or_none()
            logger.info(f'Получена запись {row}')
            return row

    async def read_by_tg_id(self, db_engine):
        """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            result = await session.execute(select(Badminton_player).where(Badminton_player.tg_id == self.tg_id))
            row = result.scalars().one_or_none()
            logger.info(f'Получена запись {row}')
            return row

    async def create(self, db_engine):
        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                try:
                    session.add(self)
                    await session.commit()
                    logger.info(f'Запись {self} успешно внесена в БД!')
                except Exception as err:
                    # await session.rollback()
                    logger.error(f'Ошибка! Внести запись в БД не получилось. {err}')

    async def delete(self, db_engine):
        async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                try:
                    await session.delete(self)
                    await session.commit()
                    logger.info(f'Запись {self} успешно удалена!')
                except Exception as err:
                    logger.error(f'Ошибка! удалить запись {self} в БД не получилось. {err}')


async def start_db() -> AsyncEngine:
    engine = create_async_engine(url=os.getenv("DB_URL"), echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.create_all)
    return engine


async def insert_people(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    Badminton_player(nickname='Nikita', tg_id=123, vk_id=2680992, b4u_id=17284),
                    Badminton_player(nickname='Katyja', tg_id=123, vk_id=2680992, b4u_id=17284),
                    Badminton_player(nickname='Jenja', tg_id=123, vk_id=2680992, b4u_id=17284),
                ]
            )
        await session.commit()


async def fetch_all_b4u_accounts(db_engine) -> [B4U_Account]:
    """Проверяем, есть ли такой ТГ - Аккаунт в БД"""

    async_session = sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        # session: AsyncSession
        # session.execute()
        result2 = await session.execute(select(B4U_Account))
        rows = result2.scalars().fetchall()
        # result = await session.execute(select(B4U_Account).where(B4U_Account.id == self.id))
        # row = result.scalars().one_or_none()
        # logger.info(f'Получена запись {row2}')
        return rows


async def add_member_using_tg_id(engine: AsyncEngine, tg_account: TG_Account):
    """Добавляем участника"""

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            session.add(tg_account)
            # session.add(TG_Account(nickname='Nikita', tg_id=123))
            # session.add_all(
            #     [
            #         TG_Account(nickname='Nikita', tg_id=123, vk_id=2680992, b4u_id=17284),
            #         Badminton_player(nickname='Katyja', tg_id=123, vk_id=2680992, b4u_id=17284),
            #         Badminton_player(nickname='Jenja', tg_id=123, vk_id=2680992, b4u_id=17284),
            #     ]
            # )
            await session.commit()


async def add_td_acc_if_not_exist(engine: AsyncEngine, tg_account: TG_Account):
    if await is_tg_acc_exists_in_db(engine, tg_account):
        # print('Такой аккаун уже существует')
        return True
    else:
        await add_member_using_tg_id(engine, tg_account)
        # print(f'{tg_account} добавлен в БД')
        return False


async def parse_b4u_by_id(b4u_id: int) -> B4U_Account:
    info = await stat_parser(b4u_id)
    b4u_player = B4U_Account(
        id=b4u_id,
        username=info['name']
    )
    if "[s] Одиночки" in info:
        b4u_player.single_rating = info['[s] Одиночки']['rating']
        b4u_player.single_rating_date_of_calc = info['[s] Одиночки']['date_of_calc']
    if "[d] Пары" in info:
        b4u_player.double_rating = info['[d] Пары']['rating']
        b4u_player.double_rating_date_of_calc = info['[d] Пары']['date_of_calc']

    return b4u_player


async def add_or_update_b4u_to_db(engine: AsyncEngine, b4u_account: B4U_Account) -> B4U_Account:
    """Добавляем или обновляем запись об аккаунте B4U в БД"""

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(B4U_Account).where(B4U_Account.id == b4u_account.id))
            user = result.scalars().first()
            if user:  # если такой уже есть в нашей базе данных...
                logger.info(f'Запись {b4u_account} уже есть в БД')
                stmt = update(B4U_Account).where(B4U_Account.id == b4u_account.id).values(
                    username=b4u_account.username,
                    single_rating=b4u_account.single_rating,
                    single_rating_date_of_calc=b4u_account.single_rating_date_of_calc,
                    double_rating=b4u_account.double_rating,
                    double_rating_date_of_calc=b4u_account.double_rating_date_of_calc,
                    modified_at=datetime.now(),
                ).execution_options(synchronize_session="fetch")
                await session.execute(stmt)

            else:
                logger.info(f'Запись {b4u_account} отсутствует в БД')
                session.add(b4u_account)
            await session.commit()
    return b4u_account


async def add_or_update_player_to_db(engine: AsyncEngine, badminton_player: Badminton_player) -> Badminton_player:
    """Добавляем или обновляем запись об аккаунте B4U в БД"""

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Badminton_player).where(
                Badminton_player.tg_id == badminton_player.tg_id))
            user = result.scalars().first()
            if user:  # если такой уже есть в нашей базе данных...
                logger.info(f'Запись {badminton_player} уже есть в БД')
                stmt = update(Badminton_player).where(Badminton_player.id == badminton_player.id).values(
                    nickname=badminton_player.nickname,
                    tg_id=badminton_player.tg_id,
                    b4u_id=badminton_player.b4u_id,
                    vk_id=badminton_player.vk_id,
                    modified_at=datetime.now(),
                ).execution_options(synchronize_session="fetch")
                await session.execute(stmt)

            else:
                logger.info(f'Запись {badminton_player} отсутствует в БД')
                session.add(badminton_player)
            await session.commit()
    return badminton_player


async def update_b4u_in_bd(engine: AsyncEngine, b4u_account: B4U_Account):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            stmt = update(B4U_Account).where(B4U_Account.id == b4u_account.id).values(
                username=b4u_account.username,
                single_rating=b4u_account.single_rating,
                single_rating_date_of_calc=b4u_account.single_rating_date_of_calc,
                double_rating=b4u_account.double_rating,
                double_rating_date_of_calc=b4u_account.double_rating_date_of_calc,
                modified_at=datetime.now(),
            ).execution_options(synchronize_session="fetch")
            await session.execute(stmt)
            await session.commit()

        # result = await session.execute(select(B4U_Account).where(B4U_Account.id == b4u_account.id))
        # user = result.scalars().first()
        # stmt = update(B4U_Account).where(B4U_Account.id == user.id)
        # print(stmt)
        print(b4u_account)
        # stmt = update(B4U_Account).where(B4U_Account.id == b4u_account.id).values(**b4u_account).execution_options(synchronize_session="fetch")
        # result = await session.execute(stmt)

        # async with session.begin():
        #     session.add(b4u_account)
        #     session.update
        #     await session.commit()


async def async_main():
    db = await start_db()
    b4u_s = await fetch_all_b4u_accounts(db)
    # b4u = await B4U_Account(id=17284).smart_get(db, minutes_for_update=0.01)
    for account in b4u_s:
        b4u = await B4U_Account(id=account.id).smart_get(db, minutes_for_update=0.01)
        print(b4u)
    # print(b4u_s)

    # for i in range(10000):
    #     b4u = B4U_Account(id=i+1)
    #     b4u_2 = await b4u.get_from_site_by_id()
    #     if b4u_2:
    #         await b4u_2.create(db)


async def create_test_b4u_accs(engine: AsyncEngine):
    test_b4u_ids = [
        17264,
        17284,
        17287,
        17392
    ]
    for test_id in test_b4u_ids:
        b4u_player = await parse_b4u_by_id(test_id)
        await add_or_update_b4u_to_db(engine, b4u_player)


async def create_test_players_accs(engine: AsyncEngine):
    test_players = [
        Badminton_player(nickname='Никита', tg_id=202181776, b4u_id=17284),
        Badminton_player(nickname='Света', tg_id=35259859, b4u_id=17287),
        Badminton_player(nickname='Саша Ракита', tg_id=77873373, b4u_id=17392),
        Badminton_player(nickname='Player Unknown'),
    ]

    for players in test_players:
        await add_or_update_player_to_db(engine, players)


if __name__ == '__main__':
    start_time = time.time()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_main())
    loop.run_until_complete(asyncio.sleep(1))
    logger.info(f"Execution time: {time.time() - start_time} seconds")
