from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
import sqlalchemy as sa

from datetime import datetime, date, time
from data import config
import logging
from typing import List

# TODO: сделать асинхронной с помощью GINO

DATABASE = {
    'drivername': config.driver_name,
    'host': config.DATABASE_HOST,
    'port': config.DATABASE_PORT,
    'username': config.DATABASE_USER,
    'password': config.DATABASE_PASSWORD,
    'database': config.DATABASE_NAME
}
DeclarativeBase = declarative_base()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Person(DeclarativeBase):
    __tablename__ = 'persons'

    id = sa.Column(sa.Integer, primary_key=True)  # ID
    name_or_nickname = sa.Column(sa.String(100))  # имя
    tg_account = sa.orm.relationship("TG_Account", backref='person', uselist=False)  # аккаунт Telegram
    activision_account = sa.Column('activision_account', sa.String(100))  # аккаунт ACTIVISION
    psn_account = sa.Column('psn_account', sa.String(100))  # аккаунт PSN
    blizzard_account = sa.Column('blizzard_account', sa.String(100))  # аккаунт Blizzard
    xbox_account = sa.Column('xbox_account', sa.String(100))  # аккаунт X-Box
    platform = sa.Column(sa.Integer, sa.ForeignKey('platforms.id'), nullable=True)  # (PC, PS4, Xbox Series X)
    input_device = sa.Column(sa.Integer, sa.ForeignKey('input_devices.id'), nullable=True)  # клавамышь или геймпад?
    about_yourself = sa.Column('about_yourself', sa.String(500))  # о себе
    created_at = sa.Column('created_at', sa.TIMESTAMP, default=datetime.now())  # дата создания аккаунта
    modified_at = sa.Column('modified_at', sa.TIMESTAMP, default=datetime.now())  # дата изменения аккаунта
    kd_warzone = sa.Column('kd_warzone', sa.Float(2, 2))  # КД Варзон
    kd_multiplayer = sa.Column('kd_multiplayer', sa.Float(2, 2))  # КД мультиплеер
    kd_cold_war_multiplayer = sa.Column('kd_cold_war_multiplayer', sa.Float(2, 2))  # КД Колдвар
    modified_kd_at = sa.Column('modified_kd_at', sa.TIMESTAMP)  # дата обновления статистики

    def __repr__(self):
        return "<Person: (id: '%s', nickname: '%s', tg_acc: '%s')>" % (self.id, self.name_or_nickname, self.tg_account)

    def full_print(self):
        return "<Person: (id: '%s', nickname: '%s', tg_acc: '%s')>" % (self.id, self.name_or_nickname, self.tg_account)


class TG_Account(DeclarativeBase):
    __tablename__ = 'tg_accounts'

    # id = sa.Column(sa.Integer, primary_key=True)
    # username: Column = sa.Column(sa.String(100))
    # person_id = sa.Column(sa.Integer, sa.ForeignKey('persons.id'), nullable=False)
    id = sa.Column('id', sa.Integer, primary_key=True)
    is_bot = sa.Column('is_bot', sa.Boolean, default=False)
    first_name = sa.Column('first_name', sa.String(100))
    last_name = sa.Column('last_name', sa.String(100))
    language_code = sa.Column('language_code', sa.String(50))
    created_at = sa.Column('created_at', sa.TIMESTAMP, default=datetime.now())
    modified_at = sa.Column('modified_at', sa.TIMESTAMP, default=datetime.now())

    # def __repr__(self):
    #     return "<TG_Account: (id: '%s', username: '%s', first_name: '%s')>" % (self.id, self.username, self.first_name)


class PlatformType(DeclarativeBase):
    __tablename__ = 'platform_types'
    id = sa.Column(sa.Integer, primary_key=True)  # ID
    name = sa.Column(sa.String(100), unique=True)  # (PC, PS, Xbox)
    description = sa.Column('description', sa.String(500))  # Personal Computer/Playstation/Xbox


class Platform(DeclarativeBase):
    __tablename__ = 'platforms'
    id = sa.Column(sa.Integer, primary_key=True)  # ID
    name = sa.Column(sa.String(100), unique=True)  # (PS4, PS5, PS4 Pro)
    description = sa.Column('description', sa.String(500))  # Personal Computer/Playstation 4/Xbox Series X
    device_type = sa.Column(sa.Integer, sa.ForeignKey('platform_types.id'), nullable=True)  # (PC, PS, Xbox)


