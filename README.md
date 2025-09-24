# Stock-Exchange-Game

Author : - Shubham Salunkhe




---

📈 Stock Exchange Game

A stock trading simulation web application built with Python (Flask) and SQLite. It allows users to register, log in, and trade stocks with virtual money while fetching live stock prices from a real-world API. This project is ideal for learning stock market basics, practicing web development, or exploring Flask-based projects.


---

✨ Features

🔑 User Authentication

Secure registration and login system.

Each user has a personal portfolio and virtual balance.


💹 Live Stock Prices (Real-World)

Stock prices update in real time using an external API (e.g., Alpha Vantage or Yahoo Finance).

Dashboard displays accurate, up-to-date market values.


🛒 Trading System

Buy and sell stocks using your virtual balance.

View trade history and track your current portfolio value.


📊 Portfolio Management

Monitor holdings, profit/loss, and remaining balance in real time.


🎨 Responsive Front-End

Clean, intuitive UI built with HTML, CSS, and JavaScript.

Uses AJAX for smooth, live updates without page reloads.




---

🛠️ Tech Stack

Layer	Technologies Used

Backend	Python, Flask
Database	SQLite
Frontend	HTML, CSS, JavaScript
Utilities	Real-world stock price API calls, Flask Blueprints



---

🚀 Getting Started

1️⃣ Prerequisites

Python 3.9+

pip (Python package manager)

Git

API key from your chosen stock price provider (e.g., Alpha Vantage)


2️⃣ Clone the Repository

git clone https://github.com/salunkheshubham263-commits/Stock-Exchange-Game.git
cd Stock-Exchange-Game

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Environment Configuration

Create a .env file in the root directory.

Add the following variables (adjust values as needed):

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
STOCK_API_KEY=your_api_key_here


5️⃣ Initialize the Database

Use the provided scripts in the database/ folder or run the app once to generate stock_game.db.


6️⃣ Run the Application

python app.py

Open your browser and visit: http://localhost:5000



---

📂 Project Structure

Stock-Exchange-Game/
│
├── api/               # Stock-related API endpoints and logic
├── database/          # Database initialization and management
├── static/            # CSS, JavaScript, and images
├── templates/         # HTML templates for Flask
├── utils/             # Helper functions (e.g., API calls for live prices)
├── app.py             # Main Flask application
├── requirements.txt   # Python dependencies
├── stock_game.db      # SQLite database (generated)
├── .env.example       # Example environment configuration
└── README.md          # Project documentation


---

📖 Usage Guide

1. Register for an account on the homepage.


2. Log in to access your dashboard.


3. View live stock prices retrieved from the external API.


4. Use Buy and Sell to trade stocks.


5. Track your portfolio balance and trade history to monitor performance.




---

🧩 Future Improvements

💾 Persistent trade history across sessions.

📊 Enhanced analytics and portfolio performance graphs.

📱 Improved mobile-friendly UI/UX.

🔔 Price alerts and notifications.



---

📜 License

This project is licensed under the MIT License. See LICENSE for details.


---

✅ Corrections made:

Minor grammar and consistency fixes (“uses an external API” → “using an external API”, clarified “visit” instead of “go to”).

Cleaned up table formatting.

Clarified .env instructions.


Would you like me to save this as a ready-to-use README.md file for download?

