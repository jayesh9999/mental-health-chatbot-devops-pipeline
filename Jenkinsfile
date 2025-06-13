pipeline {
    agent any
    
    tools {
        jdk 'jdk23'
    }
    
    environment {
        SCANNER_HOME = tool 'sonar-scanner'
        DOCKER_IMAGE = "jayesh9999/mental_health_assistant:latest"
        DOCKER_BUILDKIT = '1'
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: 'main', credentialsId: 'githubtoken', url: 'https://github.com/jayesh9999/mental_health_assistant.git'
            }
        }
        stage('Owasp Dependency Scan') {
            steps {
                dependencyCheck additionalArguments: '--scan ./', nvdCredentialsId: 'owaspnvdapikey', odcInstallation: 'owasp'
                sh 'ls -lR | grep dependency-check-report.xml || echo "Report file not found"'
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }
        stage('Sonarqube Scan') {
            steps {
                withSonarQubeEnv('sonar') {
                    sh '''$SCANNER_HOME/bin/sonar-scanner -Dsonar.projectName=MentalhealthAssistant \
                    -Dsonar.projectKey=MentalhealthAssistant \
                    -Dsonar.sources=.'''
                }
            }
        }

        stage('DockerBuild') {
            steps {
                script {
                    withDockerRegistry( credentialsId: 'dockerhubcred', url: '') {
                        sh "docker pull jayesh9999/mental_health_assistant:latest || true"
                        sh "docker build --progress=plain --cache-from=${DOCKER_IMAGE} -t ${DOCKER_IMAGE} ."
                    }
                }
            }
        }

        stage('Docker Push') {
            steps {
                script {
                    withDockerRegistry( credentialsId: 'dockerhubcred', url: '') {
                        sh "docker push --quiet=false ${DOCKER_IMAGE}"
                        sh "docker rmi ${DOCKER_IMAGE} || true"
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                withCredentials([string(credentialsId: 'ec2-host', variable: 'EC2_HOST')]) {
                    sshagent(credentials: ['ec2-ssh']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${EC2_HOST} "
                            cd /opt/flask_app &&
                            docker pull ${DOCKER_IMAGE} &&
                            docker compose down || true &&
                            docker compose up -d
                        "
                        """
                    }
                }
            }
        }    
    }
    
    post {
        always {
            cleanWs()
            sh "docker image prune -f"
        }
    }
}