from .links import links_bp


def register_routes(app):
    app.register_blueprint(links_bp)
