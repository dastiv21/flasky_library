from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)
api = Api(app)

login_model = api.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')
        # Authenticate user...
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        return {'message': 'This is a protected endpoint'}

if __name__ == '__main__':
    app.run(debug=True)