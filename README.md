# Library Management System

## Overview

A web-based application designed to help librarians manage books, members, and transactions efficiently. Built with Django and featuring a modern, responsive user interface.

## Features

- **Books Management**
  - Add, view, edit, and delete books.
  - Track stock levels.
  - Search books by title and author.

- **Members Management**
  - Add, view, edit, and delete library members.
  - Monitor outstanding debts (maximum Rs.500).

- **Transactions**
  - Issue books to members.
  - Process book returns.
  - Automatically calculate and charge fees for overdue returns.

- **Data Import**
  - Import books in bulk from an external API.
  - Specify the number of books to import with optional filters (title, authors, ISBN, publisher).

## Technologies Used

- **Backend:** Django 5.1.1, Python 3.12
- **Frontend:** HTML, CSS, Bootstrap 5
- **Database:** SQLite (default; can be switched to PostgreSQL or others)
- **Dependencies:** `requests`, `gunicorn`

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/deepak982/Library-Management
cd library_management
