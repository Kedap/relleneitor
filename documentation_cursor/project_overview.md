# Project Overview

## 🧠 Project Purpose

This project is a **Python tool to generate SQL queries** (`INSERT INTO ...`) using **synthetic data** from the `faker` library. It is designed to assist developers in **quickly creating data** for testing or seeding databases — without requiring a live database connection.

---

## ✅ Functional Requirements

The program **must be able to**:

- Define a table schema (name, columns, data types)
- Generate a list of SQL `INSERT` statements with:
  - Random but realistic values
  - Specified number of rows
- Print the generated SQL to terminal or save to `.sql` file
- Accept config via function parameters or CLI (future)

---

## 📦 Expected Code Components

### 1. `TableSchema` class  
Represents the structure of a SQL table.

```python
TableSchema(
    name="users",
    columns=[
        Column(name="id", type="INTEGER", faker="random_int"),
        Column(name="email", type="VARCHAR", faker="email"),
        Column(name="created_at", type="DATETIME", faker="date_time"),
    ]
)
```

### 2. QueryGenerator class

Takes a TableSchema and generates valid SQL INSERT statements using faker.

### 3. CLI Entry Point (optional for now)

Accept arguments like:

    table name

    number of rows

    output file path

### 📌 Design Assumptions

    Output is **SQL-only** (no execution)

    All values are properly escaped/quoted/formatted

    Compatible with standard SQL dialects

    Faker providers are used intelligently based on column type

### 🧪 Suggestions & Best Practices

    Use dataclasses for schema and columns

    Use type hints (-> str, -> list[str], etc.)

    Separate logic: schema → data → SQL string → file

    Support string quoting and date formatting helpers

    Allow easy addition of new data types / column templates

    Keep code modular, documented, and readable

### Example Output

```python
INSERT INTO users (id, email, created_at) VALUES (1, 'john.doe@example.com', '2024-02-12 14:35:00');
```

