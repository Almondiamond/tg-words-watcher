from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    add_word_prompt = State()
    delete_word_prompt = State()
