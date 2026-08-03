# Calculator App

A full-stack calculator application featuring a web-based UI and a Python Flask backend with persistent database storage.

## Features
- Basic arithmetic operations (+, -, *, /)
- Advanced functions (square root, power)
- Persistent History tracking (using SQLite/SQLAlchemy)
- REST API

## Local Development

### Prerequisites
- Python 3.8+

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the backend server:
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:8080` and automatically create a local `calculator.db` SQLite database.

4. Open `ui.html` in your browser. Ensure that the `API_BASE_URL` in `ui.html` points to `http://localhost:8080`.

## Database Configuration
By default, the application uses a local SQLite database (`calculator.db`). For production, you can set the `DATABASE_URL` environment variable to connect to PostgreSQL or MySQL.

```bash
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

## Deployment

This application is ready to be deployed to platforms like Render, Heroku, or Azure.

### Deploying to Render
1. Create a [Render](https://render.com/) account.
2. Connect your GitHub repository.
3. Render will automatically detect the `render.yaml` file and configure the web service.
4. Once deployed, update the `API_BASE_URL` in `ui.html` to point to your new Render URL.

### Deploying with Docker
A `Dockerfile` is provided for containerized environments.
```bash
docker build -t calculator-app .
docker run -p 8080:8080 calculator-app
```

### Deploying to Heroku
The provided `Procfile` makes it easy to deploy to Heroku.
```bash
heroku create
git push heroku main
```
