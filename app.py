# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Load environment variables from the .env file
load_dotenv()

# --- Configuration ---
# You will need to install the following packages:
# pip install Flask Flask-SQLAlchemy PyMySQL python-dotenv

# Create the Flask application instance
app = Flask(__name__)

# Configure the database connection using environment variables
# The format is 'mysql+pymysql://user:password@host/database_name'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://user:password@localhost/quotes_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy database instance
db = SQLAlchemy(app)


# --- Database Model ---
# Define a 'Quote' model to represent the quotes table in the database
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), nullable=True)
    background_image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Quote {self.id}>'


# --- HTML Templates (as strings for self-contained code) ---
# In a real application, these would be in a 'templates' folder.
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie & Show Quotes</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Inter', sans-serif;
            background-size: cover;
            background-position: center;
            transition: background-image 1s ease-in-out;
        }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 flex items-center justify-center min-h-screen">
    <div class="container mx-auto p-4 md:p-8 text-center relative z-10">
        <header class="mb-12">
            <h1 class="text-4xl font-bold text-gray-50 mb-2">Iconic Quotes from Movies & Shows</h1>
            <p class="text-lg text-gray-400">A collection of memorable dialogues.</p>
        </header>

        <main id="quote-container" class="bg-black bg-opacity-50 rounded-lg shadow-lg p-6 w-full max-w-xl mx-auto min-h-[200px] flex flex-col justify-center items-center transition-opacity duration-1000 ease-in-out">
            <blockquote id="quote-text" class="text-xl font-medium leading-relaxed text-gray-200 mb-4">
                "Loading quotes..."
            </blockquote>
            <p id="quote-source" class="text-sm font-semibold text-gray-400 text-right">
                -
            </p>
            <div id="quote-actions" class="mt-4 hidden">
                <a id="edit-quote-link" href="#" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 mr-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                    Edit
                </a>
                <a id="delete-quote-link" href="#" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.013 21H7.987a2 2 0 01-1.92-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Delete
                </a>
            </div>
        </main>
        
        <div class="mt-8 text-center">
            <a href="{{ url_for('add_quote') }}" class="inline-block bg-blue-600 text-white p-4 rounded-full shadow-2xl hover:bg-blue-500 transition-transform transform hover:scale-110">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
            </a>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // Retrieve quotes data from a data attribute on the body
            const quotes = {{ quotes_json | safe }};

            let currentQuoteIndex = 0;
            const quoteTextElement = document.getElementById('quote-text');
            const quoteSourceElement = document.getElementById('quote-source');
            const quoteContainer = document.getElementById('quote-container');
            const editQuoteLink = document.getElementById('edit-quote-link');
            const deleteQuoteLink = document.getElementById('delete-quote-link');
            const quoteActions = document.getElementById('quote-actions');
            const bodyElement = document.body;

            function displayQuote() {
                if (quotes.length === 0) {
                    quoteTextElement.textContent = "No quotes available. Add one!";
                    quoteSourceElement.textContent = "-";
                    bodyElement.style.backgroundImage = 'none';
                    quoteActions.classList.add('hidden');
                    return;
                }

                // Add a fading effect
                quoteContainer.style.opacity = '0';
                setTimeout(() => {
                    const quote = quotes[currentQuoteIndex];
                    quoteTextElement.textContent = `"${quote.text}"`;
                    quoteSourceElement.textContent = `- ${quote.source || 'Unknown'}`;
                    
                    // Set the background image on the body
                    if (quote.background_image_url) {
                        bodyElement.style.backgroundImage = `url('${quote.background_image_url}')`;
                    } else {
                        bodyElement.style.backgroundImage = 'none';
                    }
                    
                    // Update the edit and delete links with the correct quote ID
                    editQuoteLink.href = `/edit/${quote.id}`;
                    deleteQuoteLink.href = `/delete/${quote.id}`;
                    quoteActions.classList.remove('hidden');

                    quoteContainer.style.opacity = '1';

                    // Move to the next quote
                    currentQuoteIndex = (currentQuoteIndex + 1) % quotes.length;
                }, 500); // 500ms for the fade-out effect
            }

            // Display the first quote immediately
            displayQuote();

            // Set up an interval to change the quote every 7 seconds
            setInterval(displayQuote, 7000);
        });
    </script>
