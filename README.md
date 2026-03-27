# 📊 ASM Sales Tracker Pro
**A Web-Based Management System for Modern Sales Operations**

**Video Demo:** [Your YouTube Link Here]  
**Author:** Bui Huu Danh  
**Location:** Binh Dinh, Vietnam

---

## 🚀 Project Overview
**ASM Sales Tracker Pro** is a centralized platform designed to replace fragmented Excel sheets with a data-driven management system. It provides real-time visibility into sales performance across different organizational levels.

### 🔑 Key Features
* **Multi-level Hierarchy:** Supports three distinct user roles: **ASM** (Area Sales Manager), **Unit Manager**, and **Sales Agent**.
* **Real-time Performance Tracking:** A dynamic dashboard that visualizes KPI progress using color-coded **Bootstrap** progress bars.
* **Access Control & Privacy:** A robust permission system ensuring agents only see their own data, while managers gain a bird's-eye view of the entire team.
* **Team Management (ASM Exclusive):** Allows top-level managers to restructure the organization by reassigning agents to different units.

---

## 💾 Database Schema
The system utilizes **SQLite** with a relational structure designed for data integrity:

| Table | Description |
| :--- | :--- |
| **users** | Stores credentials (hashed via werkzeug), full names, and hierarchical metadata (`role_level`, `manager_id`). |
| **targets** | Stores monthly/yearly KPI quotas assigned to each individual. |
| **sales** | Records detailed transaction data, including amounts, customer names, and timestamps. |

---

## 🛠️ Technical Challenges & Solutions
During development, I successfully navigated several critical engineering hurdles:
* **Database Integrity:** Resolved "database disk image is malformed" errors by restructuring the schema and optimizing SQL initialization scripts.
* **Division-by-Zero Protection:** Implemented **SQL CASE statements** to handle scenarios where targets are not yet set, ensuring the dashboard remains error-free.
* **Hierarchical Logic:** Designed complex queries to ensure managers can only view data for their direct and indirect subordinates.

---

## 💻 Tech Stack
* **Backend:** Python (Flask)
* **Frontend:** HTML5, CSS3, JavaScript (Bootstrap 5)
* **Database:** SQL (SQLite3)
* **Libraries:** Flask-Session, Werkzeug, CS50 Library

---

## 📂 File Structure
* `app.py`: The core Flask application containing all routes and business logic.
* `project.db`: The SQLite database engine.
* `helpers.py`: Utility functions for login requirements and currency formatting.
* `templates/`: Jinja2 HTML templates for the UI.
* `static/`: Custom CSS and assets for the frontend.

---

## ⚙️ Getting Started
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
2. **Initialize the database:**
   ```bash
   sqlite3 project.db < schema.sql
3. **Launch the application:
Bash
flask run   
