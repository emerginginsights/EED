import csv
import datetime
import json
import os
import sys

import psycopg2
import wbdata
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

Country_table = []
Indicator_table = []
country_list = list()
indicator_list = list()
results = list()

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# Configure by environment variables
DB_NAME = os.getenv('EED_DB_NAME', 'test_worldbank')
DB_HOST = os.getenv('EED_DB_HOST', 'localhost')
DB_USER = os.getenv('EED_DB_USER', 'postgres')
DB_PASS = os.getenv('EED_DB_PASS', 'postgres')

START_YEAR = int(os.getenv('EED_START_YEAR', '2010'))
END_YEAR = int(os.getenv('EED_END_YEAR', '2019'))


# Definition of the Indicator class
class Indicator:

    def __init__(self, name, identifier, code, source, max, min, average, sum):
        self.name = name
        self.identifier = identifier
        self.API_Code = code
        self.source = source
        self.max = max
        self.min = min
        self.average = average
        self.sum = sum


# Definition of the Indicator class
class Aggregate:

    def __init__(self, name=None, identifier=None, iso=None):
        self.name = name
        self.identifier = identifier
        self.iso = iso

        self.countries = list()
        self.indicators = list()

    def add_country(self, country):
        self.countries.append(country)


# Definition of the Country class
class Country:

    def __init__(self, id, name, iso):
        self.id = id
        self.name = name
        self.iso = iso


def country_translation(name):
    for item in country_list:
        for value in item.values():
            if name == value:
                return item['country_id']


def indicator_translation(name):
    for item in indicator_list:
        for value in item.values():
            if name == value:
                indicator_id = item['indicator_id']
                indicator_api_code = item['indicator_api_code']
                indicator_description = item['indicator_description']
                indicator_source = item['indicator_source']
                indicator_topic = item['indicator_topic']
                return indicator_id, indicator_api_code, indicator_description, indicator_source, indicator_topic