</body>
</html>
"""

ADD_QUOTE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add New Quote</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-gray-800 rounded-lg shadow-lg p-8 w-full max-w-md">
        <h2 class="text-2xl font-bold text-gray-50 mb-6 text-center">Add a New Quote</h2>
        <form method="POST" action="{{ url_for('add_quote_post') }}">
            <div class="mb-4">
                <label for="text" class="block text-gray-300 font-medium mb-2">Quote Text</label>
                <textarea id="text" name="text" rows="4" required class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
            </div>
            <div class="mb-6">
                <label for="source" class="block text-gray-300 font-medium mb-2">Source (Movie/Show)</label>
                <input type="text" id="source" name="source" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
             <div class="mb-6">
                <label for="background_image_url" class="block text-gray-300 font-medium mb-2">Background Image URL</label>
                <input type="text" id="background_image_url" name="background_image_url" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
            <div class="flex justify-between">
                <button type="submit" class="w-1/2 mr-2 bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition duration-300">
                    Submit
                </button>
                <a href="{{ url_for('index') }}" class="w-1/2 ml-2 text-center bg-gray-600 text-white font-semibold py-3 rounded-lg hover:bg-gray-700 transition duration-300">
                    Cancel
                </a>
            </div>
        </form>
    </div>
</body>
</html>
"""

EDIT_QUOTE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Quote</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-gray-800 rounded-lg shadow-lg p-8 w-full max-w-md">
        <h2 class="text-2xl font-bold text-gray-50 mb-6 text-center">Edit Quote</h2>
        <form method="POST" action="{{ url_for('edit_quote_post', quote_id=quote.id) }}">
            <div class="mb-4">
                <label for="text" class="block text-gray-300 font-medium mb-2">Quote Text</label>
                <textarea id="text" name="text" rows="4" required class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">{{ quote.text }}</textarea>
            </div>
            <div class="mb-6">
                <label for="source" class="block text-gray-300 font-medium mb-2">Source (Movie/Show)</label>
                <input type="text" id="source" name="source" value="{{ quote.source }}" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
             <div class="mb-6">
                <label for="background_image_url" class="block text-gray-300 font-medium mb-2">Background Image URL</label>
                <input type="text" id="background_image_url" name="background_image_url" value="{{ quote.background_image_url }}" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
            <div class="flex justify-between">
                <button type="submit" class="w-1/2 mr-2 bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition duration-300">
                    Update
                </button>
                <a href="{{ url_for('index') }}" class="w-1/2 ml-2 text-center bg-gray-600 text-white font-semibold py-3 rounded-lg hover:bg-gray-700 transition duration-300">
                    Cancel
                </a>
            </div>
        </form>
    </div>
