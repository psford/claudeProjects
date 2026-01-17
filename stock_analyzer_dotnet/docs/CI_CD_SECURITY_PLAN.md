# CI/CD Security Migration Plan

## Current State

### Local/Pre-commit Security Tools
| Tool | Type | Coverage |
|------|------|----------|
| **Bandit** | Python SAST | Detects security issues in Python code |
| **detect-secrets** | Secrets detection | Prevents committing secrets/credentials |
| **detect-private-key** | Key detection | Blocks private key commits |
| **SecurityCodeScan.VS2019** | C#/.NET SAST | Analyzer integrated into build |

### CI/CD Security Tools (Current)
- **None explicit** - security happens locally via pre-commit hooks
- SecurityCodeScan runs during `dotnet build` but findings aren't surfaced

---

## Proposed CI/CD Security Pipeline

### Phase 1: GitHub Actions Security (Free tier)

**Add CodeQL Analysis:**
```yaml
# .github/workflows/codeql.yml
name: CodeQL Analysis

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    strategy:
      matrix:
        language: ['csharp', 'python']
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

**Add Dependency Scanning:**
- Enable Dependabot (already available via GitHub settings)
- Configure security alerts and auto-PRs

**Add Secret Scanning:**
- Enable in GitHub repository settings (free for public repos)
- Configure push protection

### Phase 2: Jenkins Security Pipeline

**Add Security Stage to Jenkinsfile:**
```groovy
stage('Security Scan') {
    parallel {
        stage('OWASP Dependency Check') {
            steps {
                sh '''
                    dotnet tool restore
                    dotnet tool run dotnet-owasp --project ${SOLUTION_PATH} --out ./security-reports
                '''
            }
        }
        stage('Python SAST') {
            steps {
                sh '''
                    pip install bandit
                    bandit -r . -f json -o security-reports/bandit.json || true
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'security-reports/**', allowEmptyArchive: true
        }
    }
}
```

### Phase 3: Quality Gates

**GitHub Branch Protection:**
- Require CodeQL to pass before merge
- Require all status checks to pass
- No force pushes to main/master

**Jenkins Quality Gate:**
- Fail build on high/critical vulnerabilities
- Warn on medium vulnerabilities
- Track security debt over time

---

## Implementation Checklist

### GitHub Actions
- [ ] Create `.github/workflows/codeql.yml`
- [ ] Enable Dependabot security updates (Settings > Security)
- [ ] Enable secret scanning (Settings > Security)
- [ ] Configure branch protection rules

### Jenkins
- [ ] Add OWASP Dependency Check stage
- [ ] Add Bandit stage for Python code
- [ ] Configure security report archiving
- [ ] Add quality gate thresholds

### Documentation
- [ ] Update TECHNICAL_SPEC.md with CI/CD security tools
- [ ] Update CI_CD_SETUP.md with security configuration
- [ ] Document how to review security findings

---

## Tool Recommendations

| Tool | Purpose | CI/CD | Cost |
|------|---------|-------|------|
| **CodeQL** | SAST for C#/Python | GitHub Actions | Free (open source) |
| **Dependabot** | Dependency vulnerabilities | GitHub | Free |
| **OWASP Dependency Check** | .NET dependency scan | Jenkins | Free |
| **Bandit** | Python SAST | Both | Free |
| **detect-secrets** | Secrets in code | Pre-commit | Free |
| **Snyk** | Dependencies + containers | Optional | Free tier / Paid |
| **SonarQube** | Code quality + security | Optional | Free tier / Paid |

---

## Security Findings Workflow

1. **Pre-commit**: Blocks commits with secrets/keys
2. **PR Creation**: CodeQL scans code changes
3. **PR Review**: Security findings shown in PR
4. **Merge**: Must pass security checks
5. **Weekly**: Scheduled full codebase scan
6. **Dependabot**: Auto-PRs for vulnerable dependencies

---

## Notes

- SecurityCodeScan.VS2019 is already integrated and runs during build
- CodeQL provides better GitHub integration for C# SAST
- Consider running both for defense-in-depth
- DAST (Dynamic testing) would require deployed environment
- Container scanning needed if/when we containerize the app
