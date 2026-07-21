# Simple EC2 Backend Deployment

This is a personal-project deployment. It uses:

- One EC2 instance
- Docker Compose
- GitHub Actions
- No Terraform, ECR, ECS, load balancer, or production HTTPS setup

## 1. EC2 Setup

Create an EC2 instance:

- AMI: Amazon Linux 2023
- Instance type: `t3.small`
- Storage: 30 GB
- Key pair: create/download `.pem`
- Security group:
  - SSH `22` from **My IP**
  - HTTP `80` from `0.0.0.0/0`

Use an Elastic IP if you do not want the backend IP to change after restart.

### Add an Elastic IP

Elastic IP means a fixed public IP for your EC2 instance. Use this if you want GitHub Actions, MongoDB Atlas, and Vercel to keep using the same backend IP.

1. Go to **AWS Console -> EC2**.
2. In the left menu, open **Elastic IPs**.
3. Click **Allocate Elastic IP address**.
4. Keep the default option selected.
5. Click **Allocate**.
6. Select the new Elastic IP.
7. Click **Actions -> Associate Elastic IP address**.
8. For **Resource type**, choose **Instance**.
9. Select your GATEMIND EC2 instance.
10. Select the private IP shown for that instance.
11. Click **Associate**.

After this, copy the Elastic IP and use it in these places:

- GitHub Actions secret `EC2_HOST`
- MongoDB Atlas Network Access as `YOUR_ELASTIC_IP/32`
- `frontend/vercel.json` proxy URL
- Browser test URL: `http://YOUR_ELASTIC_IP/api/health`

If you delete the EC2 instance later, release the Elastic IP too, otherwise AWS may still charge for it:

1. EC2 -> **Elastic IPs**
2. Select the Elastic IP
3. **Actions -> Disassociate Elastic IP address**
4. **Actions -> Release Elastic IP addresses**

## 2. Connect to EC2

From PowerShell:

```powershell
ssh -i "C:\path\to\gatemind.pem" ec2-user@YOUR_EC2_IP
```

If Windows says the key permissions are too open:

```powershell
$key = "C:\path\to\gatemind.pem"
icacls $key /inheritance:r
icacls $key /grant:r "$($env:USERNAME):(R)"
```

## 3. Run These EC2 Commands Before the Env File

After SSH login, run this full block on EC2. It installs Docker, Docker Compose, Docker Buildx, starts Docker, and creates the upload folder.

```bash
sudo dnf update -y
sudo dnf install -y docker
sudo systemctl enable --now docker

sudo mkdir -p /usr/local/lib/docker/cli-plugins

sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose

sudo curl -SL https://github.com/docker/buildx/releases/download/v0.20.1/buildx-v0.20.1.linux-amd64 \
  -o /usr/local/lib/docker/cli-plugins/docker-buildx

sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx

sudo mkdir -p /opt/gatemind/uploads

sudo docker version
sudo docker compose version
sudo docker buildx version
```

If all three version commands print successfully, EC2 is ready for the backend env file.

## 4. Create Backend Environment File

On EC2:

```bash
sudo nano /opt/gatemind/backend.env
```

Example:

```env
APP_ENV=production
SECRET_KEY=replace-with-any-long-random-text
MONGO_URI=your-mongodb-atlas-url
MONGO_DB_NAME=gatemind
MONGO_USE_MOCK=false
UPLOAD_FOLDER=/app/uploads
ENABLE_FILE_LOGGING=false
ALLOWED_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
GROQ_API_KEY=your-groq-key
GROQ_MODEL=llama-3.3-70b-versatile
HUGGINGFACE_API_KEY=your-huggingface-key
HF_TOKEN=your-huggingface-key
OTP_PREVIEW_ENABLED=true
```

Save with `Ctrl+O`, Enter, then `Ctrl+X`.

## 5. MongoDB Atlas

In MongoDB Atlas, allow your EC2 IP:

```text
YOUR_EC2_IP/32
```

## 6. GitHub Secrets

GitHub repo -> Settings -> Secrets and variables -> Actions

Repository secrets:

```text
EC2_HOST = your EC2 public/elastic IP
EC2_SSH_PRIVATE_KEY = full content of your .pem file
```

Repository variable:

```text
EC2_USER = ec2-user
```

## 7. Deploy

Push to `main`.

GitHub Actions will:

1. Run backend tests
2. Copy the backend folder to EC2
3. Run Docker Compose on EC2
4. Check `/api/health`

You can also run it manually:

```text
GitHub -> Actions -> Deploy Backend to EC2 -> Run workflow
```

## 8. Test

Open:

```text
http://YOUR_EC2_IP/api/health
```

Expected:

```json
{
  "status": "ok",
  "service": "gatemind-backend"
}
```

## Useful Commands

On EC2:

```bash
sudo docker ps
sudo docker logs --tail 100 gatemind-backend
sudo docker compose -f /opt/gatemind/source/backend/docker-compose.prod.yml restart
```

## Frontend on Vercel

For the current simple setup, `frontend/vercel.json` proxies:

```text
/api/* -> http://YOUR_EC2_IP/api/*
```

If your EC2 IP changes, update `frontend/vercel.json` and redeploy Vercel.
CHANGED EC2
