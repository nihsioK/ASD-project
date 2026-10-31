pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE = 'eduai'
    }

    stages {
        stage('Install dependencies') {
            steps {
                sh 'uv sync --locked'
            }
        }

        stage('Lint') {
            steps {
                sh 'uv run ruff check .'
                sh 'uv run ruff format --check .'
            }
        }

        stage('Unit tests') {
            steps {
                sh 'uv run pytest --junitxml=reports/junit.xml --cov=app --cov-report=term --cov-fail-under=90'
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t $IMAGE:$BUILD_NUMBER -t $IMAGE:latest .'
            }
        }

        stage('Deploy to test server') {
            steps {
                sh 'IMAGE_TAG=$BUILD_NUMBER docker compose -f deploy/docker-compose.test.yml up -d'
                // smoke test: the new version must answer before the pipeline is green
                sh 'curl --fail --silent --retry 15 --retry-delay 2 --retry-all-errors http://host.docker.internal:8081/health'
            }
        }
    }

    post {
        success {
            echo "EduAI build ${env.BUILD_NUMBER} is deployed to the test server: http://localhost:8081"
        }
    }
}
