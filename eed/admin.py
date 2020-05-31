import os

from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_basicauth import BasicAuth
from werkzeug import Response
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect

from eed.models import Country, Indicator, Aggregate

basic_auth = BasicAuth()


def setup_admin(app, db):
    if os.getenv('EED_ADMIN_USER', None):
        app.config['BASIC_AUTH_USERNAME'] = os.getenv('EED_ADMIN_USER')
    if os.getenv('EED_ADMIN_PASS', None):
        app.config['BASIC_AUTH_PASSWORD'] = os.getenv('EED_ADMIN_PASS')

    basic_auth.init_app(app)
    # set optional bootswatch theme
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin = Admin(app, name='eed', template_mode='bootstrap3')
    admin.add_view(ModelViewWithAuth(Country, db.session))
    admin.add_view(IndicatorModelView(Indicator, db.session))
    admin.add_view(AggregateModelView(Aggregate, db.session))


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            "You could not be authenticated. Please refresh the page.", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


class ModelViewWithAuth(sqla.ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class IndicatorModelView(ModelViewWithAuth):
    page_size = 100
    column_list = ('indicator_id', 'indicator_api_code', 'country', 'year',
                   'indicator_value', 'indicator_name',
                   'indicator_description', 'indicator_source', 'indicator_topic')
    column_searchable_list = ('indicator_id', 'country.country_name', 'year')
    column_filters = ('country.country_name', 'year')


class AggregateModelView(ModelViewWithAuth):
    page_size = 100
    column_list = ('aggregate_id', 'aggregate_name', 'aggregate_description',
                   'aggregate_area', 'country')
    column_filters = ('country.country_name',)
    column_searchable_list = ('aggregate_name', 'country.country_name', 'aggregate_description')
