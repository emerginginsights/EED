from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Column, String, Numeric

db = SQLAlchemy()


class Country(db.Model):
    __tablename__ = 'countrydb'

    country_id = Column(Integer, primary_key=True)
    country_name = Column(String)
    country_isoid = Column(String)
    # country_flag BYTEA,
    # country_map BYTEA,
    country_description = Column(String)
    country_area = Column(Integer)
    country_language = Column(String)
    # country_prev_election DATE,
    # country_next_election DATE


class Indicator(db.Model):
    __tablename__ = 'indicatordb'

    indicator_id = Column(Integer, primary_key=True)
    indicator_api_code = Column(String)
    indicator_name = Column(String)
    indicator_description = Column(String)
    indicator_source = Column(String)
    indicator_topic = Column(String)
    country_id = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)
    indicator_value = Column(Numeric, primary_key=True)
