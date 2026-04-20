# 🩸 RaktSetu — Blood Bridge Management System

> A full-stack blood bank management web application built for NMIMS MPSTME DBMS Mini Project (A.Y. 2025–26)

---

## 👥 Team

| Roll No. | Name | Contribution |
|----------|------|--------------|
| L074 | Mahak Wadhawan | UI Frontend (HTML/CSS/JS), SQL Queries |
| L056 | Yash Shah | Database Design, Tables, Seed Data, SQL Queries |
| L069 | Varshita Vaan | Flask Backend, API Connections, ER Diagram, SQL Queries |

---

## 📌 About the Project

**RaktSetu** (meaning *Blood Bridge* in Sanskrit) is a web-based Blood Bank Management System that digitises and streamlines the entire blood lifecycle — from donor registration and blood collection, through inventory management, to hospital blood request fulfilment.

The system is built on a **three-tier architecture**:
- **Frontend** — Single-page HTML/CSS/JS application
- **Backend** — Python (Flask) REST API
- **Database** — MySQL relational database

---

## ✨ Features

- 📋 **Donor Registry** — Register, search (by name/blood group/city), and delete donors
- 🏥 **Hospital Directory** — Manage registered hospitals
- 🩸 **Blood Inventory** — Track units per blood group with expiry date monitoring and one-click dispense
- 🚨 **Blood Requests** — Raise and manage requests with CRITICAL / HIGH / NORMAL priority levels and PENDING → APPROVED → FULFILLED status workflow
- 📊 **Dashboard** — Live summary cards (total donors, units in stock, pending requests, hospitals)
- 💻 **SQL Console** — In-app terminal for running SELECT / INSERT / UPDATE / DELETE queries directly

---

## 🗂️ Project Structure

```
RaktSetu/
├── app.py                  # Flask REST API (13 endpoints)
├── index.html              # Single-page frontend
├── raktsetu.sql            # Full DB schema + seed data + 22 SQL queries
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Database | MySQL 8.0 |
| Backend | Python 3.11, Flask |
| CORS | flask-cors |
| DB Driver | mysql-connector-python |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| API Style | REST (JSON) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/RaktSetu.git
cd RaktSetu
```

### 2. Set up the database

Open MySQL and run the SQL file:

```bash
mysql -u root -p < raktsetu.sql
```

This creates the `raktsetu` database, all four tables, indexes, and seeds 20 donors, 10 hospitals, 20 inventory records, and 18 blood requests.

### 3. Configure the database password

In `app.py`, update the `DB_CONFIG` block with your MySQL credentials:

```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'YOUR_PASSWORD',   # ← change this
    'database': 'raktsetu'
}
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Flask server

```bash
python app.py
```

The server starts at `http://localhost:5000`.

### 6. Open the app

Open `http://localhost:5000` in your browser. The Flask server serves `index.html` directly.

---

## 🗄️ Database Schema

```
donors              blood_inventory
──────────────      ──────────────────────
donor_id  (PK)  ──< inv_id        (PK)
name                blood_group
age                 units
blood_group         expiry_date
phone               received_date
city                donor_id      (FK)
last_donated

hospitals           blood_requests
──────────────      ──────────────────────
hospital_id (PK)──< req_id        (PK)
name                hospital_id   (FK)
city                patient
contact             blood_group
                    units
                    priority  (CRITICAL/HIGH/NORMAL)
                    status    (PENDING/APPROVED/FULFILLED)
                    contact
                    request_date
```

**Foreign keys:**
- `blood_inventory.donor_id` → `donors.donor_id` (ON DELETE SET NULL)
- `blood_requests.hospital_id` → `hospitals.hospital_id` (ON DELETE SET NULL)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Dashboard summary counts |
| GET | `/api/donors` | List donors (supports `?search=` and `?blood_group=` filters) |
| POST | `/api/donors` | Register a new donor |
| DELETE | `/api/donors/<donor_id>` | Delete a donor |
| GET | `/api/inventory` | Full inventory listing |
| GET | `/api/inventory/summary` | Total units grouped by blood group |
| POST | `/api/inventory` | Add blood units to inventory |
| POST | `/api/inventory/<inv_id>/dispense` | Dispense one unit from a batch |
| GET | `/api/requests` | List all blood requests (with hospital names) |
| POST | `/api/requests` | Submit a new blood request |
| PATCH | `/api/requests/<req_id>/status` | Update request status (APPROVED / FULFILLED) |
| GET | `/api/hospitals` | List all hospitals |
| POST | `/api/sql` | Execute a custom SQL query |

---

## 📝 SQL Queries Covered

The `raktsetu.sql` file includes **22 SQL queries** demonstrating:

- Basic SELECT, WHERE filters
- GROUP BY with COUNT, SUM, AVG
- INNER JOIN, LEFT JOIN (2-table and 3-table)
- HAVING clause
- Date functions (`DATE_SUB`, `DATE_ADD`, `CURDATE`, `INTERVAL`)
- Subquery (units above average)
- UPDATE (status change, inventory decrement)

---

## 📚 Course Details

- **Institute:** SVKM's NMIMS — Mukesh Patel School of Technology Management & Engineering
- **Course:** Database Management Systems (DBMS)
- **Academic Year:** 2025–26
- **Semester:** IV

---

## ⚠️ Notes

- This project is intended for **local development / academic use only**. The SQL Console endpoint exposes raw DML access and should not be deployed publicly.
- The auto-generated IDs (D001, H001, etc.) assume single-user access. Concurrent writes may cause ID collisions in a multi-user environment.

---

*Made with ❤️ by Mahak Wadhawan, Yash Shah & Varshita Vaan*
