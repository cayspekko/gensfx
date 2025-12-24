# SoundForge Deployment Guide

This guide covers various deployment options for SoundForge.

## Local Development

### Quick Start
```bash
# Clone and setup
git clone <repo-url>
cd gensfx
pip install -r requirements.txt

# Run
streamlit run app.py
```

### With Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud

### Setup
1. Push your repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository and branch
5. Set main file path: `app.py`
6. Click "Deploy"

### Secrets Configuration
Add your OpenAI API key in Streamlit Cloud:

1. Go to your app settings
2. Click "Secrets"
3. Add:
```toml
OPENAI_API_KEY = "sk-your-key-here"
```

### Custom Domain (Optional)
1. Go to app settings
2. Click "Custom domain"
3. Follow instructions to configure DNS

## Docker Deployment

### Build Image
```bash
docker build -t soundforge:latest .
```

### Run Container
```bash
# Without OpenAI API
docker run -p 8501:8501 soundforge:latest

# With OpenAI API
docker run -p 8501:8501 \
  -e OPENAI_API_KEY="sk-your-key-here" \
  soundforge:latest
```

### Docker Compose
Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  soundforge:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

## AWS Deployment

### AWS App Runner

1. **Push to ECR**:
```bash
aws ecr create-repository --repository-name soundforge
docker tag soundforge:latest <account-id>.dkr.ecr.<region>.amazonaws.com/soundforge:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/soundforge:latest
```

2. **Create App Runner Service**:
```bash
aws apprunner create-service \
  --service-name soundforge \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<account-id>.dkr.ecr.<region>.amazonaws.com/soundforge:latest",
      "ImageRepositoryType": "ECR"
    }
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }'
```

### AWS ECS (Fargate)

1. Create task definition
2. Create ECS cluster
3. Create service with load balancer
4. Configure environment variables

See AWS documentation for detailed steps.

## Google Cloud Run

### Deploy
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/soundforge

# Deploy
gcloud run deploy soundforge \
  --image gcr.io/PROJECT-ID/soundforge \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="sk-your-key-here"
```

## Heroku

### Setup
```bash
# Login
heroku login

# Create app
heroku create soundforge-app

# Set environment variables
heroku config:set OPENAI_API_KEY="sk-your-key-here"

# Deploy
git push heroku main
```

### Procfile
Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

## Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name soundforge \
  --image soundforge:latest \
  --dns-name-label soundforge \
  --ports 8501 \
  --environment-variables OPENAI_API_KEY="sk-your-key-here"
```

## Kubernetes

### Deployment YAML
Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: soundforge
spec:
  replicas: 2
  selector:
    matchLabels:
      app: soundforge
  template:
    metadata:
      labels:
        app: soundforge
    spec:
      containers:
      - name: soundforge
        image: soundforge:latest
        ports:
        - containerPort: 8501
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: soundforge-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: soundforge-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8501
  selector:
    app: soundforge
```

Deploy:
```bash
kubectl create secret generic soundforge-secrets \
  --from-literal=openai-api-key="sk-your-key-here"

kubectl apply -f k8s-deployment.yaml
```

## Environment Variables

### Required
None - app works without OpenAI API key (uses mock generator)

### Optional
- `OPENAI_API_KEY`: OpenAI API key for AI-powered generation

### Configuration
Set via:
- `.env` file (local development)
- Environment variables (Docker, cloud platforms)
- Secrets management (Kubernetes, cloud services)

## Performance Tuning

### Streamlit Configuration
Create `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 10
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Resource Limits
- **CPU**: 1 vCPU minimum, 2 vCPU recommended
- **Memory**: 512MB minimum, 1GB recommended
- **Storage**: 1GB minimum

### Scaling
- Horizontal scaling supported (stateless app)
- Session state stored in browser
- No database required

## Monitoring

### Health Check Endpoint
Streamlit provides: `http://localhost:8501/_stcore/health`

### Logging
Logs are written to stdout/stderr. Configure log aggregation:
- CloudWatch (AWS)
- Cloud Logging (GCP)
- Application Insights (Azure)
- ELK Stack (self-hosted)

### Metrics
Monitor:
- Request count
- Response time
- Error rate
- Memory usage
- CPU usage

## Security

### HTTPS
- Use reverse proxy (nginx, Caddy)
- Or cloud platform SSL/TLS termination

### API Key Protection
- Never commit API keys to git
- Use secrets management
- Rotate keys regularly

### Rate Limiting
Implement at reverse proxy or cloud platform level

### CORS
Configure in `.streamlit/config.toml` if needed

## Troubleshooting

### Port Already in Use
```bash
# Find process
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run app.py --server.port=8502
```

### Memory Issues
- Reduce max audio duration
- Implement caching
- Scale horizontally

### OpenAI API Errors
- Check API key validity
- Verify API quota
- App falls back to mock generator automatically

## Backup and Recovery

### What to Backup
- Source code (in git)
- Environment variables (in secrets manager)
- User-generated SoundSpecs (if storing)

### Disaster Recovery
- Code: Restore from git
- Config: Restore from secrets manager
- Redeploy using same process

## Cost Optimization

### Streamlit Cloud
- Free tier available
- Paid plans for custom domains and resources

### Cloud Platforms
- Use spot/preemptible instances
- Auto-scaling based on traffic
- Serverless options (Cloud Run, App Runner)

### OpenAI API
- Monitor usage
- Set spending limits
- Cache common generations (optional)

## Support

For deployment issues:
1. Check logs
2. Verify environment variables
3. Test locally first
4. Open GitHub issue with details

---

**Happy deploying! 🚀**
