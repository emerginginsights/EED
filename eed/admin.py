"""FlaskAdmin admin panel"""
import multiprocessing
import os

from flask import request
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib import sqla
from flask_basicauth import BasicAuth
from werkzeug import Response
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect

from eed.models import Country, Indicator, Aggregate
from wbscript.run import retrieve_external_data, init_dataset

basic_auth = BasicAuth()


def setup_admin(app, db_conn):
    """setup admin panel to flask app"""
    if os.getenv('EED_ADMIN_USER', None):
        app.config['BASIC_AUTH_USERNAME'] = os.getenv('EED_ADMIN_USER')
    if os.getenv('EED_ADMIN_PASS', None):
        app.config['BASIC_AUTH_PASSWORD'] = os.getenv('EED_ADMIN_PASS')

    basic_auth.init_app(app)
    # set optional bootswatch theme
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin = Admin(app, name='eed', template_mode='bootstrap3')
    admin.add_view(ModelViewWithAuth(Country, db_conn.session))
    admin.add_view(IndicatorModelView(Indicator, db_conn.session))
    admin.add_view(AggregateModelView(Aggregate, db_conn.session))

    admin.add_view(RunWBScriptView(name='Load data from WorldBank', endpoint='wbscript'))


class AuthException(HTTPException):
    """Authentication exception"""
    def __init__(self, message):
        super().__init__(message, Response(
            "You could not be authenticated. Please refresh the page.", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


class ModelViewWithAuth(sqla.ModelView):
    """ModelView wrapped with auth"""
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class IndicatorModelView(ModelViewWithAuth):
    """ModelView for Indicator"""
    page_size = 100
    column_list = ('indicator_id', 'indicator_api_code', 'country', 'year',
                   'indicator_value', 'indicator_name',
                   'indicator_description', 'indicator_source', 'indicator_topic')
    column_searchable_list = ('indicator_id', 'country.country_name', 'year')
    column_filters = ('country.country_name', 'year')


class AggregateModelView(ModelViewWithAuth):
    """ModelView for Aggregate"""
    page_size = 100
    column_list = ('aggregate_id', 'aggregate_name', 'aggregate_description',
                   'aggregate_area', 'country')
    column_filters = ('country.country_name',)
    column_searchable_list = ('aggregate_name', 'country.country_name', 'aggregate_description')


class RunWBScriptView(BaseView):
    """View for running wbscript process"""
    wbscript_process = None

    @expose('/')
    def index(self):
        """World Bank Load data index page"""
        if RunWBScriptView.is_wbscript_running():
            return self.render('admin_wbscript.html', started=True)
        return self.render('admin_wbscript.html')

    @expose('/run_wbscript')
    def run(self):
        """Route to run wbscript"""
        if RunWBScriptView.is_wbscript_running():
            return self.render('admin_wbscript.html', started=True)

        start_year = int(request.args.get('start', '2010'))
        end_year = int(request.args.get('end', '2020'))
        RunWBScriptView.wbscript_process = multiprocessing.Process(
            target=self.run_wbscript,
            args=(start_year, end_year))
        RunWBScriptView.wbscript_process.start()
        return self.render('admin_wbscript.html', started=True)

    @staticmethod
    def is_wbscript_running():
        """Checks if the script is running"""
        return (RunWBScriptView.wbscript_process
                and RunWBScriptView.wbscript_process.is_alive())

    @staticmethod
    def run_wbscript(start_year, end_year):
        """Run wbscript"""
        print("RunWBScript")
        init_dataset()
        retrieve_external_data(start_year=start_year, end_year=end_year)
