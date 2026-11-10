# 💉 VacciTrack – City Vaccination Management System

A desktop-based vaccination management application developed using **Python, SQLite and Tkinter**. VacciTrack provides a simple graphical interface to manage vaccination centres, vaccination drives and dose records.

## 📌 Project Overview

VacciTrack is designed to simplify the management of city-level vaccination records. It uses a relational database to store and manage information about vaccination centres, vaccine drives and administered doses.

The application provides database management functionalities through an easy-to-use desktop interface.

## ✨ Key Features

- **Add Vaccination Records:** Register vaccination centres, vaccine details, dose types and quantities.
- **Combined View:** View vaccination information from multiple related database tables.
- **Centre Management:** View and delete vaccination centres.
- **Vaccination Drive Management:** View and delete vaccination drives.
- **Dose Record Management:** View and delete individual dose records.
- **Input Validation:** Prevent empty fields, duplicate centre names and invalid dose quantities.
- **Cascading Deletion:** Automatically delete associated records when a centre or vaccination drive is deleted.
- **Automatic Refresh:** Update database views and dropdown lists after insertions and deletions.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| SQLite | Relational database management |
| Tkinter | Graphical User Interface |
| SQL | Database operations and queries |
| VS Code | Development environment |
| Git & GitHub | Version control and project hosting |

## 🗄️ Database Structure

The application uses three interconnected relational tables:

### 1. Centres
Stores vaccination centre information.
- Centre ID (Primary Key)
- Centre Name
- Contact Email

### 2. Vaccination Drives
Stores information about vaccination drives.
- Drive ID (Primary Key)
- Centre ID (Foreign Key)
- Vaccine Name
- Drive Date

### 3. Dose Records
Stores individual dose information.
- Dose ID (Primary Key)
- Drive ID (Foreign Key)
- Dose Type
- Dose Quantity

**Relationships:**

- One vaccination centre can have multiple vaccination drives.
- One vaccination drive can have multiple dose records.
- Foreign key constraints maintain referential integrity.
- Cascading deletion maintains consistency when parent records are deleted.

## 🖥️ Application Interface

The application includes four database viewing tabs:

1. Combined View
2. Centres
3. Vaccination Drives
4. Dose Records

## ⚙️ Installation and Setup

### Prerequisites
- Python 3.x
- VS Code (recommended)

### Steps to Run

1. Clone this repository:

   ```bash
   git clone https://github.com/MilanAttumalil/VacciTrack.git
   ```

2. Navigate to the project directory:

   ```bash
   cd VacciTrack
   ```

3. Run the application:

   ```bash
   python Vaci_Track_final.py
   ```

SQLite is included with standard Python installations, so no separate database server is required.

## 🧪 Testing

The application has been tested for:

- Adding vaccination records.
- Deleting individual dose records.
- Deleting vaccination drives.
- Deleting vaccination centres.
- Duplicate centre validation.
- Empty field validation.
- Invalid dose quantity validation.
- Cascading deletion.
- Automatic database view and dropdown refresh.

All the above functional tests were successfully completed.

## 🚀 Future Enhancements

- Search and filter vaccination records.
- Generate vaccination statistics and reports.
- Add graphical data visualisations.
- Export vaccination records to CSV or Excel.
- Introduce user authentication and role-based access.

## 👨‍💻 Author

**Milan Rajesh Attumalil**

B.Sc. Data Science and Analytics

## 📄 License

This project is developed for academic and educational purposes.