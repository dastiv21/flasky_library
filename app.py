from flask import Flask, jsonify, request, abort
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import hmac
import hashlib
import subprocess

app = Flask(__name__)
api = Api(app)

# Swagger UI setup
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (make sure it's a trailing slash)
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "MyAPI"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# In-memory data for books and borrowed books
books = {}
borrowed_books = {}
SECRET_TOKEN = 'ye993our_s123ecre747489t_to948949ken'


@app.route('/webhook/github', methods=['POST'])
def handle_github_webhook():
    # Verify the request using the secret token
    signature = request.headers.get('X-Hub-Signature')
    sha, signature = signature.split('=')
    mac = hmac.new(SECRET_TOKEN.encode(), msg=request.data,
                   digestmod=hashlib.sha1)

    # Abort if the signature doesn't match
    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403)

    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        # Handle the push event
        print("Received a push event")
        # Update Swagger documentation
        update_swagger_docs()

    return '', 200


class Book(Resource):
    def get(self, book_id=None):
        """
        Get book details.
        If no book_id is provided, returns all books.

        :param book_id: ID of the book to retrieve (optional)
        :return: Book details or list of all books
        """
        if book_id:
            book = books.get(book_id)
            if book:
                return jsonify(book)
            return jsonify({"message": "Book not found"}), 404
        return jsonify(list(books.values()))

    def post(self):
        """
        Add a new book.

        :return: Message indicating success or failure
        """
        book = request.get_json()
        book_id = book.get("id")
        if book_id in books:
            return jsonify({"message": "Book already exists"}), 400
        books[book_id] = book
        return jsonify({"message": "Book added successfully"})

class Borrow(Resource):
    def post(self):
        """
        Borrow a book by book ID.

        :return: Message indicating success or failure
        """
        data = request.get_json()
        book_id = data.get("book_id")
        user = data.get("user")
        if book_id not in books:
            return jsonify({"message": "Book not available"}), 404
        if book_id in borrowed_books:
            return jsonify({"message": "Book already borrowed"}), 400
        borrowed_books[book_id] = user
        return jsonify({"message": "Book borrowed successfully"})

class ReturnBook(Resource):
    def post(self):
        """
        Return a book by book ID.

        :return: Message indicating success or failure
        """
        data = request.get_json()
        book_id = data.get("book_id")
        if book_id not in borrowed_books:
            return jsonify({"message": "Book not borrowed"}), 404
        borrowed_books.pop(book_id)
        return jsonify({"message": "Book returned successfully"})

# Route setup
api.add_resource(Book, "/books", "/books/<string:book_id>")
api.add_resource(Borrow, "/borrow")
api.add_resource(ReturnBook, "/return")

# Swagger JSON
# @app.route('/swagger.json')
# def swagger_json():
#     """
#     Swagger API Documentation.
#     """
#     swagger_docs = {
#         "swagger": "2.0",
#         "info": {
#             "title": "Library Management API",
#             "description": "API for managing books, borrowing, and returning",
#             "version": "1.0"
#         },
#         "basePath": "/",
#         "paths": {
#             "/books": {
#                 "get": {
#                     "summary": "Retrieve all books",
#                     "responses": {
#                         "200": {"description": "A list of all books"}
#                     }
#                 },
#                 "post": {
#                     "summary": "Add a new book",
#                     "parameters": [
#                         {
#                             "in": "body",
#                             "name": "book",
#                             "description": "Book to add",
#                             "schema": {
#                                 "type": "object",
#                                 "properties": {
#                                     "id": {"type": "string"},
#                                     "title": {"type": "string"},
#                                     "author": {"type": "string"}
#                                 }
#                             }
#                         }
#                     ],
#                     "responses": {
#                         "200": {"description": "Book added successfully"}
#                     }
#                 }
#             },
#             "/books/{book_id}": {
#                 "get": {
#                     "summary": "Retrieve a specific book by ID",
#                     "parameters": [
#                         {"name": "book_id", "in": "path", "type": "string"}
#                     ],
#                     "responses": {
#                         "200": {"description": "Book details"},
#                         "404": {"description": "Book not found"}
#                     }
#                 }
#             },
#             "/borrow": {
#                 "post": {
#                     "summary": "Borrow a book",
#                     "parameters": [
#                         {
#                             "in": "body",
#                             "name": "borrow",
#                             "description": "Book to borrow",
#                             "schema": {
#                                 "type": "object",
#                                 "properties": {
#                                     "book_id": {"type": "string"},
#                                     "user": {"type": "string"}
#                                 }
#                             }
#                         }
#                     ],
#                     "responses": {
#                         "200": {"description": "Book borrowed successfully"},
#                         "400": {"description": "Book already borrowed"},
#                         "404": {"description": "Book not found"}
#                     }
#                 }
#             },
#             "/return": {
#                 "post": {
#                     "summary": "Return a borrowed book",
#                     "parameters": [
#                         {
#                             "in": "body",
#                             "name": "return",
#                             "description": "Book to return",
#                             "schema": {
#                                 "type": "object",
#                                 "properties": {
#                                     "book_id": {"type": "string"}
#                                 }
#                             }
#                         }
#                     ],
#                     "responses": {
#                         "200": {"description": "Book returned successfully"},
#                         "404": {"description": "Book not borrowed"}
#                     }
#                 }
#             }
#         }
#     }
#     return jsonify(swagger_docs)


def update_swagger_docs():
    # Assuming you have a script to generate the swagger.json
    # For example, you might use a tool like flasgger or swagger-codegen
    # Here is a placeholder for the command you would run
    command = "generate-swagger-docs"  # Replace with your actual command
    result = subprocess.run(command, shell=True, check=True)
    if result.returncode == 0:
        print("API documentation updated successfully.")
    else:
        print("Failed to update API documentation.")

if __name__ == "__main__":
    app.run(debug=True)


