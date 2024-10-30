from flask import Flask, jsonify, request, abort
from flask_restful import Api, Resource
import hmac
import hashlib
from flasgger import Swagger, swag_from

app = Flask(__name__)
swagger = Swagger(app)

api = Api(app)

# In-memory data for books and borrowed books
books = {}
borrowed_books = {}
SECRET_TOKEN = 'ye993our_s123ecre747489t_to948949ken'


@app.route('/webhook/github', methods=['POST'])
@swag_from('docs/webhook.yml')
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
        app.config['SWAGGER'] = {"update": True}

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

if __name__ == "__main__":
    app.run(debug=True)


