from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)

# Your GitHub webhook secret
GITHUB_SECRET = b'your_secret_here'

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    # Verify the request signature
    signature = request.headers.get('X-Hub-Signature')
    sha_name, signature = signature.split('=')
    if sha_name != 'sha1':
        abort(400, 'Invalid header signature')
    mac = hmac.new(GITHUB_SECRET, msg=request.data, digestmod=hashlib.sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(400, 'Invalid signature')

    # Process the GitHub event
    event = request.headers.get('X-GitHub-Event', 'ping')
    if event == 'push':
        # Handle push event
        print("Push event received")
        # Add your logic here
    else:
        print(f"Unhandled event: {event}")

    return '', 204

if __name__ == '__main__':
    app.run(debug=True)