pipeline {
    agent any 

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'  
        DOCKER_IMAGE = 'cithit/valachmr'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/valachmr/225-lab3-9.git'
        KUBECONFIG = credentials('valachmr-225-sp26')                        
    }

    stages {
        stage('Checkout') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
            }
        }

        stage('Diagnose Python') {
            steps {
                sh '''
                    which python || echo "python not found"
                    which python3 || echo "python3 not found"
                    which pip || echo "pip not found"
                    which pip3 || echo "pip3 not found"
                    python3 --version || echo "python3 version failed"
                    python3 -m pip --version || echo "python3 -m pip failed"
                '''
            }
        }

        stage('Install Dependencies') {                  // ADDED
            steps {
                sh '''
                    pip3 install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    python3 -m pytest tests/ --tb=short -v
                '''
            }
        }

        stage('Security Scan - Bandit') {
            steps {
                sh '''
                    python3 -m bandit -r main.py -f txt -o bandit-report.txt || true
                    cat bandit-report.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.txt', fingerprint: true
                }
            }
        }

        stage('Dependency Vulnerability Scan - Safety') {
            steps {
                sh '''
                    python3 -m safety check -r requirements.txt --output text || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://registry-1.docker.io', 'roseaw-dockerhub') {
                        docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}")
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDENTIALS_ID}") {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                script {
                    def kubeConfig = readFile(KUBECONFIG)
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                }
            }
        }
        
        stage('Check Kubernetes Cluster') {
            steps {
                script {
                    sh "kubectl get all"
                }
            }
        }
    }

    post {
        success {
            slackSend color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            slackSend color: "warning", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}