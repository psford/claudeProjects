pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/dotnet/sdk:8.0'
            args '-u root'  // Required for file permissions in Docker
        }
    }

    environment {
        DOTNET_CLI_TELEMETRY_OPTOUT = '1'
        DOTNET_NOLOGO = '1'
        SOLUTION_PATH = 'stock_analyzer_dotnet/StockAnalyzer.sln'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Restore') {
            steps {
                sh 'dotnet restore ${SOLUTION_PATH}'
            }
        }

        stage('Build') {
            steps {
                sh 'dotnet build ${SOLUTION_PATH} --configuration Release --no-restore'
            }
        }

        stage('Test') {
            steps {
                sh 'dotnet test ${SOLUTION_PATH} --configuration Release --no-build --logger "trx;LogFileName=test-results.trx" --results-directory ./TestResults'
            }
            post {
                always {
                    // Archive test results
                    archiveArtifacts artifacts: 'TestResults/*.trx', allowEmptyArchive: true
                }
            }
        }

        stage('Publish') {
            steps {
                sh 'dotnet publish stock_analyzer_dotnet/src/StockAnalyzer.Api/StockAnalyzer.Api.csproj --configuration Release --no-build --output ./publish'
            }
            post {
                success {
                    archiveArtifacts artifacts: 'publish/**', fingerprint: true
                }
            }
        }
    }

    post {
        success {
            echo 'Build succeeded!'
        }
        failure {
            echo 'Build failed!'
        }
    }
}
