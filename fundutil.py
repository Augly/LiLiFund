from pathlib import Path
import joblib
import sqlalchemy
from loguru import logger
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

home_dir = Path(__file__).parent
data_dir = home_dir / 'data'
db = 'sqlite:///' + str(data_dir / 'fund.db') + '?check_same_thread=False'
select_fund_filename = str(home_dir / "data" / "select_fund_set.pkl")
echo = False
engine = sqlalchemy.create_engine(db, echo=True)
session = sessionmaker(bind=engine)()
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
title = "李礼基金投资系统"
base = declarative_base()


class FundList(base):
    __tablename__ = 'fund_list'
    id = Column(Integer, autoincrement=True, primary_key=True)
    code = Column(String, index=True)
    name = Column(String)
    type = Column(String)
    trade_status = Column(String)

    def __repr__(self):
        return 'FundList ' + self.code


def delete_table(class_obj):
    class_obj.__table__.drop(engine)


base.metadata.create_all(engine)

if __name__ == '__main__':
    # delete_table(StockList)
    pass
