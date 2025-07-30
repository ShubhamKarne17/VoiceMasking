# Voice Privacy Masking System - Deployment Guide

This guide provides instructions for deploying the Voice Privacy Masking System in different environments.

## 🚀 Quick Deployment

### Local Development Setup

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd voice_masking_system
   python3.11 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install System Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install build-essential portaudio19-dev python3.11-dev
   
   # macOS
   brew install portaudio
   
   # Windows
   # Dependencies are typically included with Python installation
   ```

3. **Setup Frontend**
   ```bash
   cd src/frontend/voice-masking-ui
   npm install
   ```

4. **Start Services**
   ```bash
   # Terminal 1: Backend
   cd src/backend
   source ../../venv/bin/activate
   python api_server.py
   
   # Terminal 2: Frontend
   cd src/frontend/voice-masking-ui
   npm run dev
   ```

5. **Access Application**
   Open `http://localhost:5173` in your browser

## 🐳 Docker Deployment

### Docker Compose (Recommended)

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     backend:
       build:
         context: .
         dockerfile: Dockerfile.backend
       ports:
         - "5000:5000"
       volumes:
         - ./src/backend:/app
       environment:
         - FLASK_ENV=production
       devices:
         - /dev/snd:/dev/snd  # Audio device access
       
     frontend:
       build:
         context: .
         dockerfile: Dockerfile.frontend
       ports:
         - "3000:3000"
       depends_on:
         - backend
       environment:
         - REACT_APP_API_URL=http://localhost:5000
   ```

2. **Create Dockerfile.backend**
   ```dockerfile
   FROM python:3.11-slim
   
   RUN apt-get update && apt-get install -y \
       build-essential \
       portaudio19-dev \
       python3-dev \
       && rm -rf /var/lib/apt/lists/*
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY src/backend/ .
   
   EXPOSE 5000
   CMD ["python", "api_server.py"]
   ```

3. **Create Dockerfile.frontend**
   ```dockerfile
   FROM node:20-alpine
   
   WORKDIR /app
   COPY src/frontend/voice-masking-ui/package*.json ./
   RUN npm install
   
   COPY src/frontend/voice-masking-ui/ .
   RUN npm run build
   
   EXPOSE 3000
   CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
   ```

4. **Deploy**
   ```bash
   docker-compose up -d
   ```

## 🖥️ Desktop Application

### Electron Wrapper

1. **Install Electron**
   ```bash
   cd src/frontend/voice-masking-ui
   npm install electron electron-builder --save-dev
   ```

2. **Create electron-main.js**
   ```javascript
   const { app, BrowserWindow, shell } = require('electron')
   const path = require('path')
   const { spawn } = require('child_process')
   
   let mainWindow
   let backendProcess
   
   function createWindow() {
     mainWindow = new BrowserWindow({
       width: 1200,
       height: 800,
       webPreferences: {
         nodeIntegration: false,
         contextIsolation: true
       }
     })
   
     // Start backend server
     const pythonPath = path.join(__dirname, '../../backend/venv/bin/python')
     const serverPath = path.join(__dirname, '../../backend/api_server.py')
     backendProcess = spawn(pythonPath, [serverPath])
   
     // Load frontend
     mainWindow.loadURL('http://localhost:5173')
   }
   
   app.whenReady().then(createWindow)
   
   app.on('window-all-closed', () => {
     if (backendProcess) {
       backendProcess.kill()
     }
     if (process.platform !== 'darwin') {
       app.quit()
     }
   })
   ```

3. **Update package.json**
   ```json
   {
     "main": "electron-main.js",
     "scripts": {
       "electron": "electron .",
       "electron-dev": "concurrently \"npm run dev\" \"wait-on http://localhost:5173 && electron .\"",
       "build-electron": "npm run build && electron-builder"
     }
   }
   ```

## ☁️ Cloud Deployment

### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t3.medium or larger (for real-time audio processing)
   - Security group: Allow ports 22, 80, 443, 5000, 3000

2. **Setup Instance**
   ```bash
   # Connect to instance
   ssh -i your-key.pem ubuntu@your-instance-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install -y python3.11 python3.11-venv nodejs npm nginx
   sudo apt install -y build-essential portaudio19-dev python3.11-dev
   
   # Clone repository
   git clone <your-repo-url>
   cd voice_masking_system
   
   # Setup Python environment
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Setup frontend
   cd src/frontend/voice-masking-ui
   npm install
   npm run build
   ```

3. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           root /home/ubuntu/voice_masking_system/src/frontend/voice-masking-ui/dist;
           try_files $uri $uri/ /index.html;
       }
   
       location /api/ {
           proxy_pass http://localhost:5000/api/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Create Systemd Services**
   
   Backend service (`/etc/systemd/system/voice-masking-backend.service`):
   ```ini
   [Unit]
   Description=Voice Masking Backend
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/voice_masking_system/src/backend
   Environment=PATH=/home/ubuntu/voice_masking_system/venv/bin
   ExecStart=/home/ubuntu/voice_masking_system/venv/bin/python api_server.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Start Services**
   ```bash
   sudo systemctl enable voice-masking-backend
   sudo systemctl start voice-masking-backend
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

### Heroku Deployment

1. **Create Procfile**
   ```
   web: cd src/backend && python api_server.py
   ```

2. **Create runtime.txt**
   ```
   python-3.11.0
   ```

3. **Deploy**
   ```bash
   heroku create your-app-name
   heroku buildpacks:add heroku/python
   heroku buildpacks:add heroku/nodejs
   git push heroku main
   ```

## 🔧 Production Configuration

### Environment Variables

```bash
# Backend
export FLASK_ENV=production
export FLASK_DEBUG=False
export API_HOST=0.0.0.0
export API_PORT=5000

# Frontend
export REACT_APP_API_URL=https://your-api-domain.com
export NODE_ENV=production
```

### Security Considerations

1. **HTTPS Configuration**
   ```bash
   # Install SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

2. **Firewall Setup**
   ```bash
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

3. **Rate Limiting**
   Add to Nginx configuration:
   ```nginx
   limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
   
   location /api/ {
       limit_req zone=api burst=20 nodelay;
       # ... other config
   }
   ```

### Performance Optimization

1. **Audio Processing**
   - Use dedicated audio hardware for best performance
   - Adjust buffer sizes based on system capabilities
   - Monitor CPU usage and memory consumption

2. **Frontend Optimization**
   ```bash
   # Build optimized frontend
   npm run build
   
   # Enable gzip compression in Nginx
   gzip on;
   gzip_types text/css application/javascript application/json;
   ```

3. **Database (if needed)**
   ```bash
   # For user profiles and settings
   sudo apt install postgresql
   # Configure database connection in backend
   ```

## 📊 Monitoring & Logging

### Application Monitoring

1. **Backend Logging**
   ```python
   import logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('/var/log/voice-masking/backend.log'),
           logging.StreamHandler()
       ]
   )
   ```

2. **System Monitoring**
   ```bash
   # Install monitoring tools
   sudo apt install htop iotop nethogs
   
   # Monitor audio processing
   watch -n 1 'ps aux | grep python | grep -v grep'
   ```

### Health Checks

1. **Backend Health Check**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Frontend Health Check**
   ```bash
   curl http://localhost:3000
   ```

## 🔄 Updates & Maintenance

### Automated Updates

1. **Create Update Script**
   ```bash
   #!/bin/bash
   cd /home/ubuntu/voice_masking_system
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt
   cd src/frontend/voice-masking-ui
   npm install
   npm run build
   sudo systemctl restart voice-masking-backend
   sudo systemctl reload nginx
   ```

2. **Schedule Updates**
   ```bash
   # Add to crontab
   0 2 * * 0 /home/ubuntu/update-voice-masking.sh
   ```

### Backup Strategy

1. **Configuration Backup**
   ```bash
   # Backup important files
   tar -czf voice-masking-backup-$(date +%Y%m%d).tar.gz \
       /home/ubuntu/voice_masking_system \
       /etc/nginx/sites-available/default \
       /etc/systemd/system/voice-masking-backend.service
   ```

2. **Automated Backups**
   ```bash
   # Daily backup script
   #!/bin/bash
   BACKUP_DIR="/home/ubuntu/backups"
   DATE=$(date +%Y%m%d)
   tar -czf "$BACKUP_DIR/voice-masking-$DATE.tar.gz" \
       /home/ubuntu/voice_masking_system
   # Keep only last 7 days
   find "$BACKUP_DIR" -name "voice-masking-*.tar.gz" -mtime +7 -delete
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Audio Device Access**
   ```bash
   # Check audio devices
   aplay -l
   arecord -l
   
   # Fix permissions
   sudo usermod -a -G audio $USER
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   sudo netstat -tlnp | grep :5000
   
   # Kill conflicting processes
   sudo fuser -k 5000/tcp
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   free -h
   
   # Adjust audio buffer sizes
   # Edit audio_processor.py
   ```

### Log Analysis

```bash
# Backend logs
tail -f /var/log/voice-masking/backend.log

# System logs
journalctl -u voice-masking-backend -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

For additional support, refer to the main README.md or create an issue in the repository.

