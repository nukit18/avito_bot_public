import sqlalchemy.dialects.postgresql
from sqlalchemy import Column, BigInteger, String, sql, Date, Boolean
from sqlalchemy.dialects import postgresql

from utils.db_api.db_gino import TimedBaseModel


class Url(TimedBaseModel):
    __tablename__ = 'urls'
    url = Column(String(500))
    user_id = Column(BigInteger, primary_key=True)
    name = Column(String(100), primary_key=True)
    in_parse = Column(Boolean)
    items_list = Column(postgresql.ARRAY(String(300)))

    query: sql.Select