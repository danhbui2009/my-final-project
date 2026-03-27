ASM Sales Tracker Pro
Video Demo: [\[Your YouTube Link Here\]](https://www.youtube.com/watch?v=UiK2THjfBpY)
Author: Bui Huu Danh
Location: Binh Dinh, Vietnam
1. Project Overview
The ASM Sales Tracker Pro is a web-based management system designed to solve real-world challenges in sales operations. Instead of relying on fragmented Excel sheets, this platform centralizes data to provide:

Multi-level Hierarchy: Supports three distinct user roles: ASM (Area Sales Manager), Unit Manager, and Sales Agent.

Real-time Performance Tracking: A dynamic dashboard that visualizes KPI progress using color-coded Bootstrap progress bars.

Access Control & Privacy: A robust permission system ensuring agents only see their own data, while managers gain a birds-eye view of the entire team.

2. Database Schema
The system utilizes SQLite with a relational structure consisting of three core tables:

users: Stores credentials (hashed via werkzeug), full names, and hierarchical metadata (role_level, manager_id).

targets: Stores monthly/yearly KPI quotas assigned to each individual.

sales: Records detailed transaction data, including amounts, customer names, and timestamps.

3. Key Features
Role-Based Authentication: Users select their organizational level during registration. The system maintains state using Flask-Session.

Dynamic Dashboard: Implements complex SQL queries (JOIN, GROUP BY, SUM) to calculate real-time completion percentages.

Team Management (ASM Exclusive): Allows top-level managers to restructure the organization by reassigning agents to different managers.

Target Setting & Sales Reporting: A seamless workflow from quota allocation to daily sales updates.

Transaction History: A comprehensive audit trail of all recorded sales, sorted by recency for easy reconciliation.

4. Technical Challenges
During development, I successfully navigated several critical engineering hurdles:

Database Integrity: Faced and resolved a database disk image is malformed error by restructuring the schema and optimizing SQL initialization scripts.

Division-by-Zero Protection: Implemented SQL CASE statements to handle scenarios where targets are not yet set, ensuring the dashboard remains functional and error-free.

Hierarchical Logic: Designed recursive-style queries to ensure managers can only view data for their direct and indirect subordinates.

5. File Structure
app.py: The core Flask application containing all routes and business logic.

project.db: The SQLite database engine.

helpers.py: Utility functions for login requirements and currency formatting.

templates/: Jinja2 HTML templates for the UI.

static/: Custom CSS and assets for the frontend.

6. Getting Started
Install dependencies: pip install -r requirements.txt

Initialize the database: sqlite3 project.db < schema.sql

Launch the application: flask run
