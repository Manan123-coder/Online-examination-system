// Jenkins reads this file and runs the stages automatically on every build.
pipeline {
    agent any
    environment {
        VERSION = "1.${env.BUILD_NUMBER}"      // build #5 creates images tagged 1.5
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }             // download the code from GitHub
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements-dev.txt
                for s in student-service question-service result-service; do
                    pip install -r $s/requirements.txt
                done
                '''
            }
        }
        stage('Security Check') {
            steps {
                sh '''
                . venv/bin/activate
                for s in student-service question-service result-service; do
                    (cd $s && bandit -r . -x ./tests,./venv && pip-audit -r requirements.txt)
                done
                '''
            }
        }
        stage('Run Tests') {
            steps {
                sh '''
                . venv/bin/activate
                for s in student-service question-service result-service; do
                    (cd $s && pytest)
                done
                '''
            }
        }
        stage('Build Docker Images') {
            steps { sh 'docker compose build' }          // tags images with $VERSION
        }
        stage('Deploy') {
            steps { sh 'docker compose up -d' }
        }
    }
    post {
        success { echo "Build ${VERSION} succeeded" }
        failure { echo "Build failed - check the stage that is red" }
    }
}
