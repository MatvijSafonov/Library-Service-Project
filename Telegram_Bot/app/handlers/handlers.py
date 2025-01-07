from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.keyboard import (
    menu,
    start_keyboard,
    get_books_pagination_keyboard,
    get_borrowings_pagination_keyboard,
)
from app.states.states import Login, Reg, RentBook
from app.services.api import (
    make_login_request,
    get_books,
    make_registration_request,
    get_borrowings,
    rent_book,
)

router = Router()


# Изменяем функции, использующие bot
async def send_message_to_user(chat_id: int, text: str, bot: Bot):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


# Handler for command /start------------------------------------------------------------
@router.message(CommandStart())
async def send_welcome(message: Message):
    chat_id = message.chat.id
    print(f"User chat_id: {chat_id}")
    await message.answer(
        f"Hello! Your chat_id is: {chat_id}", reply_markup=start_keyboard
    )


# Handler for command /login------------------------------------------------------------
@router.message(Command("login"))
async def cmd_login(message: Message, state: FSMContext):
    await message.answer("Enter your email:")
    await state.set_state(Login.email)


@router.message(StateFilter(Login.email))
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Now enter your password:")
    await state.set_state(Login.password)


@router.message(StateFilter(Login.password))
async def process_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()

    try:
        response_data = await make_login_request(data["email"], data["password"])
        # Save JWT in FSMContext
        await state.update_data(jwt_token=response_data.get("access"))
        await message.answer("Successfully authorized! ✅")
    except Exception as e:
        await message.answer(f"Authorization error: {str(e)} ❌")
    finally:
        # Don't clear state to save token
        await state.set_state(None)


# Handler for command /menu
@router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Меню", reply_markup=menu)


