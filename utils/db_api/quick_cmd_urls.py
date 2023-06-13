import threading
from datetime import date, datetime
from sqlalchemy import sql
from asyncpg import UniqueViolationError

from utils.db_api.db_gino import db
from utils.db_api.schemas.urls_parsing import Url
import secrets

from utils.misc.avito_parser import parsing_urls


async def add_url(url: str, user_id: int, name: str, in_parse: bool = True):
    try:
        url = Url(url=url, user_id=user_id, name=name, in_parse=in_parse, items_list=[])
        await url.create()
        threading.Thread(target=parsing_urls, args=(url.url, url.name, url.user_id)).start()

    except UniqueViolationError:
        pass


async def all_in_parse_false():
    urls = await Url.query.gino.all()
    for url in urls:
        await url.update(in_parse=False).apply()


async def select_all_urls():
    urls = await Url.query.gino.all()
    return urls


async def get_urls_user(user_id: int):
    urls = await Url.query.where(Url.user_id == user_id).gino.all()
    return urls


async def check_name_url(user_id: int, name: str):
    urls = await Url.query.where(Url.user_id == user_id).gino.all()
    return name in [url.name for url in urls]


async def delete_url_user(user_id: int, name: str):
    url = await Url.query.where(Url.name == name and Url.user_id == user_id).gino.first()
    await url.delete()


async def add_item_to_list(user_id: int, name: str, item: str):
    user = await Url.query.where(Url.name == name and Url.user_id == user_id).gino.first()
    items_list = user.items_list
    if len(items_list) >= 120:
        items_list.pop(0)
    items_list.append(item)
    await user.update(items_list=items_list).apply()


async def add_item_p2_to_list(user_id: int, name: str, item: str):
    user = await Url.query.where(Url.name == name and Url.user_id == user_id).gino.first()
    items_list = user.items_list
    new_items_list = [item]
    new_items_list += items_list
    await user.update(items_list=new_items_list).apply()


async def get_items_list(user_id: int, name: str):
    user = await Url.query.where(Url.name == name and Url.user_id == user_id).gino.first()
    return user.items_list


async def remove_items_list(user_id: int, name: str):
    user = await Url.query.where(Url.name == name and Url.user_id == user_id).gino.first()
    await user.update(items_list=[]).apply()