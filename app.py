from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import joblib
import numpy as np
import os

# Initialize the Flask app
app = Flask(__name__)

# Get the current directory of the app.py file
base_dir = os.path.dirname(os.path.abspath(__file__))

# Load pickle files from the static folder
popularityDF = joblib.load(open(os.path.join(base_dir, 'static/popularity.pkl'), 'rb'))
finalTable = joblib.load(open(os.path.join(base_dir, 'static/final.pkl'), 'rb'))
books = joblib.load(open(os.path.join(base_dir, 'static/books.pkl'), 'rb'))
similarScores = joblib.load(open(os.path.join(base_dir, 'static/similarity_scores.pkl'), 'rb'))

# Routes
@app.route('/')
def recommend_ui():
    return render_template('index.html', data=None, message=None)

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    try:
        index = np.where(finalTable.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarScores[index])), key=lambda x: x[1], reverse=True)[1:5]
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == finalTable.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)
        return render_template('index.html', data=data, message=None)
    except IndexError:
        return redirect(url_for('recommend_ui', message="No recommendations found. Please check the book title."))

@app.route('/clear')
def clear_recommendations():
    return redirect(url_for('recommend_ui'))

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('query', '')
    if query:
        suggestions = popularityDF[popularityDF['Book-Title'].str.contains(query, case=False, na=False)]['Book-Title'].tolist()
    else:
        suggestions = []
    return jsonify(suggestions[0:5])

@app.route('/bookcase')
def bookcase():
    popular_books = popularityDF[['Book-Title', 'Book-Author', 'Image-URL-M']].drop_duplicates()
    return render_template('bookcase.html', books=popular_books)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