# Handler for command /help
@router.message(Command("help"))
async def get_help(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data.get("jwt_token")

    if token:
        help_text = (
            "🟢 Status: Authorized\n"
            "Available commands:\n"
            "/menu - Show main menu\n"
            "/contacts - Show contacts\n"
            "/reg - Register new account\n"
            "❗️ You can use all bot features"
        )
    else:
        help_text = (
            "🔴 Status: Unauthorized\n"
            "Available commands:\n"
            "/login - Authorize in system\n"
            "/reg - Register new account\n"
            "❗️ Please login to use all features"
        )

    await message.answer(help_text)


# Handler for command /contacts
@router.message(Command("contacts"))
async def get_contacts(message: Message):
    await message.answer(
        """
📞 Phone: +380123456789
📧 Email: Example@user.com
✈️ Telegram: @example
🚕 Address: Example street, 123
    """
    )


# Handler for registration--------------------------------------------------------------
@router.message(Command("reg"))
async def register(message: Message, state: FSMContext):
    await state.set_state(Reg.email)
    await message.answer("Enter your email for registration:")


@router.message(StateFilter(Reg.email))
async def process_reg_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Enter your password:")
    await state.set_state(Reg.password)


@router.message(StateFilter(Reg.password))
async def process_reg_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()

    try:
        # Register user with chat_id
        reg_response = await make_registration_request(  # noqa
            data["email"], data["password"], str(message.chat.id)
        )
        await message.answer("Successfully registered! ✅")

        # Auto login after registration
        login_response = await make_login_request(data["email"], data["password"])
        await state.update_data(jwt_token=login_response.get("access"))
        await message.answer("You have been automatically logged in! ✅")

    except Exception as e:
        await message.answer(f"Registration error: {str(e)} ❌")
    finally:
        await state.set_state(None)


# Handler for command "📚 All Books"----------------------------------------------------
@router.callback_query(F.data == "all_books")
async def show_books(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.get("jwt_token")

    if not token:
        await callback.answer("Please login first! /login")
        return

    try:
        books = await get_books(token)
        formatted_text = "📚 Books list:\n\n"

        for book in books["results"]:
            formatted_text += (
                f"📖 Title: {book['title']}\n"
                f"👤 Author: {book['author']['first_name']} "
                f"{book['author']['last_name']}\n\n"
            )

        keyboard = get_books_pagination_keyboard(
            books["next"] is not None, books["previous"] is not None, 1
        )

        await callback.message.answer(formatted_text, reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Error: {str(e)}")


@router.callback_query(lambda c: c.data.startswith("books_page_"))
async def process_books_page(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[2])
    data = await state.get_data()
    token = data.get("jwt_token")

    try:
        books = await get_books(token, page)
        formatted_text = "📚 Books list:\n\n"

        for book in books["results"]:
            formatted_text += (
                f"📖 Title: {book['title']}\n"
                f"👤 Author: {book['author']['first_name']} "
                f"{book['author']['last_name']}\n\n"
            )

        keyboard = get_books_pagination_keyboard(
            books["next"] is not None, books["previous"] is not None, page
        )

        await callback.message.edit_text(formatted_text, reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Error: {str(e)}")


@router.callback_query(F.data == "login")
async def login_button(callback: CallbackQuery, state: FSMContext):
    await cmd_login(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "reg")
async def register_button(callback: CallbackQuery, state: FSMContext):
    await register(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "my_books")
async def show_borrowings(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.get("jwt_token")

    if not token:
        await callback.answer("Please login first! /login")
        return

    try:
        borrowings = await get_borrowings(token)
        formatted_text = "📚 Your Borrowed Books:\n\n"

        for item in borrowings["results"]:
            formatted_text += (
                f"📖 Borrowing ID: {item['id']}\n"
                f"📅 Borrow Date: {item['borrow_date']}\n"
                f"⏳ Return Date: {item['expected_return_date']}\n"
                f"✅ Returned: {item['actual_return_date'] or 'Not returned'}\n\n"
            )

        keyboard = get_borrowings_pagination_keyboard(
            borrowings["next"] is not None, borrowings["previous"] is not None, 1
        )

        await callback.message.answer(formatted_text, reply_markup=keyboard)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"Error: {str(e)}")


@router.callback_query(lambda c: c.data.startswith("borrow_page_"))
async def process_borrowings_page(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[2])
    data = await state.get_data()
    token = data.get("jwt_token")

    try:
        borrowings = await get_borrowings(token, page)
        formatted_text = "📚 Your Borrowed Books:\n\n"

        for item in borrowings["results"]:
            status_emoji = "✅" if item["actual_return_date"] else "❌"
            formatted_text += (
                f"📖 Borrowing ID: {item['id']}\n"
                f"📅 Borrow Date: {item['borrow_date']}\n"
                f"⏳ Return Date: {item['expected_return_date']}\n"
                f"{status_emoji} Returned: "
                f"{item['actual_return_date'] or 'Not returned'}\n\n"
            )

        keyboard = get_borrowings_pagination_keyboard(
            borrowings["next"] is not None, borrowings["previous"] is not None, page
        )

        await callback.message.edit_text(formatted_text, reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Error: {str(e)}")


@router.message(StateFilter(RentBook.return_date))
async def process_return_date(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await rent_book(data["jwt_token"], int(data["book_id"]), message.text)
        await message.answer(
            "Book rented successfully! ✅\nYou will receive payment link soon."
        )
    except Exception as e:
        await message.answer(f"Error: {str(e)} ❌")
    finally:
        await state.clear()


@router.callback_query(F.data == "rent_book")
async def start_rent(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.get("jwt_token")

    if not token:
        await callback.answer("Please login first! /login")
        return

    await callback.message.answer("Enter book ID to rent:")
    await state.set_state(RentBook.book_id)
    await callback.answer()


@router.message(StateFilter(RentBook.book_id))
async def process_book_id(message: Message, state: FSMContext):
    try:
        book_id = int(message.text)
        await state.update_data(book_id=book_id)
        await message.answer("Enter expected return date (YYYY-MM-DD):")
        await state.set_state(RentBook.return_date)
    except ValueError:
        await message.answer("Please enter a valid book ID (number)!")
