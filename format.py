from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)

# The secret token you get from your GitHub webhook settings
GITHUB_SECRET_TOKEN = 'your_secret_token_here'


@app.route('/webhook', methods=['POST'])
def handle_github_webhook():
    # Verify the request using the secret token
    signature = request.headers.get('X-Hub-Signature')
    sha, signature = signature.split('=')
    mac = hmac.new(GITHUB_SECRET_TOKEN.encode(), msg=request.data,
                   digestmod=hashlib.sha1)

    # Abort if the signature doesn't match
    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403)

    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        # Handle the push event
        print("Received a push event")
        # Your logic to handle the push event goes here

    return '', 200


if __name__ == '__main__':
    app.run(debug=True)