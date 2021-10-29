from aiogram.dispatcher.filters.state import State, StatesGroup


class RegPlayerState(StatesGroup):

    intro_player_out_db = State()  # при старте бота, если игрок не найден в БД
    intro_player_in_db = State()  # при старте бота, если игрок найден в БД

    username_ask = State()
    username_entered = State()

    profile_correctly_save = State()
    profile_correctly_renamed = State()
    profile_correctly_b4u_input = State()
    profile_correctly_vk_input = State()


    profile_renaming = State()
    profile_vk_input = State()
    profile_b4u_input = State()
    # profile_correctly_save = State()
    # profile_correctly_save = State()
    # profile_correctly_save = State()



    no_person_in_db = State()
    show_profile_or_stats = State()
    showing_person_data = State()
    showing_statistics = State()
    edit_profile = State()


class StogovaScheduleState(StatesGroup):
    show_details = State
    hide_details = State


