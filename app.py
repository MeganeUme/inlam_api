from flask import Flask, request, jsonify, current_app, g
import requests
import sqlite3
from database import get_db_connection, close_db_connection
from decorator import log_request_body

app = Flask(__name__)

app.config["DATABASE"] = "Books.db"



@app.route("/")
def home():
    return "Hello world"

#GET /books - Hämtar alla böcker i databasen. Du ska kunna filtrera på titel, författare och/eller genre via en parameter i search-query. Exempelvis: /books?genre=biography
#working
@app.route("/books", methods=["GET"])
@log_request_body
def get_books():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                    SELECT books.*, CAST(avg(reviews.review_score) AS REAL) as average_score
                    FROM books
                    JOIN reviews ON books.book_id = reviews.book_id
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
            "average_score" :row["average_score"]
        }
        books_list.append(book)
    
    return jsonify(books=books_list), 200
    
#POST /books - Lägger till en eller flera böcker i databasen. 
#working - room for improvement   
@app.route("/books", methods=["POST"])
@log_request_body
def add_books():
    if request.method == "POST":
        data = request.json

        # Validate the required fields and data types
        if not all(field in data for field in ['title', 'author']):
            return jsonify({"error": "Title and Author are required"}), 400

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
            return jsonify({"error": str(e)}), 500

#GET /books/{book_id} - Hämtar en enskild bok.
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book_id(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                    SELECT books.*, CAST(avg(reviews.review_score) AS REAL) as average_score
                    FROM books
                    JOIN reviews ON books.book_id = reviews.book_id
                    WHERE books.book_id = ?
                    GROUP BY books.book_id, books.title
                """, (book_id,))

    data = cursor.fetchone()

    if data:
            # Convert the data to a dictionary for JSON serialization
        book = {
            "book_id": data["book_id"],
            "title": data["title"],
            "author": data["author"],
            "summary": data["summary"],
            "genre": data["genre"],
            "average_score": data["average_score"]
        }
        return jsonify(book), 200
    else:
        return jsonify({"error": f"Book with ID {book_id} not found"}), 404
    


#PUT /books/{book_id} - Uppdaterar information om en enskild bok.
# NEED TO FIX THIS working
@app.route("/books/<int:book_id>", methods=["PUT"])
@log_request_body
def update_book(book_id):
    if request.method == "PUT":
        data = request.json

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            set_clause = ', '.join(f"{field} = ?" for field in data.keys())

            cursor.execute(
                f"UPDATE books SET {set_clause} WHERE book_id = ?",
                tuple(data.values()) + (book_id,)
            )
            connection.commit()
            return jsonify({"message": f"Book with ID {book_id} updated successfully"}), 201
        except Exception as e:
            connection.rollback()
            return jsonify({"error": str(e)}), 500


#DELETE /books/{book_id} - Tar bort en enskild bok
#working
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        connection.commit()
        return jsonify({"message": f"Book with ID {book_id} deleted successfully"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"erorr": str(e)}), 500

#POST /reviews -  Lägger till en ny recension till en bok.
#working improvement ?
@app.route("/reviews", methods=["POST"])
@log_request_body
def add_review():
    if request.method == "POST":
        data = request.json

        if not all(field in data for field in ['book_id', 'review_text', 'review_score']):
            return jsonify({"error": "book_id, review_text, and review_score are required"}), 400

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
            return jsonify({"error": str(e)}), 500




#GET /reviews - Hämtar alla recensioner som finns i databasen
#working
@app.route("/reviews", methods=["GET"])
def get_all_reviews():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT reviews.book_id, books.title as book_title, reviews.review_text
                   FROM reviews
                   JOIN books ON reviews.book_id = books.book_id
                """)
    data = cursor.fetchall()

    reveiw_list = []
    for row in data:
        review = {
            "book_id" : row["book_id"],
            "book_title" : row["book_title"],
            "review_text" : row["review_text"]
        }
        reveiw_list.append(review)
    
    return jsonify(reviews=reveiw_list), 200
    


#GET /reviews/{book_id} - Hämtar alla recensioner för en enskild bok.
@app.route("/reviews/<int:book_id>", methods=["GET"])
def get_book_reviews(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT reviews.book_id, books.title as book_title, reviews.review_text
                   FROM reviews
                   JOIN books ON reviews.book_id = books.book_id
                   WHERE reviews.book_id = ?
                """, (book_id,))
    
    data = cursor.fetchall()
    
    if data:
        reveiw_list = []
        for row in data:
            review = {
                "book_id" : row["book_id"],
                "book_title" : row["book_title"],
                "review_text" : row["review_text"]
            }
            reveiw_list.append(review)
    
        return jsonify(reviews=reveiw_list), 200
    else:
        return jsonify({"error": f"Reviews for Book ID {book_id} not found"}), 404

#GET /books/top - Hämtar de fem böckerna med högst genomsnittliga recensioner.
@app.route("/books/top", methods=["GET"])
def get_top_reviews():
    connection = get_db_connection()
    cursor = connection.cursor()

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
                "book_id" : row["book_id"],
                "book_title" : row["book_title"],
                "average_score" : row["average_score"]
            }
            books_list.append(book)
        return jsonify(top_books=books_list), 200
    else:
        return jsonify({"error": "There was no books"}), 404

#GET /author - Hämtar en kort sammanfattning om författaren och författarens mest kända verk. Använd externa API:er för detta.
@app.route("/author", methods=["GET"])
@log_request_body
def get_author():
    author_name = request.args.get("name")

    if author_name is None:
        return jsonify({"error": "Author name not provided"}), 400
    
    known_work = get_author_most_known_work(author_name)

    if known_work is None:
        return jsonify({"error": "No information found for the specified author"}), 404
    
    short_summary = get_author_short_summary(author_name)


    response_data = {
        "author_name" : author_name,
        "most_known_work" : known_work,
        "short_summary" : short_summary
    }

    return jsonify(response_data)

def get_author_most_known_work(author_name):
    search_url = f"https://openlibrary.org/search.json?author={author_name.replace(' ', '+')}"
    response = requests.get(search_url)
    data = response.json()

    #check if results were found
    if "docs" not in data or len(data["docs"]) == 0:
        return None, None
    
    result = data["docs"][0]

    known_work = result.get("title", "Unkown")
    
    return known_work


def get_author_short_summary(author_name):
    base_url = "https://en.wikipedia.org/w/api.php"
    
    # Set parameters for the Wikipedia API request
    params = {
        "action": "query",
        "format": "json",
        "titles": author_name,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True
    }

    # Make the API request
    response = requests.get(base_url, params=params)
    data = response.json()

    # Extract and return the summary
    page = next(iter(data["query"]["pages"].values()), None)
    if page:
        return page["extract"]
    else:
        return "Summary not found."


if __name__ == "__main__":
    app.run(debug=True)