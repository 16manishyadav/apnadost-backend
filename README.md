# ApnaDost Backend

A FastAPI-based backend for the ApnaDost mental health chatbot application.

## Features

- FastAPI REST API
- Firebase Authentication
- Google Gemini AI Integration
- Firestore Database
- Docker Support
- Render Deployment Ready

## Prerequisites

- Python 3.11+
- Docker (optional)
- Firebase Project
- Google Gemini API Key

## Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type": "service_account", ...}
```

## Local Development

### Without Docker

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn main:app --reload
```

### With Docker

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Or build and run manually:
```bash
docker build -t apnadost-backend .
docker run -p 8000:8000 --env-file .env apnadost-backend
```

## API Endpoints

- `GET /` - Health check
- `POST /api/chat` - Chat with AI companion

## Docker Deployment

### Build Docker Image

```bash
docker build -t apnadost-backend .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e GEMINI_API_URL=your_url \
  -e GOOGLE_APPLICATION_CREDENTIALS_JSON=your_json \
  apnadost-backend
```

## Render Deployment

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Connect your GitHub repository to Render
3. Render will automatically detect the `render.yaml` file
4. Set environment variables in Render dashboard

### Option 2: Manual Setup

1. Create a new Web Service in Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard

### Environment Variables in Render

Add these environment variables in your Render service:

- `GEMINI_API_KEY`
- `GEMINI_API_URL`
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`

## CI/CD with GitHub Actions

The repository includes a GitHub Actions workflow that:

1. Runs tests on pull requests
2. Deploys to Render on main branch pushes
3. Requires `RENDER_TOKEN` and `RENDER_SERVICE_ID` secrets

### Setting up GitHub Secrets

1. Go to your GitHub repository settings
2. Navigate to Secrets and variables > Actions
3. Add these secrets:
   - `RENDER_TOKEN`: Your Render API token
   - `RENDER_SERVICE_ID`: Your Render service ID

## Health Checks

The application includes health checks:

- Docker: `curl -f http://localhost:8000/`
- Render: Automatic health checks

## Security Considerations

- Uses non-root user in Docker container
- Environment variables for sensitive data
- CORS configured for production
- Firebase token verification

## Troubleshooting

### Common Issues

1. **Port already in use**: Change port in docker-compose.yml or use different port
2. **Environment variables not set**: Ensure all required env vars are configured
3. **Firebase credentials**: Make sure GOOGLE_APPLICATION_CREDENTIALS_JSON is properly formatted

### Logs

View logs with:
```bash
# Docker
docker logs <container_id>

# Render
# Check logs in Render dashboard
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Your License Here] 