from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)

# Replace 'your_secret_token' with the secret token you configured on GitHub
SECRET_TOKEN = 'your_secret_token'

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    # Verify the request signature
    signature = request.headers.get('X-Hub-Signature')
    if signature is None:
        abort(400, 'Missing X-Hub-Signature header')

    # Compute the HMAC hex digest
    sha_name, signature = signature.split('=')
    if sha_name != 'sha1':
        abort(501, 'Not implemented: signature algorithm not supported')

    mac = hmac.new(SECRET_TOKEN.encode(), msg=request.data, digestmod=hashlib.sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403, 'Invalid signature')

    # Process the GitHub event
    payload = request.json
    if payload['ref'] == 'refs/heads/master':
        # Implement your logic here for handling the push event
        print('Received push to master branch')

    return '', 204

if __name__ == '__main__':
    app.run(debug=True)