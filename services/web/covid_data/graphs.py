from flask import Blueprint, render_template, abort, request, url_for
from jinja2 import TemplateNotFound
from .models import WeeklyFiguresModel

graphs_page = Blueprint('graphs_page', __name__, template_folder='templates', url_prefix='/graphs')


@graphs_page.route('/graphs', defaults={'graph': 'index'})
@graphs_page.route('/<graph>')
def show(graph):
    items = list()
    if graph == 'weekly_figures':
        items.append({
            'url': url_for('graphs_page.show', graph='weekly_figures'),
            'text': 'Totals to Date',
        })
        dates = WeeklyFiguresModel().get_valid_date_series()
        for date in dates:
            items.append({
                'url': url_for('graphs_page.all_deaths_by_age_at_current_week_json', week=date),
                'text': date.strftime("%Y-%m-%d"),
                'args': 'ajax'
            })
    else:
        abort(404)
    return render_template('graphs/%s.html' % graph, items=items)


@graphs_page.route('/total_deaths_json')
def total_deaths_json():
    return WeeklyFiguresModel().total_deaths_averages_json()


@graphs_page.route('/all_deaths_by_age_at_current_week_json')
def all_deaths_by_age_at_current_week_json():
    return WeeklyFiguresModel().total_deaths_by_age_at_week_json(week=WeeklyFiguresModel().latest_week)


@graphs_page.route('/all_deaths_by_age_at_week_json')
def total_deaths_by_age_at_week_json(week):
    return WeeklyFiguresModel().total_deaths_by_age_at_week_json(week=week)


@graphs_page.route('/total_deaths_by_region_at_current_week_json')
def total_deaths_by_region_at_current_week_json():
    return WeeklyFiguresModel().total_deaths_by_region_at_date_json()


@graphs_page.route('/deaths_by_region_on_date_json')
def deaths_by_region_on_date_json():
    date = request.args.get('date')
    return WeeklyFiguresModel().deaths_by_region_on_date_json(date=date)


@graphs_page.route('/total_deaths_by_age_and_sex')
def total_deaths_by_age_and_sex():
    date = request.args.get('date')
    return WeeklyFiguresModel().total_deaths_by_age_and_sex_at_date_json(date=date)


@graphs_page.route('/graphs_for_date')
def graphs_for_date():
    date = request.args.get('date')
    return date if date is not None else "Not defined"


@graphs_page.route('/covid_registrations')
def covid_registrations():
    date = request.args.get('date')
    return date if date is not None else "Not defined"


@graphs_page.route('/covid_occurrences')
def covid_occurrences():
    date = request.args.get('date')
    return date if date is not None else "Not defined"
