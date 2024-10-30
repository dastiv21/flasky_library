from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from

app = Flask(__name__)
swagger = Swagger(app)

GITHUB_SECRET_TOKEN = 'your_secret_token_here'


@app.route('/webhook', methods=['POST'])
@swag_from('docs/webhook.yml')  # Use the Swagger YAML file for documentation
def handle_github_webhook():
    # Verify the request using the secret token
    signature = request.headers.get('X-Hub-Signature')
    sha, signature = signature.split('=')
    mac = hmac.new(GITHUB_SECRET_TOKEN.encode(), msg=request.data,
                   digestmod=hashlib.sha1)

    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403)

    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        # Handle the push event
        print("Received a push event")
        # Your logic to handle the push event goes here
        # After handling the event, update the Swagger documentation
        app.config['SWAGGER'] = {"update": True}

    return jsonify({"status": "done"}), 200


if __name__ == '__main__':
    app.run(debug=True)