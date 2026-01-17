# CI/CD Setup Documentation

This project has two CI/CD systems configured: **GitHub Actions** (cloud-based) and **Jenkins** (local Docker).

---

## GitHub Actions

### Overview
- **Location**: `.github/workflows/dotnet-ci.yml`
- **Trigger**: Push or PR to `master` branch (when `stock_analyzer_dotnet/**` changes)
- **Runners**: Ubuntu (primary) + Windows (verification)
- **Dashboard**: https://github.com/psford/claudeProjects/actions

### Workflow Stages
1. **Checkout** - Clone repository
2. **Setup .NET** - Install .NET 8.0 SDK
3. **Restore** - Restore NuGet packages
4. **Build** - Build solution in Release mode
5. **Test** - Run unit tests, upload results as artifacts

### Manual Trigger
The workflow supports `workflow_dispatch` for manual runs:
1. Go to Actions tab in GitHub
2. Select ".NET CI" workflow
3. Click "Run workflow"

### Configuration
```yaml
env:
  DOTNET_VERSION: '8.0.x'
  SOLUTION_PATH: 'stock_analyzer_dotnet/StockAnalyzer.sln'
```

---

## Jenkins (Local Docker)

### Overview
- **Container**: `jenkins/jenkins:lts` with Docker-in-Docker
- **URL**: http://localhost:8080
- **Job**: `StockAnalyzer`
- **Credentials**: Stored in `.env` file

### Prerequisites
- Docker Desktop running
- Port 8080 available

### Starting Jenkins
```bash
# Start Jenkins container
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# Install Docker CLI inside Jenkins (run once after container creation)
docker exec -u root jenkins apt-get update
docker exec -u root jenkins apt-get install -y docker.io

# Fix Docker socket permissions
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

### Stopping Jenkins
```bash
docker stop jenkins
```

### Restarting Jenkins
```bash
docker start jenkins
# Remember to fix Docker socket permissions after restart:
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

### Pipeline Stages (Jenkinsfile)
1. **Checkout** - Clone from GitHub using PAT credentials
2. **Restore** - `dotnet restore`
3. **Build** - `dotnet build --configuration Release`
4. **Test** - `dotnet test` with TRX output, archives results
5. **Publish** - `dotnet publish`, archives artifacts with fingerprints

### Triggering Builds

**Via UI:**
1. Go to http://localhost:8080/job/StockAnalyzer/
2. Click "Build Now"

**Via CLI:**
```bash
# Get crumb and trigger build
docker exec jenkins bash -c '
  CRUMB=$(curl -s -u "psford:psford" "http://localhost:8080/crumbIssuer/api/json" | sed "s/.*crumb\":\"//;s/\".*//")
  curl -X POST "http://localhost:8080/job/StockAnalyzer/build" \
    -u "psford:psford" \
    -H "Jenkins-Crumb: $CRUMB"
'
```

### Checking Build Status
```bash
# Check latest build status
docker exec jenkins curl -s -u "psford:psford" \
  "http://localhost:8080/job/StockAnalyzer/lastBuild/api/json?tree=result,building,number"
```

### Credentials
Jenkins credentials are stored in:
- **GitHub PAT**: Credential ID `github-pat` (for private repo access)
- **Jenkins login**: See `.env` file (`JENKINS_USER`, `JENKINS_PASSWORD`)

### Installed Plugins
- `docker-workflow` - Docker Pipeline support
- `docker-plugin` - Docker integration
- `git` - Git SCM
- `workflow-aggregator` - Pipeline support

---

## Comparison

| Feature | GitHub Actions | Jenkins |
|---------|---------------|---------|
| **Hosting** | Cloud (GitHub) | Local (Docker) |
| **Cost** | Free (2000 min/month) | Free (self-hosted) |
| **Config File** | `.github/workflows/*.yml` | `Jenkinsfile` |
| **Trigger** | Automatic on push/PR | Manual or webhook |
| **Build Environment** | GitHub runners | Docker containers |
| **Artifacts** | GitHub Artifacts | Jenkins Artifacts |
| **Learning Curve** | Lower (YAML) | Higher (Groovy DSL) |

---

## Troubleshooting

### GitHub Actions
- **Build not triggering**: Check if path filter matches changed files
- **Permission denied**: Verify GitHub token has correct scopes

### Jenkins
- **Docker permission denied**: Run `docker exec -u root jenkins chmod 666 /var/run/docker.sock`
- **Workspace cleanup fails**: Files created by Docker have root ownership; clean manually:
  ```bash
  docker exec -u root jenkins rm -rf /var/jenkins_home/workspace/StockAnalyzer
  ```
- **Git auth fails**: Verify `github-pat` credential is configured correctly
- **Container not starting**: Ensure Docker Desktop is running and port 8080 is free

---

## Files

| File | Purpose |
|------|---------|
| `.github/workflows/dotnet-ci.yml` | GitHub Actions workflow |
| `Jenkinsfile` | Jenkins pipeline definition |
| `.env` | Jenkins credentials (gitignored) |

---

*Last updated: 2026-01-17*
