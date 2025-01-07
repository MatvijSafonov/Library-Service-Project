from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder  # noqa

menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📖 Rent Book", callback_data="rent_book"),
        ],
        [InlineKeyboardButton(text="❗️ My Borrowed Books", callback_data="my_books")],
        [
            InlineKeyboardButton(text="📚 All Books", callback_data="all_books"),
        ],
    ]
)

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Login ✅", callback_data="login"),
            InlineKeyboardButton(text="👤 Register 👤", callback_data="reg"),
        ]
    ]
)


def get_books_pagination_keyboard(
    has_next: bool, has_prev: bool, current_page: int
) -> InlineKeyboardMarkup:
    buttons = []
    if has_prev:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Previous", callback_data=f"books_page_{current_page-1}"
            )
        )
    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text="Next ➡️", callback_data=f"books_page_{current_page+1}"
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_borrowings_pagination_keyboard(
    has_next: bool, has_prev: bool, current_page: int
) -> InlineKeyboardMarkup:
    buttons = []
    if has_prev:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Previous", callback_data=f"borrow_page_{current_page-1}"
            )
        )
    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text="Next ➡️", callback_data=f"borrow_page_{current_page+1}"
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