class InputDeviceType(DeclarativeBase):
    __tablename__ = 'input_device_types'
    id = sa.Column(sa.Integer, primary_key=True)  # ID
    name = sa.Column(sa.String(100), unique=True)  # mouse, gamepad
    description = sa.Column('description', sa.String(500))  # mouse, gamepad


class InputDevice(DeclarativeBase):
    __tablename__ = 'input_devices'
    id = sa.Column(sa.Integer, primary_key=True)  # ID
    name = sa.Column(sa.String(100), unique=True)  # mouse, Dualsense
    description = sa.Column('description', sa.String(500))  # mouse, Dualsense
    device_type = sa.Column(sa.Integer, sa.ForeignKey('input_device_types.id'), nullable=True)  # mouse, gamepad


class DB:

    def __init__(self, db_config=None):
        if db_config is None:
            db_config = DATABASE
        self.engine = create_engine(URL(**db_config))
        DeclarativeBase.metadata.create_all(self.engine)
        Session = sa.orm.sessionmaker(bind=self.engine)
        self.session = Session()


    def close(self):
        session = self.session
        session.close()


    def is_tg_account_exists(self, tg_id=None, tg_username=None):
        """Проверяем, существует ли указанный аккаунт Telegram в БД с данным ID"""

        engine = self.engine
        session = self.session

        with engine.connect() as conn:
            if tg_username is None:
                if session.query(TG_Account).filter_by(id=tg_id).first():
                    return True
            if tg_id is None:
                if session.query(TG_Account).filter_by(username=tg_username).first():
                    return True
            if (tg_id is not None) and (tg_username is not None):
                if session.query(TG_Account).filter_by(id=tg_id, username=tg_username).first():
                    return True
        return False

    def get_tg_account(self, tg_id=None, tg_username=None) -> TG_Account:
        """По указанному ID получаем объект"""
        engine = self.engine
        session = self.session
        with engine.connect() as conn:
            if self.is_tg_account_exists(tg_id, tg_username):
                if tg_username is None:
                    tg_account = session.query(TG_Account).filter_by(id=tg_id).first()
                if tg_id is None:
                    tg_account = session.query(TG_Account).filter_by(username=tg_username).first()
                if (tg_id is not None) and (tg_username is not None):
                    tg_account = session.query(TG_Account).filter_by(id=tg_id, username=tg_username).first()
                conn.close()
                return tg_account

    def update_tg_account(self, tg_account: TG_Account):
        """Обновляем данные об участнике"""

        with self.engine.connect() as conn:
            if self.is_tg_account_exists(tg_account.id):
                print('Данный пользователь найден в БД, сейчас обновим')
                try:
                    self.session.add(tg_account)
                    self.session.commit()
                    return True
                except Exception as ex:
                    print('Обновить данные пользователя в БД не получилось, ошибка', ex)
            else:
                print('Нет пользователя с данным ID в БД')
                return False

    def is_person_exists(self, tg_account=None, person_id=None):
        """Проверяем, существует ли указанный аккаунт Telegram в БД с данным ID"""

        engine = self.engine
        session = self.session
        result = False
        with engine.connect() as conn:
            if person_id is None:
                # print('case1: ', session.query(Person).filter_by(tg_account=tg_account).first())
                if session.query(Person).filter_by(tg_account=tg_account).first():
                    result = True
            if tg_account is None:
                # print('case2: ', session.query(Person).filter_by(id=person_id).first())
                if session.query(Person).filter_by(id=person_id).first():
                    result = True
            if (tg_account is not None) and (person_id is not None):
                # print('case3: ', session.query(Person).filter_by(id=person_id).first())
                if session.query(Person).filter_by(id=person_id, tg_account=tg_account).first():
                    result = True
            return result

    def get_person_by_tg_account(self, tg_account) -> Person:
        """По указанному ID получаем объект"""
        engine = self.engine
        session = self.session
        with engine.connect() as conn:
            if self.is_tg_account_exists(tg_account.id, tg_account.username):
                member = session.query(Person).filter_by(tg_account=tg_account).first()
                return member

    def get_all_persons(self, **config_filter) -> List[Person]:
        """По указанному ID получаем объект"""

        with self.engine.connect() as conn:
            members = self.session.query(Person).filter_by(**config_filter).all()
            return members

    def get_all_platforms(self, **config_filter) -> List[Platform]:
        """По указанному ID получаем объект"""

        with self.engine.connect() as conn:
            platforms = self.session.query(Platform).filter_by(**config_filter).all()
            return platforms

    def get_all_input_devices(self, **config_filter) -> List[InputDevice]:
        """По указанному ID получаем объект"""

        with self.engine.connect() as conn:
            devices = self.session.query(InputDevice).filter_by(**config_filter).all()
            return devices

    def add_member_using_tg_id(self, tg_account: TG_Account):
        """Добавляем участника"""

        with self.engine.connect() as conn:
            if self.get_tg_account(tg_id=tg_account.id):
                print('Аккаунт с таким ID есть в базе данных')
            else:
                print('Нет такого аккаунта в базе данных')
                try:
                    tg_account.person = Person()
                    self.session.add(tg_account)
                    self.session.commit()
                finally:
                    return True
        return False



    def update_person(self, person: Person):
        """Обновляем данные об участнике"""

        with self.engine.connect() as conn:
            if self.is_person_exists(person.tg_account, person.id):
                print('Данный пользователь найден в БД, сейчас обновим')
                try:
                    person.modified_at = datetime.now()
                    self.session.add(person)
                    self.session.commit()
                    return True
                finally:
                    pass
            else:
                print('Нет пользователя с данным ID в БД')
                return False

    def migration_from_old_bd(self):
        values = self.session.execute('SELECT * FROM cod_users ORDER BY id')
        users = []
        for value in values:
            user = {
                'tg_id': value[1],
                'tg_name': value[2],
                'name': value[3],
                'psn_id': value[4],
                'activision_id': value[5],
                'kd_warzone': None,
                'kd_mw19_multiplayer': None
            }
            try:
                user['kd_warzone'] = float(value[6])
            except:
                pass
            try:
                user['kd_mw19_multiplayer'] = float(value[7])
            except:
                pass

            logger.info(user)
            users.append(user)

        for user in users:
            person = Person(
                name_or_nickname=user['name'],
                activision_account=user['activision_id'],
                psn_account=user['psn_id'],
                kd_warzone=user['kd_warzone'],
                kd_multiplayer=user['kd_mw19_multiplayer'],
                tg_account=TG_Account(id=user['tg_id'], username=user['tg_name'])
            )
            print(person)
            try:
                self.session.add(person)
                self.session.commit()
                print(person, ' - добавлен в БД')
            except Exception as ex:
                print(person, ', ОШИБКА: ', ex)

    def create_devices(self):
        pass


