import os
import asyncio
from contextlib import suppress

from dotenv import load_dotenv
from telethon import TelegramClient as TC
from telethon.tl.functions.account import UpdateStatusRequest as USR


class TelegramOnline:
    """
        Класс позволяет добавлять телеграм аккаунты и держать их в онлайн
    """

    def __init__(self, api_id: int, api_hash: str, directory: str) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.directory = directory

    def create_folder(self) -> None:
        """
            Метод создаёт директорию для хранения сессий телеграм аккаунтов, если она не существует

        :return: None
        """
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

    async def add_new_session(self) -> None:
        """
            Метод позволяет добавить новую сессию телеграм аккаунта

        :return: None
        """
        phone = input('Введите номер телефона: ')
        client = TC(self.directory + phone, api_id=self.api_id, api_hash=self.api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            await client.sign_in(phone, input('Введите код: '))
            print(f'Аккаунт с номером "{phone}", добавлен')
        else:
            print(f'Аккаунт с номером "{phone}", был добавлен ранее и всё ещё активен')

        await client.disconnect()
        return await main()

    async def send_status_online(self, session: str) -> None:
        """
            Метод отправляет статус онлайн на телеграм аккаунт

        :param session: Путь к сессии телеграм аккаунта
        :return: None
        """
        async with TC(session, api_id=self.api_id, api_hash=self.api_hash) as client:
            if await client.is_user_authorized():
                print(f'Аккаунт с номером: "+{session}", теперь онлайн')
                while True:
                    await client(USR(offline=False))
                    await asyncio.sleep(15)
            else:
                print(f'Попытка входа в аккаунт с номером: "+{session}" завершилась неудачно')

    async def get_all_sessions(self) -> list:
        """
            Метод получает все сессии телеграм аккаунтов в заданной директории и возвращает их в виде списка

        :return: list
        """
        sessions = []
        for session in os.listdir(self.directory):
            if session.count('.session') >= 1:
                sessions.append(self.directory + session)
        if sessions:
            return sessions
        else:
            print('Вы не добавили ни одного аккаунта')

    async def sender(self) -> None:
        """
            Метод позволяет одновременно отправлять статус онлайн на все телеграм аккаунты

        :return: None
        """
        tasks = []
        for session in await self.get_all_sessions():
            tasks.append(asyncio.create_task(self.send_status_online(session)))

        await asyncio.gather(*tasks)


async def main() -> None:
    """
        Основная функция запуска проекта, содержащая небольшое меню

    :return: None
    """
    telegram_online = TelegramOnline(int(os.getenv("API_ID")), os.getenv("API_ID"), os.getenv("DIRECTORY"))
    telegram_online.create_folder()
    actions = {
        '1': ['Добавить аккаунт', telegram_online.add_new_session],
        '2': ['Запустить онлайн', telegram_online.sender]
    }
    for action in actions:
        print(f"{action}. {actions[str(action)][0]}")
    await actions[input('Выберите действия: ')][1]()


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    with suppress(KeyboardInterrupt):
        asyncio.run(main())
