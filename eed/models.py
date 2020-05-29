from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Column, String, Numeric, Date, LargeBinary

db = SQLAlchemy()


class Country(db.Model):
    __tablename__ = 'countrydb'

    country_id = Column(Integer, primary_key=True)
    country_name = Column(String)
    country_isoid = Column(String)
    country_flag = Column(LargeBinary)
    country_map = Column(LargeBinary)
    country_description = Column(String)
    country_area = Column(Integer)
    country_language = Column(String)
    country_prev_election = Column(Date)
    country_next_election = Column(Date)

    def res_dict(self):
        return {
            'country_name': self.country_name,
            'country_id': self.country_id,
            'language': self.country_language,
            'description': self.country_description,
            'iso_id': self.country_isoid,
            'prev_election': self.country_prev_election,
            'next_election': self.country_next_election,
        }


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
