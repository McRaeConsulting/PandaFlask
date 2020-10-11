from flask import Flask, jsonify, render_template, url_for, send_from_directory


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from . import graphs
    app.register_blueprint(graphs.graphs_page)

    @app.route('/')
    def index():
        items = [{'url': url_for('graphs_page.show', graph='weekly_figures'),
                  'text': 'Weekly Figures 2020'},
                 # {'url': url_for('graphs_page.show', graph='covid_registrations'),
                 #  'text': 'Daily COVID-19 Registrations'},
                 # {'url': url_for('graphs_page.show', graph='covid_occurrences'),
                 #  'text': 'Daily COVID-19 Occurrences'},
                 ]
        return render_template('index.html', items=items)

    @app.route('/home')
    def home():
        return index()

    @app.route('/static/<path:filename>')
    def staticfiles(filename):
        return send_from_directory(app.config["STATIC_FOLDER"], filename)

    @app.route('/hello')
    def hello_world():
        return jsonify("Hello world! I'm here for a reason")

    return app
