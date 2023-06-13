import asyncio

from data import config
from utils.db_api import quick_cmd_urls
from utils.db_api.db_gino import db


async def test():
    await db.set_bind(config.POSTGRES_URI)
    await db.gino.drop_all()
    await db.gino.create_all()

    print("Добавляем ссылки")
    await quick_cmd_urls.add_url(url="akdfkskds", user_id=123, name="first")
    await quick_cmd_urls.add_url(url="ewferg", user_id=123, name="second")
    await quick_cmd_urls.add_url(url="ewferg", user_id=12, name="second")

    print("Получаем все")
    print(await quick_cmd_urls.select_all_urls())

    print("Получаем ссылки одного пользователя")
    print(await quick_cmd_urls.get_urls_user(123))

    print("Удаляем одного")
    await quick_cmd_urls.delete_url_user(name="second", user_id=123)

    print("Получаем все")
    print(await quick_cmd_urls.select_all_urls())

    print("Проверяем доступность создания нового")
    print(await quick_cmd_urls.check_name_url(12, "third"))
    print(await quick_cmd_urls.check_name_url(12, "second"))

    print("Проверяем будет ли найден ключ которого нет")
    print(await quick_cmd_urls.check_name_url(1234, "2222"))

    print("Добавляем 130 ссылок, должно остаться 120")
    for i in range(0, 130):
        await quick_cmd_urls.add_item_to_list(user_id=123, name="first", item=f"avito.ru/{i}")
    items_list = await quick_cmd_urls.get_items_list(user_id=123, name="first")
    print(items_list)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())