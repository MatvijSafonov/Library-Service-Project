import aiohttp
from typing import Dict


async def make_login_request(email: str, password: str) -> Dict:
    async with aiohttp.ClientSession() as session:
        # API request for login
        async with session.post(
            "http://app:8000/api/users/token/",
            json={"email": email, "password": password},
        ) as response:
            if response.status == 200:
                return await response.json()
            raise Exception(f"Authorization error: {response.status}")


async def make_registration_request(
    email: str, password: str, telegram_chat_id: str
) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://app:8000/api/users/",
            json={
                "email": email,
                "password": password,
                "telegram_chat_id": telegram_chat_id,
            },
        ) as response:
            if response.status == 201:
                return await response.json()
            raise Exception(f"Registration error: {response.status}")


async def get_books(token: str, page: int = 1) -> Dict:
    headers = {"Authorize": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://app:8000/api/library/books/?page={page}", headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            raise Exception(f"Error fetching books: {response.status}")


async def get_borrowings(token: str, page: int = 1) -> Dict:
    headers = {
        "Authorize": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        url = f"http://app:8000/api/borrowings/?page={page}"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 401:
                raise Exception("Authentication failed")
            raise Exception(f"Error fetching borrowings: {response.status}")


async def rent_book(token: str, book_id: int, expected_return_date: str) -> Dict:
    headers = {"Authorize": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"book": book_id, "expected_return_date": expected_return_date}
    print(f"Debug - Request data: {data}")  # Отладка запроса

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://app:8000/api/borrowings/", headers=headers, json=data
        ) as response:
            print(f"Debug - Status: {response.status}")  # Отладка статуса
            if response.status == 201:
                return await response.json()
            text = await response.text()
            print(f"Debug - Error response: {text}")  # Отладка ответа
            raise Exception(f"Error renting book: {response.status} - {text}")