def main():
    db = DB()
    # db.migration_from_old_bd()

    # print(values)

    # nikita = Person(name_or_nickname='Nikita_Ivanov')
    # nikita_tg = TG_Account(username='npopok', id=654321, person=nikita)
    # db.session.add(nikita)
    # db.session.add(nikita_tg)
    # db.session.commit()
    # nikita_person = db.session.query(Person).filter_by(name_or_nickname='Nikita_Ivanov').first()
    # print(nikita_person)
    # print(db.is_tg_account_exists(654321))  # Да
    # print(db.is_tg_account_exists(983276544))  # Нет
    # print(db.is_tg_account_exists(tg_username="npopok"))  # Да
    # print(db.is_tg_account_exists(tg_username='Nikita_Petukhov'))  # Нет
    # nikita_tg = db.get_tg_account(tg_id=654321)
    # print(nikita_tg)
    # db.session.delete(nikita_tg)
    # db.session.commit()
    # print(db.is_tg_account_exists(654321))  # Нет
    # print(db.is_person_exists(person_id=1))
    # print(db.is_person_exists(person_id=3))
    # print(db.is_person_exists(tg_account=nikita_tg, person_id=3))
    # print(db.is_person_exists(tg_account=nikita_tg, person_id=4))
    # nikita_person = db.get_person_by_tg_account(nikita_tg)
    # print(nikita_person)
    # persons = db.get_all_persons()
    #
    # for person in persons:
    #     print(person)

    # tg_account = TG_Account(id=6543212)
    # a = db.add_member_using_tg_id(tg_account)
    # print(a)

    # nikita_tg = db.get_tg_account(tg_id=65400321)
    # print(nikita_tg)
    # nikita_person = db.get_person_by_tg_account(nikita_tg)
    # nikita_person.input_devices = 'Клава'
    # db.update_person(nikita_person)


if __name__ == "__main__":
    main()
