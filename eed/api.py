"""API endpoints for countries and stats"""
from collections import defaultdict

from flask import Blueprint, request
from sqlalchemy import or_

from eed.models import Country, Indicator

stats_api_bp = Blueprint("country_stats", __name__, url_prefix='/api')


@stats_api_bp.route('/indicators')
def indicators_list():
    """All indicators list"""
    indicators = Indicator.query.distinct(Indicator.indicator_id).all()
    indicators_details = {}
    for ind in indicators:
        indicators_details[ind.indicator_id] = {
            'api_code': ind.indicator_api_code,
            'name': ind.indicator_name,
            'description': ind.indicator_description,
            'source': ind.indicator_source,
            'topics': ind.indicator_topic,
        }
    return indicators_details


@stats_api_bp.route('/countries/')
def countries():
    """All countries list"""
    res_countries = Country.query.all()
    return {'countries': [c.res_dict() for c in res_countries]}


@stats_api_bp.route('/countries/<country_id_or_name>')
def country(country_id_or_name):
    """Country by ID or Name or ISOCode"""
    country_res = get_country_by_id_or_name(country_id_or_name)
    return country_res.res_dict()


@stats_api_bp.route('/countries/<country_id_or_name>/stats')
def country_stats(country_id_or_name):
    """stats for a country

    indicator_ids - get parameter to specify list of indicators
    (if not specified - all indicators)"""
    country_res = get_country_by_id_or_name(country_id_or_name)
    res_dict = country_res.res_dict()

    indicators_query = Indicator.query.filter(Indicator.country_id == country_res.country_id)
    indicator_ids = request.args.get('indicator_ids')
    if indicator_ids:
        ids_lst = indicator_ids.split(',')
        indicators_query = indicators_query.filter(Indicator.indicator_id.in_(ids_lst))
    indicators = indicators_query.all()
    indicators_dict = defaultdict(dict)
    for ind in indicators:
        indicators_dict[ind.indicator_id][ind.year] = str(ind.indicator_value)
    res_dict['indicator_values'] = indicators_dict

    return res_dict


def get_country_by_id_or_name(country_id_or_name):
    """helper function to get country by id or name or iso code"""
    try:
        country_id = int(country_id_or_name)
        country_query = Country.query.filter(Country.country_id == country_id)
    except ValueError:
        country_query = Country.query.filter(or_(Country.country_name == country_id_or_name,
                                                 Country.country_isoid == country_id_or_name))
    return country_query.first_or_404(
        description='Country "{}" not found'.format(country_id_or_name))
