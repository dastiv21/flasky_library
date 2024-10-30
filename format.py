from flask import Flask, request, abort, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import os

app = Flask(__name__)

# Swagger configuration
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (make sure it's a trailing slash)
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "MyAPI"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/webhook', methods=['POST'])
def handle_github_webhook():
    # Verify the request using the secret token
    # ... (same as before)

    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        # Handle the push event
        print("Received a push event")
        # Your logic to handle the push event goes here

        # Regenerate the Swagger documentation
        swagger_json = generate_swagger_json()
        cache.set('swagger_json', swagger_json)

    return '', 200


def generate_swagger_json():
    # Logic to generate the Swagger/OpenAPI JSON
    # This can be done by parsing your code annotations or any other way you define your API
    # For this example, let's assume it's a static JSON file
    with open('static/swagger.json', 'r') as f:
        return f.read()


@app.route('/swagger.json')
def swagger_json():
    # Endpoint to serve the Swagger JSON
    # This will serve the latest cached version
    cached_swagger_json = cache.get('swagger_json')
    if cached_swagger_json is None:
        # If the cache is empty, regenerate and cache the Swagger JSON
        swagger_json = generate_swagger_json()
        cache.set('swagger_json', swagger_json)
        return jsonify(swagger_json)
    return jsonify(cached_swagger_json)


if __name__ == '__main__':
    app.run(debug=True)