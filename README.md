# Fitness_tracker_30011
fitness tracker
🏃 Personal Fitness Tracker
This is a personal fitness tracker application designed to help individuals track their fitness activities, set personal goals, and share their progress with friends. The core feature is a dynamic leaderboard that ranks friends based on a chosen fitness metric.

The application is built in Python using Streamlit for the frontend and a PostgreSQL database for the backend.

✨ Features
User Profile Management: Create and update a personal profile (name, email, weight).

Workout and Progress Tracking: Log workouts with details like duration and a list of exercises (sets, reps, weight). Visualize your progress over time with charts.

Dynamic Leaderboard: View a leaderboard that ranks you and your friends based on selected metrics (e.g., total workouts, total minutes).

Social Connections: Add and remove friends to compete on the leaderboard.

Goal Setting: Set personal fitness goals to stay motivated.

Business Insights: Get a quick overview of key metrics like total workouts and average duration.

⚙️ Technical Stack
Frontend: Python with Streamlit

Backend: Python

Database: PostgreSQL

Database Connector: psycopg2

🚀 Getting Started
Prerequisites
Python 3.x installed.

PostgreSQL installed and running.

Installation
Clone the repository:

git clone https://github.com/your-username/fitness-tracker.git
cd fitness-tracker

Install the required Python packages:

pip install -r requirements.txt

(Note: You'll need to create a requirements.txt file containing streamlit and psycopg2-binary).

Database Setup
Create a PostgreSQL database:
Open your PostgreSQL client and run the following command to create the database:

CREATE DATABASE fitness_tracker;

Configure database connection:
Open the backend.py file and update the DatabaseManager class with your PostgreSQL credentials:

db = DatabaseManager(dbname="fitness_tracker", user="your_username", password="your_password")

Run the application for the first time:
The DatabaseManager will automatically create all the necessary tables (users, workouts, exercises, friends, goals) the first time it connects.

Running the Application
Once everything is set up, run the Streamlit app from your terminal:

streamlit run frontend.py

The application will open in your web browser at http://localhost:8501.

🤝 Contribution
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

Fork the Project.

Create your Feature Branch (git checkout -b feature/AmazingFeature).

Commit your Changes (git commit -m 'Add some AmazingFeature').

Push to the Branch (git push origin feature/AmazingFeature).

Open a Pull Request.

📄 License
Distributed under the MIT License. See LICENSE for more information.

📬 Contact
Project Link: https://github.com/your-username/fitness-tracker
