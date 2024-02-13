import mysql.connector
import pandas
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = sqlalchemy.orm.declarative_base()


class BooksNonProdManagement(Base):
    __tablename__ = 'books_non_prod_management'
    SL_No = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    MarketPlace = Column(String)
    Type = Column(String)
    Category = Column(String)


engine = create_engine(
    'mysql+pymysql://Books_prod:Zxcv!1234@ec2-54-70-46-145.us-west-2.compute.amazonaws.com:3306/prod')
Session = sessionmaker(bind=engine)
session = Session()
query = session.query(BooksNonProdManagement.MarketPlace, BooksNonProdManagement.Type, BooksNonProdManagement.Category)

Mp = []
Type = []
Category = []

for title, author, publisher in query:
    Mp.append(title)
    Type.append(author)
    Category.append(publisher)


# engine = create_engine(
#     "mysql+pymysql://Books_prod:Zxcv!1234@ec2-54-70-46-145.us-west-2.compute.amazonaws.com:3306/prod")
# Session = sessionmaker(bind=engine)
# session = Session()
#
# Base = sqlalchemy.orm.declarative_base()
#
#
# class User(Base):
#     __tablename__ = 'Prod_Database'
#
#     UserId = Column(String(50), primary_key=True, unique=True)
#     BuildAudit = Column(String(50))
#     BuildAuditDate = Column(Date)
#     LiveDate = Column(Date)
#     MarketPlace = Column(String(10))
#     Process = Column(String(75))
#     DealName = Column(String(75))
#     NDeal = Column(Integer)
#     SimLink = Column(String(150))
#     NTitle = Column(Integer)
#     NEmails = Column(Integer)
#     NOnsite = Column(Integer)
#     NPns = Column(Integer)
#     NVen = Column(Integer)
#     utilization = Column(Integer)
#
#
# Base.metadata.create_all(engine)
# config_data = {
#     "host": "ec2-54-70-46-145.us-west-2.compute.amazonaws.com",
#     "user": "Books_prod",
#     "passwd": "Zxcv@1234",
#     "port": 3306,
#     "database": "prod"
# }
#
# db = mysql.connector.connect(host=config_data["host"], user=config_data["user"], passwd=config_data["passwd"],
#                              port=config_data["port"], database=config_data["database"])
# cursor = db.cursor()
# cursor.execute('SELECT User FROM books_prod_user')
# username = cursor.fetchall()
# print(username)
