from aiogram.fsm.state import State, StatesGroup


class Login(StatesGroup):
    email = State()
    password = State()


class Reg(StatesGroup):
    email = State()
    password = State()


class RentBook(StatesGroup):
    book_id = State()
    return_date = State()
