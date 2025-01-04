from flask import Flask, render_template, request, redirect, url_for
import pickle
import numpy as np

# Load data
popular_df = pickle.load(open('c:/Users/lenovo/Desktop/brs_website/model/popular.pkl', 'rb'))
pt = pickle.load(open('c:/Users/lenovo/Desktop/brs_website/model/pt.pkl', 'rb'))
books = pickle.load(open('c:/Users/lenovo/Desktop/brs_website/model/books.pkl', 'rb'))
similarity_scores = pickle.load(open('c:/Users/lenovo/Desktop/brs_website/model/similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_ratings'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend_books():
    user_input = request.form.get('user_input')
    
    # Call the recommend function to fetch recommended books
    recommended_books = recommend(user_input)
    
    if isinstance(recommended_books, str):  # If a string, it's an error message
        return render_template('recommend.html', error=recommended_books)
    
    return render_template('recommend.html', data=recommended_books)

# Change contact to about
@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        # Handle form submission here (you can process data, like handling feedback)
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        # You can process the data or send an email if needed
        return redirect(url_for('index'))  # Redirect to home after submitting the form
    
    return render_template('about.html')  # Render the 'about.html' template

def recommend(book_name):
    
    book_name_lower = book_name.lower()
    
    
    index = np.where(pt.index.str.lower() == book_name_lower)[0]
    
    if len(index) == 0:
        return "Book not found. Please check the spelling or try a different book."
    
    index = index[0] 
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]
    
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'].str.lower() == pt.index[i[0]].lower()]
        
        
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        
        
        image_url_m = temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values
        image_url_s = temp_df.drop_duplicates('Book-Title')['Image-URL-S'].values
        image_url_l = temp_df.drop_duplicates('Book-Title')['Image-URL-L'].values
        
      
        if image_url_m.size > 0 and image_url_m[0]: 
            item.append(image_url_m[0])
        elif image_url_s.size > 0 and image_url_s[0]: 
            item.append(image_url_s[0])
        elif image_url_l.size > 0 and image_url_l[0]:  
            item.append(image_url_l[0])
        else:
            item.append("default_image_url_here")  

        data.append(item)
    
    return data

if __name__ == '__main__':
    app.run(debug=True)
