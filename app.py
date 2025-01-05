from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

# Load trained models and data
popularityDF = joblib.load(open("/Users/abdullah/ProjectML/book-recommendation-system/popularity.pkl", "rb"))
finalTable = joblib.load(open('/Users/abdullah/ProjectML/book-recommendation-system/final.pkl', 'rb'))
books = joblib.load(open('/Users/abdullah/ProjectML/book-recommendation-system/books.pkl', 'rb'))
similarScores = joblib.load(open('/Users/abdullah/ProjectML/book-recommendation-system/similarity_scores.pkl', 'rb'))

@app.route('/')
def recommend_ui():
    # Render the page with no recommendations initially
    return render_template('index.html', data=None, message=None)

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    try:
        # Find book index and get similar books
        index = np.where(finalTable.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarScores[index])), key=lambda x: x[1], reverse=True)[1:5]

        # Prepare recommendations
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == finalTable.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)

        # Store recommendations temporarily using Flask session
        return render_template('index.html', data=data, message=None)

    except IndexError:
        # Redirect with a message if the book title isn't found
        return redirect(url_for('recommend_ui', message="No recommendations found. Please check the book title."))

@app.route('/clear')
def clear_recommendations():
    # Redirect to the home page to clear any recommendations still present there
    return redirect(url_for('recommend_ui'))

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('query', '')
    print("Incoming query for autocomplete suggestion is: ", query)
    if query:
        suggestions = popularityDF[popularityDF['Book-Title'].str.contains(query, case=False, na=False)]['Book-Title'].tolist()
    else:
        suggestions = []
    
    return jsonify(suggestions[0:5])

@app.route('/bookcase')
def bookcase():
    # Pass the filtered popular books to the template
    popular_books = popularityDF[['Book-Title', 'Book-Author', 'Image-URL-M']].drop_duplicates()
    return render_template('bookcase.html', books=popular_books)

if __name__ == '__main__':
    app.run(debug=True)

