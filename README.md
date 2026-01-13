# 🎓 Edu Fairuzullah - Learning Management System (LMS)

This repository contains the source code for the **Edu Fairuzullah LMS**, a cloud-native prototype developed for the **Cloud Computing** course assessment. The system allows educators to manage courses and resources while enabling learners to enroll and access educational content.

## 🚀 Live Deployment
The application is deployed and hosted on **AWS Elastic Beanstalk**.
* **Live URL:** [http://edufairuzullah-lms-env.eba-8bvurr59.ap-southeast-2.elasticbeanstalk.com/login]

## 📋 Features

### 1. Role-Based Access Control (RBAC)
* **Educator Role:**
  * Secure login/logout.
  * Create, Read, Update, and Delete (CRUD) courses.
  * Upload learning resources (PDF/Slides) to the cloud server.
  * Add virtual meeting links (Zoom/Teams).
* **Learner Role:**
  * Read-only access to course lists.
  * One-click Course Enrollment.
  * Access to download materials and join live classes after enrollment.

### 2. Cloud Architecture
* **Platform:** AWS Elastic Beanstalk (PaaS).
* **Compute:** EC2 Instances (Auto-scaling enabled).
* **Database:** SQLite (Prototype) / Designed for AWS RDS migration.
* **Storage:** Local Instance Storage (Prototype) / Designed for AWS S3.

## 🛠️ Technology Stack
* **Backend:** Python 3.10+, Flask Framework
* **Server:** Gunicorn (WSGI)
* **Database:** SQLite3
* **Frontend:** HTML5, Bootstrap 5, Jinja2 Templating
* **Infrastructure:** Amazon Web Services (AWS)

## ⚙️ How to Run Locally

1. **Clone the repository**
   ```bash
   git clone [https://github.com/your-username/Edu-Fairuzullah-LMS.git](https://github.com/your-username/Edu-Fairuzullah-LMS.git)
   cd Edu-Fairuzullah-LMS
   That is a great idea. having your code on GitHub is excellent for your portfolio and makes it easy for your lecturer to view your work.

2. **Install Dependencies**
```bash
pip install -r requirements.txt

```

3. **Run the Application**
```bash
python application.py

```

The app will run at `http://127.0.0.1:5000`.

## 📂 Project Structure

* `application.py`: Main Flask application logic and database routes.
* `templates/`: HTML interfaces for Login, Educator Dashboard, and Learner Dashboard.
* `requirements.txt`: List of dependencies required for AWS deployment.
```
