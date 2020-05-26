import decimal
import json
from collections import defaultdict

from flask import Blueprint, request, jsonify

from .models import Country, Indicator

stats_api_bp = Blueprint("country_stats", __name__, url_prefix='/api')


@stats_api_bp.route('/country_stats')
def country_stats():
    country_query = request.args.get('country')
    country = Country.query.filter(Country.country_name == country_query)\
        .first_or_404(description='Country "{}" not found'.format(country_query))
    res_dict = {
        'country_name': country.country_name,
        'country_id': country.country_id,
        'language': country.country_language,
        'description' : country.country_description,
        'iso_id': country.country_isoid,
        'prev_election': country.country_prev_election,
        'next_election': country.country_next_election,
    }

    indicators = Indicator.query.filter(Indicator.country_id == country.country_id).all()
    indicators_dict = defaultdict(dict)
    for ind in indicators:
        indicators_dict[ind.indicator_id][ind.year] = str(ind.indicator_value)
    res_dict['indicator_values'] = indicators_dict

    return res_dict


@stats_api_bp.route('/indicators')
def indicators_list():
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
