from extensions import (
    app,
    os
)

from app.controller.service_controller import api
import logging

logging.basicConfig(level=logging.DEBUG)

app.logger.setLevel(logging.INFO)


# register the api
app.register_blueprint(api)

if __name__ == '__main__':
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    app.run('localhost', 8080, debug=True)