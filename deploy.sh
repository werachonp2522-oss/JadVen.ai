#!/bin/bash
# ==========================================================
#  JadVen.ai - Linux Deployment Script
#  Server: 10.0.100.147
#  Usage: bash deploy.sh
# ==========================================================
set -e

echo ""
echo "=========================================="
echo "  JadVen.ai - Production Deployment"
echo "  Server: $(hostname) / 10.0.100.147"
echo "=========================================="
echo ""

# ---------- Config ----------
APP_DIR="/opt/jadven"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
PYTHON_BIN="python3"
NODE_BIN="node"

# ---------- Step 1: Install system dependencies ----------
echo "[1/7] Installing system dependencies..."
sudo apt-get update -qq || true
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm nginx -qq || true

# ---------- Step 2: Copy project ----------
echo "[2/7] Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo cp -r . $APP_DIR/
sudo chown -R $USER:$USER $APP_DIR

# ---------- Step 3: Backend setup ----------
echo "[3/7] Setting up Python backend..."
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Create production .env if not exists
if [ ! -f .env ]; then
  cat > .env << 'EOF'
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:///./jadven.db
EOF
  echo "  ⚠️  Created .env — please edit GEMINI_API_KEY!"
else
  # If .env exists but doesn't have SECRET_KEY, append it
  if ! grep -q "SECRET_KEY" .env; then
    echo "SECRET_KEY=$(python3 -c \"import secrets; print(secrets.token_hex(32))\")" >> .env
    echo "  ✅ Appended SECRET_KEY to existing .env"
  fi
fi

# Run database migrations and seed
python3 seed_db.py
echo "  ✅ Database seeded"

# ---------- Step 4: Frontend build ----------
echo "[4/7] Building Next.js frontend..."
cd $FRONTEND_DIR
npm install --silent
npm run build
echo "  ✅ Frontend built"

# ---------- Step 5: Install systemd services ----------
echo "[5/7] Installing systemd services..."

sudo tee /etc/systemd/system/jadven-backend.service > /dev/null << EOF
[Unit]
Description=JadVen.ai FastAPI Backend
After=network.target

[Service]
User=$USER
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
ExecStart=$BACKEND_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/jadven-frontend.service > /dev/null << EOF
[Unit]
Description=JadVen.ai Next.js Frontend
After=network.target jadven-backend.service

[Service]
User=$USER
WorkingDirectory=$FRONTEND_DIR
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# ---------- Step 6: Start services ----------
echo "[6/7] Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable jadven-backend jadven-frontend
sudo systemctl restart jadven-backend jadven-frontend

# ---------- Step 7: Configure nginx ----------
echo "[7/7] Configuring Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/jadven > /dev/null << 'EOF'
server {
    listen 80;
    server_name 10.0.100.147;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/jadven /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo ""
echo "=========================================="
echo "  ✅ Deploy สำเร็จ!"
echo "  เข้าใช้งานที่: http://10.0.100.147"
echo "  API Docs:      http://10.0.100.147/api/docs"
echo "=========================================="
echo ""
echo "📋 คำสั่งที่ใช้บ่อย:"
echo "  sudo systemctl status jadven-backend"
echo "  sudo systemctl status jadven-frontend"
echo "  sudo journalctl -u jadven-backend -f   # ดู logs"
