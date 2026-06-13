# Deploy GATEMIND Backend Directly to EC2

This deployment uses one EC2 instance and Docker Compose. Terraform, ECS, ECR, and a load balancer are not required.

## 1. Create the EC2 Instance

In the AWS console:

1. Open **EC2 → Launch instance**.
2. Name it `gatemind-backend`.
3. Select **Amazon Linux 2023**.
4. Select `t3.small`. Use `t3.micro` only for light testing.
5. Create and download an RSA `.pem` key pair.
6. Configure at least 30 GB gp3 storage.
7. Allow inbound:
   - SSH `22` from **My IP**
   - HTTP `80` from `0.0.0.0/0`
8. Launch the instance.
9. Allocate and associate an Elastic IP so the backend address does not change.

## 2. Connect to EC2

From PowerShell:

```powershell
ssh -i "C:\path\to\gatemind.pem" ec2-user@YOUR_EC2_PUBLIC_IP
```

## 3. Install Docker on EC2

Run inside EC2:

```bash
sudo dnf update -y
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
sudo mkdir -p /opt/gatemind/uploads
sudo chown -R 999:999 /opt/gatemind/uploads
```

Confirm Docker Compose is available:

```bash
sudo docker compose version
```

If it is unavailable:

```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

Install a compatible Docker Buildx plugin:

```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/buildx/releases/download/v0.20.1/buildx-v0.20.1.linux-amd64 \
  -o /usr/local/lib/docker/cli-plugins/docker-buildx
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx
sudo docker buildx version
```

## 4. Create the Production Environment File

On EC2:

```bash
sudo nano /opt/gatemind/backend.env
```

Add:

```env
APP_ENV=production
SECRET_KEY=replace-with-a-long-random-secret
MONGO_URI=your-mongodb-atlas-connection-string
MONGO_DB_NAME=gatemind
MONGO_USE_MOCK=false
UPLOAD_FOLDER=/app/uploads
ENABLE_FILE_LOGGING=false
ALLOWED_ORIGINS=https://your-frontend-domain.example
GROQ_API_KEY=your-groq-key-if-used
```

The container port is fixed to `5000` by `docker-compose.prod.yml`; do not add
`PORT` to this environment file.

Protect it:

```bash
sudo chmod 600 /opt/gatemind/backend.env
```

## 5. Configure MongoDB Atlas

Add the EC2 Elastic IP followed by `/32` under:

```text
MongoDB Atlas → Security → Network Access
```

## 6. Configure GitHub Actions

Open:

```text
GitHub repository → Settings → Secrets and variables → Actions
```

Add repository secrets:

- `EC2_HOST`: EC2 Elastic IP
- `EC2_SSH_PRIVATE_KEY`: complete contents of the downloaded `.pem` file

Add repository variable:

- `EC2_USER`: `ec2-user`

## 7. Deploy

Commit and push to `main`. Backend CI runs first. After it passes, GitHub Actions copies the backend to EC2 and rebuilds the Docker container.

You can also manually run:

```text
GitHub repository → Actions → Deploy Backend to EC2 → Run workflow
```

## 8. Verify

Open:

```text
http://YOUR_EC2_ELASTIC_IP/api/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "gatemind-backend"
}
```

## Useful EC2 Commands

```bash
sudo docker ps
sudo docker logs --tail 100 gatemind-backend
sudo docker compose -f /opt/gatemind/source/backend/docker-compose.prod.yml restart
```

Uploaded documents remain under `/opt/gatemind/uploads` across container deployments.

## HTTPS

This basic setup uses HTTP. Before handling production users, configure a domain with Nginx and Let’s Encrypt or add an AWS load balancer later.