</body>
</html>
"""

# Sample movie and show quotes to populate the database initially
SAMPLE_QUOTES = [
    {"text": "May the Force be with you.", "source": "Star Wars", "background_image_url": "https://placehold.co/1920x1080/000000/FFFFFF?text=Star+Wars"},
    {"text": "I'm the king of the world!", "source": "Titanic", "background_image_url": "https://placehold.co/1920x1080/000000/FFFFFF?text=Titanic"},
    {"text": "Here's looking at you, kid.", "source": "Casablanca", "background_image_url": "https://placehold.co/1920x1080/000000/FFFFFF?text=Casablanca"},
    {"text": "Houston, we have a problem.", "source": "Apollo 13", "background_image_url": "https://placehold.co/1920x1080/000000/FFFFFF?text=Apollo+13"},
    {"text": "My precious.", "source": "The Lord of the Rings", "background_image_url": "https://placehold.co/1920x1080/000000/FFFFFF?text=Lord+of+the+Rings"},
    {"text": "Elementary, my dear Watson.", "source": "Sherlock Holmes", "background_image_url": "https://placehold.co/1920x1080/000000/FFFFFF?text=Sherlock+Holmes"},
    {"text": "Live long and prosper.", "source": "Star Trek", "background_image_url": "https://placehold.co/1920x1080/000000/FFFFFF?text=Star+Trek"},
]


# --- Routes ---
@app.route('/')
def index():
    """
    Renders the homepage, displaying a single quote from the database at a time.
    """
    quotes = Quote.query.all()
    # Serialize the quotes to a list of dictionaries, including the ID
    quotes_list = [{"id": quote.id, "text": quote.text, "source": quote.source, "background_image_url": quote.background_image_url} for quote in quotes]
    # Pass the quotes as a JSON string for the JavaScript to use
    return render_template_string(INDEX_TEMPLATE, quotes_json=jsonify(quotes_list).get_data(as_text=True))


@app.route('/add')
def add_quote():
    """
    Renders the form to add a new quote.
    """
    return render_template_string(ADD_QUOTE_TEMPLATE)


@app.route('/add_quote', methods=['POST'])
def add_quote_post():
    """
    Handles the form submission to add a new quote to the database.
    """
    try:
        text = request.form['text']
        source = request.form.get('source')
        background_image_url = request.form.get('background_image_url')
        new_quote = Quote(text=text, source=source, background_image_url=background_image_url)
        db.session.add(new_quote)
        db.session.commit()
    except Exception as e:
        print(f"Error adding quote: {e}")
        db.session.rollback()

    return redirect(url_for('index'))

@app.route('/edit/<int:quote_id>')
def edit_quote(quote_id):
    """
    Renders the form to edit an existing quote.
    """
    quote = Quote.query.get_or_404(quote_id)
    return render_template_string(EDIT_QUOTE_TEMPLATE, quote=quote)

@app.route('/edit_quote_post/<int:quote_id>', methods=['POST'])
def edit_quote_post(quote_id):
    """
    Handles the form submission to update an existing quote.
    """
    try:
        quote = Quote.query.get_or_404(quote_id)
        quote.text = request.form['text']
        quote.source = request.form.get('source')
        quote.background_image_url = request.form.get('background_image_url')
        db.session.commit()
    except Exception as e:
        print(f"Error editing quote: {e}")
        db.session.rollback()

    return redirect(url_for('index'))


@app.route('/delete/<int:quote_id>')
def delete_quote(quote_id):
    """
    Deletes a quote with the specified ID.
    """
    quote = Quote.query.get_or_404(quote_id)
    db.session.delete(quote)
    db.session.commit()
    return redirect(url_for('index'))


def render_template_string(template_string, **kwargs):
    """
    A helper function to render templates from a string.
    This is for demonstration purposes to keep the code in one file.
    """
    env = Environment(loader=FileSystemLoader('.'))
    # Pass Flask's url_for function to the template context
    return env.from_string(template_string).render(url_for=url_for, **kwargs)


# --- Setup and Running ---
if __name__ == '__main__':
    # Create the database and table if they don't exist
    with app.app_context():
        # IMPORTANT: If you encounter an error like "Unknown column 'background_image_url'",
        # it's because the database table was created from a previous version of the code.
        # You need to drop the old table for the new one to be created with the correct schema.
        # To fix, connect to your MySQL database and run: DROP TABLE quote;
        # Then restart the Flask application.
        db.create_all()

        # Add sample quotes if the database is empty
        if not Quote.query.first():
            for q in SAMPLE_QUOTES:
                db.session.add(Quote(text=q['text'], source=q['source'], background_image_url=q['background_image_url']))
            db.session.commit()

    # Run the Flask development server
    app.run(debug=True)
