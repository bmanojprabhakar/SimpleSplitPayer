# Trip Expense Tracker

A simple web application to track shared expenses between two people, with automatic balance calculation and running totals.

## Features

- Add new expenses with details like date, description, category, and payment mode
- Automatic calculation of equal shares (customizable)
- Track running balance between two people
- View all expenses in a sortable table
- Responsive design that works on mobile and desktop
- Customizable person names with localStorage persistence

## Setup

### Local Development

1. Make sure you have Python 3.8+ installed
2. Clone the repository and navigate to the project directory
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy the environment file and modify as needed:
   ```bash
   cp .env.example .env
   ```
6. Run the application:
   ```bash
   python app.py
   ```
7. Open your browser and go to `http://localhost:5000`

### Deployment

This application is configured for deployment on platforms like:
- **Render**: Use the `render.yaml` configuration
- **Railway**: Supports automatic deployment from Git
- **Heroku**: Use the `Procfile` for deployment

For production deployment, consider using PostgreSQL instead of SQLite by setting the `DATABASE_URL` environment variable.

## Usage

1. **Adding an Expense**:
   - Click the "Add Expense" button
   - Fill in the expense details
   - The shares will be automatically calculated equally, but you can modify them
   - Click "Save Expense" to add it to the list

2. **Customizing Names**:
   - Use the "Customize Names" section to set person names
   - Names are saved in browser localStorage and persist across sessions

3. **Viewing Expenses**:
   - All expenses are displayed in a table
   - The current balance is shown at the top
   - Edit or delete expenses using the action buttons

## Environment Variables

- `FLASK_ENV`: Set to `development` for local development
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `PORT`: Port number for the application (defaults to 5000)

## Data Structure

The application uses SQLAlchemy ORM with support for both SQLite (development) and PostgreSQL (production).

## Free Hosting Recommendations

1. **Render** (Recommended): 
   - Free tier with 750 hours/month
   - Automatic deployments from Git
   - Built-in PostgreSQL database

2. **Railway**:
   - $5 credit monthly on free tier
   - Easy deployment process

3. **Heroku**:
   - Free tier discontinued, but still popular for paid hosting