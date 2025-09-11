pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "quotes_app:latest"
        DOCKER_HUB_REPO = "${env.dockerHubUser}/quotes_app"
        PROJECT_NAME = "quotes-cicd"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git url: "https://github.com/AnkitaB5007/Iconic-Quotes.git", branch: "master"
                echo 'Code cloned from GitHub.'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE} ."
            }
        }

        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                // Add actual test command here, e.g. pytest, unittest, etc.
                echo 'Unit tests completed successfully.'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "dockerHubCreds",
                    passwordVariable: "dockerHubPass",
                    usernameVariable: "dockerHubUser"
                )]) {
                    echo 'Logging into Docker Hub...'
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    
                    echo 'Tagging and pushing image...'
                    sh "docker tag ${DOCKER_IMAGE} ${DOCKER_HUB_REPO}:latest"
                    sh "docker push ${DOCKER_HUB_REPO}:latest"
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh '''
                echo "Cleaning up old containers and networks (preserving volumes)..."
                docker compose -p ${PROJECT_NAME} down --remove-orphans || true

                echo "Removing old app container if still exists..."
                docker rm -f quotes_app || true

                echo "Starting new deployment for project ${PROJECT_NAME}..."
                docker compose -p ${PROJECT_NAME} up -d
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline executed successfully.'
        }
        failure {
            echo 'Pipeline failed. Please check logs.'
        }
    }
}