def init_dataset():
    # create global Indicator_table from indicator.cfg
    with open(os.path.join(SCRIPT_PATH, 'Mindicators.csv'), newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        global Indicator_table
        Indicator_table = data[1:]

    # create global Country_table from indicator.cfg
    with open(os.path.join(SCRIPT_PATH, 'Mcountries.csv'), newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        global Country_table
        Country_table = data[1:]

    for idx, country in enumerate(Country_table):
        country_dict = dict()  # country_dict must this format: {'country_id': '', 'country_name': '', 'country_ISOid': ''}
        country_dict['country_id'] = idx + 1
        country_dict['country_name'] = country[2]
        country_dict['country_ISOid'] = country[1]
        country_list.append(country_dict)

    for indicator in Indicator_table:
        indicator_dict = dict()
        # indicator_dict must this format: {'indicator_id': '', 'indicator_api_code': '', 'indicator_name': '' , 'indicator_description': '', 'indicator_source' :'', 'indicator_topic' :''}
        indicator_dict['indicator_id'] = indicator[2]
        indicator_dict['indicator_api_code'] = indicator[0]
        indicator_dict['indicator_name'] = indicator[1]
        indicator_dict['indicator_description'] = indicator[3]
        indicator_dict['indicator_source'] = indicator[4]
        indicator_dict['indicator_topic'] = indicator[5]
        indicator_list.append(indicator_dict)


def retrieve_external_data(start_year=START_YEAR, end_year=END_YEAR):
    print('Getting data.......', start_year, '-', end_year)
    data_date = (datetime.datetime(start_year, 1, 1), datetime.datetime(end_year, 1, 1))
    indicators = dict()
    for i in Indicator_table:
        indicators[i[0]] = i[1]

    countries = [country[0] for country in Country_table]

    res = wbdata.get_dataframe(indicators, country=countries, data_date=data_date)
    print("fetched...")
    json_res = res.to_dict('index')

    none_countries = []
    for key, value in json_res.items():
        country_id = country_translation(key[0])
        if country_id is None:
            none_countries.append(key)
            continue

        year = key[1]
        for k, v in value.items():
            indicator_dict = dict()  # {'indicator_id': '', 'indicator_api_code': '', 'indicator_name': '' , 'indicator_description': '', 'indicator_source' :'', 'indicator_topic' :''}
            indicator_id, indicator_api_code, indicator_description, indicator_source, indicator_topic = indicator_translation(k)
            indicator_dict['indicator_id'] = indicator_id
            indicator_dict['country_id'] = country_id
            indicator_dict['year'] = year
            indicator_dict['indicator_name'] = k
            indicator_dict['indicator_api_code'] = indicator_api_code
            indicator_dict['indicator_description'] = indicator_description
            indicator_dict['indicator_source'] = indicator_source
            indicator_dict['indicator_topic'] = indicator_topic
            indicator_dict['indicator_value'] = v
            results.append(indicator_dict)

    # export json if countries is none
    with open('none_countries.json', 'w') as outfile:
        json.dump(none_countries, outfile)

    insert_table('countryDB', country_list)
    truncate_table('indicatorDB')

    for result in results:
        if result['indicator_value'] is None:
            result['indicator_value'] = 0
        if str(result['indicator_value']) == 'nan':
            result['indicator_value'] = 0

    with open('results.json', 'w') as outfile:
        json.dump(results, outfile)

    insert_table('indicatorDB', results)
    print("Data Loading FINISHED.")


def create_db():
    con = psycopg2.connect(dbname='postgres', user=DB_USER, password=DB_PASS, host=DB_HOST)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        sql = '''CREATE database {} '''.format(DB_NAME)
        cur.execute(sql)
        cur.close()
        con.commit()
    except psycopg2.ProgrammingError as e:
        print(e)
    finally:
        if con is not None:
            con.close()


def create_table():
    con = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        commands = [
            '''
                CREATE TABLE countryDB (
                    country_id SERIAL PRIMARY KEY,
                    country_name VARCHAR,
                    country_ISOid VARCHAR,
                    country_flag BYTEA,
                    country_map BYTEA,
                    country_description VARCHAR,
                    country_area INT,
                    country_language VARCHAR,
                    country_prev_election DATE,
                    country_next_election DATE
                )
            ''',
            '''
                CREATE TABLE indicatorDB (
                    indicator_id BIGINT,
                    indicator_api_code VARCHAR,
                    indicator_name VARCHAR,
                    indicator_description VARCHAR,
                    indicator_source VARCHAR,
                    indicator_topic VARCHAR,
                    country_id INTEGER REFERENCES countryDB(country_id),
                    year INT,
                    indicator_value DECIMAL
                )
            ''',
            '''
               CREATE TABLE aggregateDB (
                   aggregate_id SERIAL PRIMARY KEY,
                   aggregate_name VARCHAR,
                   aggregate_map BYTEA,
                   aggregate_description VARCHAR,
                   aggregate_area INT,
                   country_id INTEGER REFERENCES countryDB(country_id)
               )
            ''',
        ]
        for sql in commands:
            cur.execute(sql)
        cur.close()
        con.commit()

    except psycopg2.ProgrammingError as e:
        print(e)
    finally:
        if con is not None:
            con.close()


def truncate_table(table_name):
    con = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        sql = '''  truncate table {}  '''.format(table_name)
        cur.execute(sql)
        cur.close()
        con.commit()

    except psycopg2.ProgrammingError as e:
        print(e)
    finally:
        if con is not None:
            con.close()


def insert_table(table_name, list_data):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) as con:
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        for item in list_data:
            cur = con.cursor()
            column_name = str(tuple(item.keys()))
            value = tuple(item.values())

            # formatting quote for db values
            a = list(value)
            for idx, i in enumerate(a):
                if isinstance(i, str):
                    i = i.replace("'", "''")
                    a[idx] = i
            value = str(tuple(a))

            try:
                commands = [
                    '''
                        INSERT INTO {} {} VALUES {} ;
                    '''.format(table_name, column_name.replace('\'', ''), value.replace('"', '\'')),
                ]
                for sql in commands:
                    cur.execute(sql)
                cur.close()
                con.commit()

            except psycopg2.ProgrammingError as e:
                print(commands)
                print(e)

            except psycopg2.DataError as e:
                print(commands)
                print(e)

            except psycopg2.IntegrityError as e:
                if 'duplicate key value violates unique constraint' in str(e):
                    print(commands)
                    continue


def read_table(commands):
    con = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        cur.execute(commands)
        records = cur.fetchall()
        column_names = [row[0] for row in cur.description]
        datas = list()
        for record in records:
            zipp = zip(column_names, record)
            mapping = dict(map(list, zipp))
            datas.append(mapping)

    except psycopg2.ProgrammingError as e:
        print(e)
    finally:
        if con is not None:
            con.close()

    return datas


def drop_db():
    con = psycopg2.connect(dbname='postgres', user=DB_USER, password=DB_PASS, host=DB_HOST)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        sql = '''DROP database {} '''.format(DB_NAME)
        cur.execute(sql)
        cur.close()
        con.commit()
    except psycopg2.ProgrammingError as e:
        print(e)
    finally:
        if con is not None:
            con.close()


def retrievecountryfromsql(country=None, indicator=None, year=None, type_=None):
    for c in Country_table:
        for item in c:
            if country == item:
                characteristics = c

    country_id = country_translation(country)

    if indicator is None and year is None:
        print('{} characteristics: {}'.format(country, characteristics))

    if isinstance(indicator, str) and isinstance(year, int):
        commands = ''' 
            SELECT indicator_value FROM indicatorDB  
            WHERE country_id = {} AND
            indicator_id = {} AND
            year = {}
        '''.format(country_id, indicator, year)
        datas = read_table(commands=commands)
        return datas

    if isinstance(indicator, str) and isinstance(year, tuple):
        start = int(year[0])
        end = int(year[1])
        year_range = [i for i in range(start, end+1)]

        if type_ is None:
            commands = ''' 
                SELECT indicator_value FROM indicatorDB  
                WHERE country_id = {} AND
                indicator_id = {} AND (
            '''.format(country_id, indicator)
            for year in year_range:
                commands += 'year = {} OR '.format(year)

            commands = commands[:-3]+')'

        elif type_ == 'SUM':
            commands = ''' 
                        SELECT SUM(indicator_value) as sum_indicator_value FROM indicatorDB  
                        WHERE country_id = {} AND
                        indicator_id = {} AND (
                    '''.format(country_id, indicator)
            for year in year_range:
                commands += 'year = {} OR '.format(year)
            commands = commands[:-3] + ')'

        elif type_ == 'AVERAGE':
            commands = ''' 
                        SELECT AVG(indicator_value) as average_indicator_value FROM indicatorDB  
                        WHERE country_id = {} AND
                        indicator_id = {} AND (
                    '''.format(country_id, indicator)
            for year in year_range:
                commands += 'year = {} OR '.format(year)
            commands = commands[:-3] + ')'

        elif type_ == 'MAX':
            commands = ''' 
                        SELECT * FROM indicatorDB WHERE indicator_value IN 
                        (SELECT MAX(indicator_value) as max_indicator_value FROM indicatorDB  
                        WHERE country_id = {} AND
                        indicator_id = {} AND (
                    '''.format(country_id, indicator)
            for year in year_range:
                commands += 'year = {} OR '.format(year)
            commands = commands[:-3] + '))'

        elif type_ == 'MIN':
            commands = ''' 
                        SELECT * FROM indicatorDB WHERE indicator_value IN 
                        (SELECT MIN(indicator_value) as min_indicator_value FROM indicatorDB  
                        WHERE country_id = {} AND
                        indicator_id = {} AND (
                    '''.format(country_id, indicator)
            for year in year_range:
                commands += 'year = {} OR '.format(year)
            commands = commands[:-3] + '))'

        datas = read_table(commands=commands)
        return datas

    if indicator is None and isinstance(year, int):
        commands = ''' 
                    SELECT indicator_value FROM indicatorDB  
                    WHERE country_id = {} AND
                    year = {}
                '''.format(country_id, year)
        datas = read_table(commands=commands)
        return datas

    if indicator is None and isinstance(year, tuple):
        start = int(year[0])
        end = int(year[1])
        year_range = [i for i in range(start, end + 1)]
        commands = ''' 
                    SELECT indicator_value FROM indicatorDB  
                    WHERE country_id = {} AND (
                '''.format(country_id, indicator)
        for year in year_range:
            commands += 'year = {} OR '.format(year)
        commands = commands[:-3] + ')'

        datas = read_table(commands=commands)
        return datas


def delete_country(country_id):
    con = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        sql = '''delete from aggregatedb where country_id = {}'''.format(country_id)
        cur.execute(sql)
        sql = '''delete from indicatordb where country_id = {}'''.format(country_id)
        cur.execute(sql)
        sql = '''delete from countrydb where country_id = {}'''.format(country_id)
        cur.execute(sql)
        cur.close()
        con.commit()

        print('country deleted')

    except psycopg2.ProgrammingError as e:
        print(e)
    finally:
        if con is not None:
            con.close()


def retrieveaggregatefromsql(aggregate=list, indicators=None, year=None, type_=None):

    # if indicators = 1 and year = 1
    if isinstance(indicators, str) and isinstance(year, int):
        indicator_id, indicator_api_code, indicator_description, indicator_source, indicator_topic = indicator_translation(indicators)

        if type_ == 'SUM':
            commands = '''
                        SELECT SUM(indicator_value) as sum_indicator_value FROM indicatorDB
                        WHERE year = {} AND
                        indicator_id = {} AND (
                    '''.format(year, indicator_id)
            for c in aggregate:
                commands += 'country_id = {} OR '.format(c)
            commands = commands[:-3] + ')'
            datas = read_table(commands=commands)
            return datas

        elif type_ == 'AVERAGE':
            commands = '''
                        SELECT AVG(indicator_value) as average_indicator_value FROM indicatorDB
                        WHERE year = {} AND
                        indicator_id = {} AND (
                    '''.format(year, indicator_id)
            for c in aggregate:
                commands += 'country_id = {} OR '.format(c)
            commands = commands[:-3] + ')'
            datas = read_table(commands=commands)
            return datas

        elif type_ == 'MAX':
            commands = '''
                        SELECT * FROM indicatorDB WHERE indicator_value IN 
                        (SELECT MAX(indicator_value) as max_indicator_value FROM indicatorDB
                        WHERE year = {} AND
                        indicator_id = {} AND (
                    '''.format(year, indicator_id)
            for c in aggregate:
                commands += 'country_id = {} OR '.format(c)
            commands = commands[:-3] + '))'
            datas = read_table(commands=commands)
            return datas

        elif type_ == 'MIN':
            commands = '''
                        SELECT * FROM indicatorDB WHERE indicator_value IN 
                        (SELECT MIN(indicator_value) as min_indicator_value FROM indicatorDB
                        WHERE year = {} AND
                        indicator_id = {} AND (
                    '''.format(year, indicator_id)
            for c in aggregate:
                commands += 'country_id = {} OR '.format(c)
            commands = commands[:-3] + '))'
            datas = read_table(commands=commands)
            return datas

    if isinstance(indicators, str) and isinstance(year, tuple):
        indicator_id, indicator_api_code, indicator_description, indicator_source, indicator_topic = indicator_translation(indicators)

        if type_ == 'SUM':
            commands = '''
                        SELECT SUM(indicator_value) as sum_indicator_value FROM indicatorDB
                        WHERE indicator_id = {} AND (
                    '''.format(indicator_id)
            for c in aggregate:
                commands += 'country_id = {} OR '.format(c)
            commands = commands[:-3] + ')  AND ('

            start = int(year[0])
            end = int(year[1])
            year_range = [i for i in range(start, end + 1)]
            for y in year_range:
                commands += 'year = {} OR '.format(y)
            commands = commands[:-3] + ')'

            datas = read_table(commands=commands)
            return datas

        elif type_ == 'AVERAGE':
            commands = '''
                        SELECT AVG(indicator_value) as average_indicator_value FROM indicatorDB
                        WHERE indicator_id = {} AND (
                    '''.format(indicator_id)
            for c in aggregate:
                commands += 'country_id = {} OR '.format(c)
            commands = commands[:-3] + ')  AND ('

            start = int(year[0])
            end = int(year[1])
            year_range = [i for i in range(start, end + 1)]
            for y in year_range:
                commands += 'year = {} OR '.format(y)
            commands = commands[:-3] + ')'

            datas = read_table(commands=commands)
            return datas

        elif type_ == 'MAX':
            commands = '''
                        SELECT * FROM indicatorDB WHERE indicator_value IN 
                        (SELECT MAX(indicator_value) as max_indicator_value FROM indicatorDB
                        WHERE indicator_id = {} AND (
                    '''.format(indicator_id)
            for c in aggregate:
                commands += 'country_id = {} OR '.format(c)
            commands = commands[:-3] + ')  AND ('

            start = int(year[0])
            end = int(year[1])
            year_range = [i for i in range(start, end + 1)]
            for y in year_range:
                commands += 'year = {} OR '.format(y)
            commands = commands[:-3] + '))'

            datas = read_table(commands=commands)
            return datas

        elif type_ == 'MIN':
            commands = '''
                            SELECT * FROM indicatorDB WHERE indicator_value IN 
                            (SELECT MIN(indicator_value) as min_indicator_value FROM indicatorDB
                            WHERE indicator_id = {} AND (
                        '''.format(indicator_id)
            for c in aggregate:
                commands += 'country_id = {} OR '.format(c)
            commands = commands[:-3] + ')  AND ('

            start = int(year[0])
            end = int(year[1])
            year_range = [i for i in range(start, end + 1)]
            for y in year_range:
                commands += 'year = {} OR '.format(y)
            commands = commands[:-3] + '))'

            datas = read_table(commands=commands)
            return datas

def show_country_data():
    # sample indicator parameter
    indicator_name = 'Population ages 0-4, female (% of female population)' # SP.POP.0004.FE.5Y / 8011111710552
    indicator_id, indicator_api_code, indicator_description, indicator_source, indicator_topic = indicator_translation(indicator_name)

    # Retrieve for one country all the characteristics (in Country table)
    datas = retrievecountryfromsql(country='Angola', indicator=None, year=None)

    # Retrieve for one country for one indicator, the indicator_value (for a specific year)
    datas = retrievecountryfromsql(country='Angola', indicator=indicator_id, year=2010)

    # Retrieve for one country for one indicator, all the indicator_value (for a years range)
    datas = retrievecountryfromsql(country='Angola', indicator=indicator_id, year=(2010,2012))

    # Retrieve for one country for one indicator, the sum of all the indicator_value (for a years range)
    sum = retrievecountryfromsql(country='Angola', indicator=indicator_id, year=(2010, 2012), type_='SUM')[0]
    print('SUM (country: Angola, indicator: {}, year:(2010, 2012)) =  \n{} \n ==========================='.format(indicator_id, sum))

    # Retrieve for one country for one indicator, the average of all the indicator_value (for a years range)
    average = retrievecountryfromsql(country='Angola', indicator=indicator_id, year=(2010, 2012), type_='AVERAGE')[0]
    print('AVERAGE : (country: Angola, indicator: {}, year:(2010, 2012)) = \n{} \n ==========================='.format(indicator_id, average))

    # Retrieve for one country for one indicator, the max of all the indicator_value (for a years range)
    max = retrievecountryfromsql(country='Angola', indicator=indicator_id, year=(2010, 2012), type_='MAX')[0]
    print('MAX : (country: Angola, indicator: {}, year:(2010, 2012)) = \n{} \n ==========================='.format(indicator_id, max))

    # Retrieve for one country for one indicator, the min of all the indicator_value (for a years range)
    min = retrievecountryfromsql(country='Angola', indicator=indicator_id, year=(2010, 2012), type_='MIN')[0]
    print('MIN : (country: Angola, indicator: {}, year:(2010, 2012)) = \n{} \n ==========================='.format(indicator_id, min))

    # Retrieve for one country for all indicators, all the indicator_value (for a specific year)
    datas = retrievecountryfromsql(country='Angola', year=2010)

    # Retrieve for one country for all indicators, all the indicator_value (for a years range)
    datas = retrievecountryfromsql(country='Angola', year=(2010, 2012))

    # example result indicator_name (Population ages 0-4, female (% of female population) country 'Angola'
    example_indicator = Indicator(
        name=indicator_name,
        identifier=indicator_id,
        code=indicator_api_code,
        source=indicator_source,
        max={'year': max['year'], 'value':max['indicator_value']},
        min={'year': min['year'], 'value':min['indicator_value']},
        average=average['average_indicator_value'],
        sum=sum['sum_indicator_value']
    )
    print('EXAMPLE AVERAGE WITH CLASS: ')
    print(example_indicator.average)
    print('===========================================')


def show_aggregate_data():
    indicators = ['Population ages 0-4, female (% of female population)', 'Population ages 0-14, female']

    coutries = get_countries_from_aggregate('Africa')
    coutries_id = []
    for c in coutries:
        coutries_id.append(c['country_id'])

    # 'For an aggregate, and for one indicator, retrieve the sum of all the indicator_value (for a specific year)'
    print('For an aggregate, and for one indicator, retrieve the sum of all the indicator_value (for a specific year)')
    sum = retrieveaggregatefromsql(aggregate=coutries_id, indicators=indicators[0], year=2010, type_='SUM')
    print(sum)
    print('===========================================')

    # For an aggregate, and for one indicator, retrieve the sum of all the indicator_value (for a years range)
    print('For an aggregate, and for one indicator, retrieve the sum of all the indicator_value (for a years range)')
    sum = retrieveaggregatefromsql(aggregate=coutries_id, indicators=indicators[0], year=(2010, 2012), type_='SUM')
    print(sum)
    print('===========================================')

    # 'For an aggregate, and for one indicator, retrieve the sum of all the indicator_value (for a specific year)'
    print(
        'For an aggregate, and for one indicator, retrieve the average of all the indicator_value (for a specific year)')
    avg = retrieveaggregatefromsql(aggregate=coutries_id, indicators=indicators[0], year=2010, type_='AVERAGE')
    print(avg)
    print('===========================================')

    # For an aggregate, and for one indicator, retrieve the sum of all the indicator_value (for a years range)
    print(
        'For an aggregate, and for one indicator, retrieve the average of all the indicator_value (for a years range)')
    avg = retrieveaggregatefromsql(aggregate=coutries_id, indicators=indicators[0], year=(2010, 2012), type_='AVERAGE')
    print(avg)
    print('===========================================')

    # 'For an aggregate, and for one indicator, retrieve the maximum value of all the indicator_value and return the country that has the maximum of all the indicator_value (for a specific year) '
    print(
        'For an aggregate, and for one indicator, retrieve the maximum value of all the indicator_value and return the country that has the maximum of all the indicator_value (for a specific year) ')
    max = retrieveaggregatefromsql(aggregate=coutries_id, indicators=indicators[0], year=2010, type_='MAX')
    print(max)
    print('===========================================')

    # For an aggregate, and for one indicator, retrieve the maximum value of all the indicator_value and return the country that has the maximum of all the indicator_value (for a specific year)
    print(
        'For an aggregate, and for one indicator, retrieve the maximum value of all the indicator_value and return the country that has the maximum of all the indicator_value (for a years range) ')
    max = retrieveaggregatefromsql(aggregate=coutries_id, indicators=indicators[0], year=(2010, 2012), type_='MAX')
    print(max)
    print('===========================================')

    # 'For an aggregate, and for one indicator, retrieve the maximum value of all the indicator_value and return the country that has the maximum of all the indicator_value (for a specific year) '
    print(
        'For an aggregate, and for one indicator, retrieve the minimum value of all the indicator_value and return the country that has the maximum of all the indicator_value (for a specific year) ')
    min = retrieveaggregatefromsql(aggregate=coutries_id, indicators=indicators[0], year=2010, type_='MIN')
    print(min)
    print('===========================================')

    # For an aggregate, and for one indicator, retrieve the maximum value of all the indicator_value and return the country that has the maximum of all the indicator_value (for a specific year)
    print(
        'For an aggregate, and for one indicator, retrieve the minimum value of all the indicator_value and return the country that has the minimum of all the indicator_value (for a years range) ')
    min = retrieveaggregatefromsql(aggregate=coutries_id, indicators=indicators[0], year=(2010, 2012), type_='MIN')
    print(min)
    print('===========================================')


def country_id_in_aggregate_checker(country_id):
    commands = ''' 
                SELECT * FROM aggregateDB  
                WHERE country_id = {}
            '''.format(country_id)

    datas = read_table(commands=commands)
    return datas


def add_aggregate(data=dict()):
    country_id_list = [item['country_id'] for item in country_id_in_aggregate_checker(data['country_id'])]
    if data['country_id'] not in country_id_list:
        insert_table('aggregateDB', [data])
        print('country in aggregatedb added')
    else:
        print('country in aggregatedb already exists')


def get_countries_from_aggregate(name):
    commands = ''' 
                    SELECT country_id FROM aggregateDB  
                    WHERE aggregate_name = '{}'
                '''.format(name)

    datas = read_table(commands=commands)
    return datas


if __name__ == '__main__':
    answer = input('Input type: \n'
                   'Y: Create the database and populate data from wbdata,\n'
                   'N: Delete database,\n'
                   'SC: Show country data from indicatorsdb,\n'
                   'AA: Add aggregate to aggregatedb \n'
                   'SA: Show country data by aggregate (make sure you have run AA) \n'
                   'AC: Add country to an aggregatedb \n'
                   'DC: Delete country from an aggregatedb \n'
                   'Input: ')

    # Create database, table and retrieve data from wbdata
    if answer == 'Y':
        create_db()
        create_table()
        init_dataset()
        retrieve_external_data()

    # Drop table
    elif answer == 'N':
        drop_db()

    # Show country data
    elif answer == 'SC':
        init_dataset()
        show_country_data()

    # Add Aggregate
    elif answer == 'AA':
        init_dataset()

        # insert manual aggregate
        africa = Aggregate(name='Africa',
                           identifier='AFR',
                           iso='AF')

        # Add country to Aggregate.add_country
        africa.add_country('Angola')
        africa.add_country('Burundi')

        for country in africa.countries:
            data = {
                'aggregate_name': africa.name,
                'aggregate_map': '',
                'aggregate_description': 'Africa Aggregate',
                'aggregate_area': 1,
                'country_id': country_translation(country)
            }
            add_aggregate(data)


    elif answer == 'SA':
        init_dataset()
        show_aggregate_data()


    elif answer == 'AC':
        init_dataset()
        new_country = ['BEN', 'BJ', 'Benin', 'Porto-Novo']

        # insert to table countrydb
        country_dict = dict()  # country_dict must this format: {'country_id': '', 'country_name': '', 'country_ISOid': ''}
        country_dict['country_id'] = len(country_list) + 1
        country_dict['country_name'] = new_country[2]
        country_dict['country_ISOid'] = new_country[0]
        country_list.append(country_dict)

        # getting new data from wbdata
        Country_table.append(new_country)
        retrieve_external_data()

        # add country to aggregatedb
        data = {
            'aggregate_name': 'Africa',
            'aggregate_map': '',
            'aggregate_description': 'Africa Aggregate',
            'aggregate_area': 1,
            'country_id': country_translation(new_country[2])
        }
        add_aggregate(data)

    elif answer == 'DC':
        delete_country(49)

    else:
        sys.exit()
