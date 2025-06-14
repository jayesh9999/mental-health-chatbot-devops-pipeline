End-to-End DevOps Workflow: Deploying a GenAI Mental Health Assistant

A production-ready AI-powered Mental Health Assistant Chatbot designed using Flask, Google Gemini, and LangChain. This project is focused on highlighting end-to-end DevOps practices including infrastructure provisioning, configuration management, CI/CD automation, containerization, and deployment.

🚀 Project Objective

To demonstrate real-world DevOps engineering skills through the full software delivery lifecycle of a production application:

Deploy and manage the application using best DevOps practices in a cloud environment.

Build an intelligent chatbot that addresses mental health-related queries empathetically and informatively.


![devops_architecture_chatbot drawio](https://github.com/user-attachments/assets/58ccf765-ac7d-41ec-953d-21b4409fd9de)


⚙️ Technologies Used

Application Stack:

Flask: Python web framework for backend

LangChain: Framework for integrating LLMs

Google Gemini Pro: For natural language generation

PostgreSQL: Database for user and chat history

Docker: Containerization

DevOps Stack:

Terraform: Infrastructure as Code (IaC) to provision AWS EC2

Ansible: Configuration management of EC2 instance

Docker Compose: Multi-container orchestration

Jenkins: CI/CD pipeline

GitHub: Source code and CI/CD trigger

Docker Hub: Container image registry

Nginx: Reverse proxy and static file serving

🧰 Key DevOps Highlights

1. 🌐 Infrastructure Provisioning (Terraform)

Provisioned an EC2 instance on AWS using Terraform.

Defined networking, security groups, and instance attributes in code.

Ensured reproducibility and version control for infrastructure.

2. ✉️ Configuration Management (Ansible)

Used Ansible playbooks to:

Install Docker and dependencies

Configure Nginx

Prepare the instance for deployment

3. ⚒️ CI/CD Pipeline (Jenkins)

Configured Jenkins with GitHub webhook to auto-trigger on git push

Steps in pipeline:

Clone the latest code

Build Docker image for Flask app

Push image to Docker Hub

SSH into EC2 instance

Pull latest Docker image

Restart application using Docker Compose

4. 📁 Containerization & Deployment

The app is containerized using Docker.

docker-compose.yaml defines the services:

Flask app

PostgreSQL

Nginx reverse proxy

🎮 Features of the Chatbot

Empathetic and professional tone in responses

Real-time typing animation

User login and chat history storage

🚩 How to Run Locally (Optional)

git clone https://github.com/your-username/mental-health-chatbot.git

cd mental-health-chatbot

docker-compose up --build

App will be available at: http://localhost

📦 Docker Hub

https://hub.docker.com/r/jayesh9999/mental_health_assistant

🚀 Future Improvements

Add monitoring using Prometheus + Grafana

Enable HTTPS using Let's Encrypt

🌐 Live URL

http://13.127.34.192/

📊 Author

Jayesh Thorat

DevOps Enthusiast | AWS Certified Solutions Architect
