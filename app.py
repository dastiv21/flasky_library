from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
api = Api(app)

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Library Management API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# In-memory data for books and borrowed books
books = {}
borrowed_books = {}

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
@app.route('/swagger.json')
def swagger_json():
    """
    Swagger API Documentation.
    """
    swagger_docs = {
        "swagger": "2.0",
        "info": {
            "title": "Library Management API",
            "description": "API for managing books, borrowing, and returning",
            "version": "1.0"
        },
        "basePath": "/",
        "paths": {
            "/books": {
                "get": {
                    "summary": "Retrieve all books",
                    "responses": {
                        "200": {"description": "A list of all books"}
                    }
                },
                "post": {
                    "summary": "Add a new book",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "book",
                            "description": "Book to add",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "author": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {"description": "Book added successfully"}
                    }
                }
            },
            "/books/{book_id}": {
                "get": {
                    "summary": "Retrieve a specific book by ID",
                    "parameters": [
                        {"name": "book_id", "in": "path", "type": "string"}
                    ],
                    "responses": {
                        "200": {"description": "Book details"},
                        "404": {"description": "Book not found"}
                    }
                }
            },
            "/borrow": {
                "post": {
                    "summary": "Borrow a book",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "borrow",
                            "description": "Book to borrow",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "book_id": {"type": "string"},
                                    "user": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {"description": "Book borrowed successfully"},
                        "400": {"description": "Book already borrowed"},
                        "404": {"description": "Book not found"}
                    }
                }
            },
            "/return": {
                "post": {
                    "summary": "Return a borrowed book",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "return",
                            "description": "Book to return",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "book_id": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {"description": "Book returned successfully"},
                        "404": {"description": "Book not borrowed"}
                    }
                }
            }
        }
    }
    return jsonify(swagger_docs)

if __name__ == "__main__":
    app.run(debug=True)
