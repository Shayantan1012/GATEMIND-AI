# Deploy GATEMIND Backend Directly to EC2

This deployment uses one EC2 instance and Docker Compose. Terraform, ECS, ECR, and a load balancer are not required.

## 1. Create the EC2 Instance

In the AWS console:

1. Open **EC2 -> Launch instance**.
2. Name it `gatemind-backend`.
3. Select **Amazon Linux 2023**.
4. Select `t3.small`. Use `t3.micro` only for light testing.
5. Create and download an RSA `.pem` key pair.
6. Configure at least 30 GB gp3 storage.
7. Allow inbound:
   - SSH `22` from **My IP**
   - HTTP `80` from `0.0.0.0/0`
   - HTTPS `443` from `0.0.0.0/0` when HTTPS is configured
8. Launch the instance.
9. Allocate and associate an Elastic IP so the backend address does not change.

### Allocate and Associate an Elastic IP

An Elastic IP keeps the backend public IP stable when the EC2 instance is stopped and started.

1. Open **AWS Console -> EC2 -> Network & Security -> Elastic IP addresses**.
2. Select **Allocate Elastic IP address**.
3. Keep **Amazon's pool of IPv4 addresses** selected, then choose **Allocate**.
4. Select the newly allocated Elastic IP.
5. Choose **Actions -> Associate Elastic IP address**.
6. For **Resource type**, select **Instance**.
7. Select the GATEMIND backend EC2 instance.
8. Select its private IP address, then choose **Associate**.
9. Copy the Elastic IP and use it as `EC2_HOST` in GitHub Actions.

After associating it:

- Add `ELASTIC_IP/32` to MongoDB Atlas Network Access.
- Point the backend domain's DNS `A` record to the Elastic IP.
- Test the backend at `http://ELASTIC_IP/api/health`.

AWS charges for public IPv4 addresses, including Elastic IPs. Release an Elastic IP after it is no longer needed:

1. Select it under **Elastic IP addresses**.
2. Choose **Actions -> Disassociate Elastic IP address**.
3. Choose **Actions -> Release Elastic IP addresses**.

## 2. Connect to EC2

From PowerShell:

```powershell
ssh -i "C:\path\to\gatemind.pem" ec2-user@YOUR_EC2_ELASTIC_IP
```

If Windows reports that the private key permissions are too open:

```powershell
$key = "C:\path\to\gatemind.pem"
icacls $key /inheritance:r
icacls $key /grant:r "$($env:USERNAME):(R)"
```

Never commit or share the private key. If it is exposed, create a replacement key, add its public key to `~/.ssh/authorized_keys`, update the GitHub secret, verify the new key, and remove the old key.

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
HUGGINGFACE_API_KEY=your-huggingface-key-if-used
HF_TOKEN=your-huggingface-key-if-used
OTP_PREVIEW_ENABLED=false
```

Set `OTP_PREVIEW_ENABLED=true` only while SMS delivery is unavailable. It returns OTPs to the requesting frontend and must be disabled after Twilio is configured.

Pending OTPs are stored in the running backend process for ten minutes. A container restart or deployment invalidates pending OTPs.

The container port is fixed to `5000` by `docker-compose.prod.yml`; do not add `PORT` to this environment file.

Protect the environment file:

```bash
sudo chmod 600 /opt/gatemind/backend.env
```

## 5. Configure MongoDB Atlas

Add the EC2 Elastic IP followed by `/32` under:

```text
MongoDB Atlas -> Security -> Network Access
```

## 6. Configure GitHub Actions

Open:

```text
GitHub repository -> Settings -> Secrets and variables -> Actions
```

Add repository secrets:

- `EC2_HOST`: EC2 Elastic IP
- `EC2_SSH_PRIVATE_KEY`: complete contents of the private SSH key

Add repository variable:

- `EC2_USER`: `ec2-user`

Secret names contain only letters, numbers, and underscores. Do not include `=`, spaces, or quotes in their names.

## 7. Deploy

Commit and push to `main`. Backend CI runs first. After it passes, GitHub Actions copies the backend to EC2 and rebuilds the Docker container.

You can also manually run:

```text
GitHub repository -> Actions -> Deploy Backend to EC2 -> Run workflow
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

## Connect the Vercel Frontend

The frontend uses relative `/api` requests. `frontend/vercel.json` proxies those requests from Vercel to EC2, avoiding browser mixed-content errors while the backend uses HTTP.

Update the proxy destination whenever the Elastic IP changes:

```json
{
  "source": "/api/:path*",
  "destination": "http://YOUR_EC2_ELASTIC_IP/api/:path*"
}
```

Do not set `VITE_API_BASE_URL` in Vercel while using this proxy. After changing `frontend/vercel.json`, push the change and let Vercel redeploy.

When a backend HTTPS domain is available, set:

```text
VITE_API_BASE_URL=https://api.your-domain.example
```

Then the frontend can call the backend domain directly.

## HTTPS

This basic setup uses HTTP. Before handling production users:

1. Point a backend domain such as `api.your-domain.example` to the Elastic IP.
2. Bind the Docker port to localhost instead of exposing it publicly.
3. Install Nginx and configure it as a reverse proxy to `127.0.0.1:5000`.
4. Install a Let's Encrypt certificate with Certbot.
5. Change the Vercel API URL to the HTTPS backend domain.
6. Set `ALLOWED_ORIGINS` to the exact Vercel production URL.

## Useful EC2 Commands

```bash
sudo systemctl status docker --no-pager
sudo docker ps -a
sudo docker logs --tail 300 gatemind-backend
sudo docker compose -f /opt/gatemind/source/backend/docker-compose.prod.yml restart
curl http://127.0.0.1/api/health
```

Uploaded documents remain under `/opt/gatemind/uploads` across container deployments.

Confirm an environment variable exists without displaying its value:

```bash
sudo docker exec gatemind-backend sh -c 'test -n "$MONGO_URI" && echo MONGO_URI=SET || echo MONGO_URI=MISSING'
```

Check whether OTP preview mode reached the container:

```bash
sudo docker exec gatemind-backend printenv OTP_PREVIEW_ENABLED
```

If GitHub Actions deployment fails, open the **Show backend diagnostics** step. It prints Docker status, health information, and recent application logs.
