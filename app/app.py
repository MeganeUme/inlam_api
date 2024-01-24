from flask import Flask, request, jsonify, current_app, g, abort
from app.database import get_db_connection, close_db_connection
from app.decorator import log_request_body

import asyncio
from app.author_api import get_author_info

from app.error_response import error_response

app = Flask(__name__)

app.config["DATABASE"] = "Books.db"



@app.route("/")
def home():
    """
    Home endpoint. Returns a simple greeting message.
    """
    return "Hello world"


@app.route("/books", methods=["GET"])
def get_books():
    """
    GET endpoint to retrieve all books from the database. 
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
                        SELECT books.*, CAST(avg(reviews.review_score) AS REAL) as average_score
                        FROM books
                        LEFT JOIN reviews ON books.book_id = reviews.book_id
                        GROUP BY books.book_id, books.title
                    """)
        data = cursor.fetchall()
        
        books_list = []
        for row in data:
            book = {
                "book_id": row["book_id"],
                "title": row["title"],
                "author": row["author"],
                "summary": row["summary"],
                "genre": row["genre"],
                "average_score": float(row["average_score"])
            }
            books_list.append(book)
        
        return jsonify(books=books_list), 200
    except Exception as e:
        return error_response(f"Failed to fetch books. Readon: {str(e)}", 500)


@app.route("/books", methods=["POST"])
@log_request_body
def add_books():
    """
    POST endpoint to add one or more books to the database.
    Requires a JSON payload with at least 'title' and 'author' fields.
    """
    if request.method == "POST":
        data = request.json

        # Validate the required fields and data types
        if not all(field in data for field in ['title', 'author']):
            return error_response("Title and Author are required", 400)

        title = data["title"]
        author = data["author"]
        summary = data.get("summary", "")
        genre = data.get("genre", "")

        # Insert the data into the database
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO books (title, author, summary, genre) VALUES (?, ?, ?, ?)",
                (title, author, summary, genre)
            )
            connection.commit()
            return jsonify({"message": "Book added successfully"}), 201
        except Exception as e:
            connection.rollback()
            return error_response(f"Failed to add book. Reason: {str(e)}", 500)


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book_id(book_id):
    """
    GET endpoint to retrieve information about a specific book by its ID.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
                        SELECT books.*, CAST(avg(reviews.review_score) AS REAL) as average_score
                        FROM books
                        LEFT JOIN reviews ON books.book_id = reviews.book_id
                        WHERE books.book_id = ?
                        GROUP BY books.book_id, books.title
                    """, (book_id,))

        data = cursor.fetchone()

        if data:
            book = {
                "book_id": data["book_id"],
                "title": data["title"],
                "author": data["author"],
                "summary": data["summary"],
                "genre": data["genre"],
                "average_score": data["average_score"] if data["average_score"] is not None else None
            }
            return jsonify(book), 200
        else:
            return error_response(f"Book with ID {book_id} not found", 404)

    except Exception as e:
        return error_response(f"Failed to fetch book. Reason: {str(e)}", 500)



@app.route("/books/<int:book_id>", methods=["PUT"])
@log_request_body
def update_book(book_id):
    """
    PUT endpoint to update information about a specific book by its ID.
    """
    if request.method == "PUT":
        data = request.json

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Check if the book with the specified ID exists
            cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
            existing_book = cursor.fetchone()

            if existing_book is None:
                # Return a 404 Not Found status code
                return jsonify({"error": "Not Found", "message": f"Book with ID {book_id} not found"}), 404

            set_clause = ', '.join(f"{field} = ?" for field in data.keys())

            cursor.execute(
                f"UPDATE books SET {set_clause} WHERE book_id = ?",
                tuple(data.values()) + (book_id,)
            )
            connection.commit()
            return jsonify({"message": f"Book with ID {book_id} updated successfully"}), 201

        except Exception as e:
            connection.rollback()
            return error_response(f"Failed to update book. Reason: {str(e)}", 500)





