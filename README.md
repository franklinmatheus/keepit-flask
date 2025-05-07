# KeepIt – Personal and Family Financial Management System

## Overview

**KeepIt** is a personal and family financial management system developed during the *Database (DIM0125)* course at the Federal University of Rio Grande do Norte (UFRN). It supports collaborative financial tracking, enabling users to manage shared incomes and expenses within a family group while automating recurring entries and generating insightful reports.

## 🔧 Technologies Used

### 🖥️ Backend (Python + Flask)

- **Python 3** – Main programming language  
- **Flask** – Web framework to handle routes and requests  
- **MySQL Connector (mysql-connector-python)** – Executes SQL statements for persistent data storage  

### 📊 Data Management and Visualization

- **SQL** – Used extensively for user authentication, CRUD operations on incomes/expenses, and report generation  
- **Pandas** – Data manipulation and aggregation for financial reports  
- **Statsmodels**, **Scipy** – Financial forecasting and statistical modeling  

### 🧰 Support Libraries

- **Flask-Caching** – Response caching for performance  
- **Jinja2**, **Werkzeug**, **Click** – Flask core components  
- **DateUtil**, **PyTZ** – Date/time handling for scheduling and recurring transactions  

## 💾 SQL Operations

The backend performs critical data operations using raw SQL queries, such as:

### 🔐 User Authentication
```sql
SELECT * FROM usuario WHERE login = %s AND senha = %s;
```

### 💰 Financial Transactions
```sql
-- Add common income
INSERT INTO receita_comum (id_receita, constante, automatica, dia_mes, status) VALUES (...);

-- Add uncommon income
INSERT INTO receita_incomum (id_receita, atualizada, emissor, motivo) VALUES (...);

-- Add common expense
INSERT INTO despesa_comum (id_despesa, constante, automatica, dia_mes, status) VALUES (...);

-- Add uncommon expense
INSERT INTO despesa_incomum (id_despesa, destino) VALUES (...);

-- Programmed future expense
INSERT INTO despesa_programada (id_despesa, deferido) VALUES (...);
```

### 📊 Reporting & Aggregation
```sql
-- Aggregate expenses and income by user/family
SELECT SUM(valor) FROM despesa WHERE cpf_usuario = %s AND MONTH(data) = %s;

-- Retrieve full transaction history
SELECT * FROM receita WHERE cpf_usuario = %s ORDER BY data DESC;
```

All queries are securely parameterized in Python using the MySQL Connector API.

## 🚀 Features
- Personal and family-level budget tracking
- Recurring and one-time income/expense management
- Calendar reminders for scheduled transactions
- Role-based interaction: Manager, Contributor, Dependent
- Automatic propagation of recurring transactions
- Financial reports with aggregation and forecasts

## 📦 System Architecture
The application is organized as a web-based backend built in Flask with a relational database (MySQL) supporting all data operations.

### Requirements

```txt
Click==7.0
Flask==1.0.3
Flask-Caching==1.7.2
mysql-connector-python==8.0.16
numpy==1.16.4
pandas==0.24.2
patsy==0.5.1
protobuf==3.8.0
python-dateutil==2.8.0
pytz==2019.1
scipy==1.3.0
six==1.12.0
statsmodels==0.9.0
Werkzeug==0.15.4
```

## ✅ Use Cases

| Code  | Description                        |
| ----- | ---------------------------------- |
| CSU01 | Add one-time income                |
| CSU02 | Add recurring income               |
| CSU03 | Add recurring expense              |
| CSU04 | Estimate monthly expenses          |
| CSU05 | Schedule one-time expense          |
| CSU06 | Add one-time expense               |
| CSU07 | Generate financial report          |
| CSU08 | Create family group                |
| CSU09 | Assign family members              |
| CSU10 | Request dependency support         |
| CSU11 | Approve dependency support request |

## ⚙️ Getting Started

1. Clone the repository:

```bash
git clone https://github.com/franklinmatheus/keepit-flask
```

2. Set up your Python environment:

```bash
pip install -r requirements.txt
```

3. Launch the Flask application:

```bash
python keepit/index.py
```
