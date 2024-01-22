from flask import Flask, request, render_template, jsonify
import json
import sqlite3

app = Flask(__name__)

#connect to database
def get_db_connection():
    connection = sqlite3.connect("Books.db")
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def home():
    return "Hello world"

#GET /books - Hämtar alla böcker i databasen. Du ska kunna filtrera på titel, författare och/eller genre via en parameter i search-query. Exempelvis: /books?genre=biography
#working
@app.route("/books", methods=["GET"])
def get_books():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM books")
    data = cursor.fetchall()

    connection.close()
    
    books_list = []
    for row in data:
        book = {
            "book_id": row["book_id"],
            "title": row["title"],
            "author": row["author"],
            "summary": row["summary"],
            "genre": row["genre"]
        }
        books_list.append(book)
    
    return jsonify(books=books_list)
    
#POST /books - Lägger till en eller flera böcker i databasen. 
#working - room for improvement   
@app.route("/books", methods=["POST"])
def add_books():
    if request.method == "POST":
        # Get data from the request
        data = request.get_json()

        # Validate the required fields
        if "title" not in data or "author" not in data:
            return jsonify({"error": "Title and Author are required"}), 400

        # Extract data from the request
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
            connection.close()
            return jsonify({"message": "Book added successfully"}), 201
        except Exception as e:
            connection.rollback()
            connection.close()
            return jsonify({"error": str(e)}), 500

#GET /books/{book_id} - Hämtar en enskild bok.
@app.route("/books/{book_id}", methods=["GET"])
def get_book_id(book_id):
    pass


#PUT /books/{book_id} - Uppdaterar information om en enskild bok.
@app.route("/books/{book_id}", methods=["PUT"])
def update_book(book_id):
    pass

#DELETE /books/{book_id} - Tar bort en enskild bok
@app.route("/books/{book_id}", methods=["DELETE"])
def delete_book(book_id):
    pass

#POST /reviews -  Lägger till en ny recension till en bok.
@app.route("/reviews", methods=["POST"])
def add_review():
    pass


#GET /reviews - Hämtar alla recensioner som finns i databasen
@app.route("/reviews", methods=["GET"])
def get_all_reviews():
    pass


#GET /reviews/{book_id} - Hämtar alla recensioner för en enskild bok.
@app.route("/reviwes/{book_id}", methods=["GET"])
def get_book_reviews(book_id):
    pass


#GET /books/top - Hämtar de fem böckerna med högst genomsnittliga recensioner.
@app.route("/books/top", methods=["GET"])
def get_top_reviews():
    pass

#GET /author - Hämtar en kort sammanfattning om författaren och författarens mest kända verk. Använd externa API:er för detta.
@app.route("/author", methods=["GET"])
def get_author():
    pass




if __name__ == "__main__":
    app.run(debug=True)