@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    """
    DELETE endpoint to delete a specific book by its ID.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the book with the specified ID exists
        cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
        existing_book = cursor.fetchone()

        if existing_book is None:
            # Return a 404 Not Found status code
            abort(404, description=f"Book with ID {book_id} not found")

        # Delete the book if it exists
        cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        connection.commit()

        return jsonify({"message": f"Book with ID {book_id} deleted successfully"}), 200

    except Exception as e:
        connection.rollback()
        return error_response(f"Failed to delete book. Reason: {str(e)}", 500)



@app.route("/reviews", methods=["POST"])
@log_request_body
def add_review():
    """
    POST endpoint to add a new review for a book.
    Requires a JSON payload with 'book_id', 'review_text', and 'review_score' fields.
    """
    if request.method == "POST":
        data = request.json

        if not all(field in data for field in ['book_id', 'review_text', 'review_score']):
            return error_response("book_id, review_text, and review_score are required", 400)

        book_id = data["book_id"]
        review_text = data["review_text"]
        review_score = data["review_score"]

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO reviews (book_id, review_text, review_score) VALUES (?, ?, ?)",
                (book_id, review_text, review_score)
            )
            connection.commit()
            return jsonify({"message": f"Review for Book with {book_id} added successfully"}), 201

        except Exception as e:
            connection.rollback()
            return error_response(f"Failed to add review. Reason: {str(e)}", 500)




@app.route("/reviews", methods=["GET"])
def get_all_reviews():
    """
    GET endpoint to retrieve all reviews from the database.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
                       SELECT reviews.book_id, books.title as book_title, reviews.review_text
                       FROM reviews
                       LEFT JOIN books ON reviews.book_id = books.book_id
                    """)
        data = cursor.fetchall()

        review_list = []
        for row in data:
            review = {
                "book_id": row["book_id"],
                "book_title": row["book_title"],
                "review_text": row["review_text"]
            }
            review_list.append(review)

        return jsonify(reviews=review_list), 200

    except Exception as e:
        return error_response(f"Failed to fetch reviews. Reason: {str(e)}", 500)



@app.route("/reviews/<int:book_id>", methods=["GET"])
def get_book_reviews(book_id):
    """
    GET endpoint to retrieve all reviews for a specific book by its ID.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
                       SELECT reviews.book_id, books.title as book_title, reviews.review_text
                       FROM reviews
                       LEFT JOIN books ON reviews.book_id = books.book_id
                       WHERE reviews.book_id = ?
                    """, (book_id,))

        data = cursor.fetchall()

        if data:
            review_list = []
            for row in data:
                review = {
                    "book_id": row["book_id"],
                    "book_title": row["book_title"],
                    "review_text": row["review_text"]
                }
                review_list.append(review)

            return jsonify(reviews=review_list), 200
        else:
            return error_response(f"Reviews for Book ID {book_id} not found", 404)

    except Exception as e:
        return error_response(f"Failed to fetch reviews. Reason: {str(e)}", 500)


@app.route("/books/top", methods=["GET"])
def get_top_reviews():
    """
    GET endpoint to retrieve the top five books with the highest average review score.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
                        SELECT books.book_id as book_id, books.title as book_title, CAST(avg(reviews.review_score) AS REAL) as average_score
                        FROM books
                        JOIN reviews ON books.book_id = reviews.book_id
                        GROUP BY books.book_id, books.title
                        ORDER BY average_score DESC
                        LIMIT 5;
                    """)

        data = cursor.fetchall()

        if data:
            books_list = []
            for row in data:
                book = {
                    "book_id": row["book_id"],
                    "book_title": row["book_title"],
                    "average_score": row["average_score"]
                }
                books_list.append(book)

            return jsonify(top_5_books=books_list), 200
        else:
            return error_response("There were no books", 404)

    except Exception as e:
        return error_response(f"Failed to fetch top books. Reason: {str(e)}", 500)


@app.route("/author", methods=["GET"])
def get_author():
    """
    GET endpoint to retrieve a brief summary about an author and their most famous works.
    Requires the 'name' parameter in the query string.
    """
    author_name = request.args.get("name")

    if author_name is None:
        return error_response("Author name not provided", 400)

    try:
        result = asyncio.run(get_author_info(author_name))
        return jsonify(result)

    except Exception as e:
        return error_response(f"Failed to fetch author information. Reason: {str(e)}", 500)


