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
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 flex items-center justify-center min-h-screen">
    <div class="container mx-auto p-4 md:p-8 text-center">
        <header class="mb-12">
            <h1 class="text-4xl font-bold text-gray-50 mb-2">Iconic Quotes from Movies & Shows</h1>
            <p class="text-lg text-gray-400">A collection of memorable dialogues.</p>
        </header>

        <main id="quote-container" class="bg-gray-800 rounded-lg shadow-lg p-6 w-full max-w-xl mx-auto min-h-[200px] flex flex-col justify-center items-center transition-opacity duration-1000 ease-in-out">
            <blockquote id="quote-text" class="text-xl font-medium leading-relaxed text-gray-200 mb-4">
                "Loading quotes..."
            </blockquote>
            <p id="quote-source" class="text-sm font-semibold text-gray-400 text-right">
                -
            </p>
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

            function displayQuote() {
                if (quotes.length === 0) {
                    quoteTextElement.textContent = "No quotes available. Add one!";
                    quoteSourceElement.textContent = "-";
                    return;
                }

                // Add a fading effect
                quoteContainer.style.opacity = '0';
                setTimeout(() => {
                    const quote = quotes[currentQuoteIndex];
                    quoteTextElement.textContent = `"${quote.text}"`;
                    quoteSourceElement.textContent = `- ${quote.source || 'Unknown'}`;
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

# Sample movie and show quotes to populate the database initially
SAMPLE_QUOTES = [
    {"text": "May the Force be with you.", "source": "Star Wars"},
    {"text": "I'm the king of the world!", "source": "Titanic"},
    {"text": "Here's looking at you, kid.", "source": "Casablanca"},
    {"text": "Houston, we have a problem.", "source": "Apollo 13"},
    {"text": "My precious.", "source": "The Lord of the Rings"},
    {"text": "Elementary, my dear Watson.", "source": "Sherlock Holmes"},
    {"text": "Live long and prosper.", "source": "Star Trek"},
]


# --- Routes ---
@app.route('/')
def index():
    """
    Renders the homepage, displaying a single quote from the database at a time.
    """
    quotes = Quote.query.all()
    quotes_list = [{"text": quote.text, "source": quote.source} for quote in quotes]
    # Pass the quotes as a JSON string for the JavaScript to use
    return render_template_string(INDEX_TEMPLATE, quotes_json=jsonify(quotes_list).get_data(as_text=True))


@app.route('/add')
def add_quote():
    """
    Renders the form to add a new quote.
    """
    # In a real app, you'd use render_template('add.html')
    return render_template_string(ADD_QUOTE_TEMPLATE)


@app.route('/add_quote', methods=['POST'])
def add_quote_post():
    """
    Handles the form submission to add a new quote to the database.
    """
    try:
        text = request.form['text']
        source = request.form.get('source')
        new_quote = Quote(text=text, source=source)
        db.session.add(new_quote)
        db.session.commit()
    except Exception as e:
        print(f"Error adding quote: {e}")
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
        # This line creates the table based on the 'Quote' model
        db.create_all()

        # Add sample quotes if the database is empty
        if not Quote.query.first():
            for q in SAMPLE_QUOTES:
                db.session.add(Quote(text=q['text'], source=q['source']))
            db.session.commit()

    # Run the Flask development server
    app.run(debug=True)
