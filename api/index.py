from api.app import create_app
from apig_wsgi import make_lambda_handler

app = create_app()

handler = make_lambda_handler(app)
