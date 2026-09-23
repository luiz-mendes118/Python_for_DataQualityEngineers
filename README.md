# Python for Data Quality Engineers

Welcome to the **Python for Data Quality Engineers** repository! This repository contains coursework, labs, scripts, and assignments focused on building robust data pipelines, implementing automated data validation, testing data quality, and ensuring data integrity using Python.

---

## 🛠️ Prerequisites & Setup

Before working with this repository, make sure you have the course prerequisites set up:

1. **GitHub Account:** [GitHub](https://github.com/) configured for version control.
2. **Python 3:** Download and install Python 3.
3. **IDE:** Download and install [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/) for developing and debugging your code.

---

## 📂 Repository Structure

Python_for_DataQualityEngineers/
│
├── .gitignore               # Files & directories to ignore (e.g., venv, __pycache__, .idea, .DS_Store)
├── README.md                # Project documentation (this file)
├── requirements.txt         # Project dependencies
│
├── tasks/                   # Course tasks and assignments
│   ├── 1-python_basics/     # Module 1: Python Basics & Data Profiling
│   │   ├── Python_Basics_Task.py
│   │   └── data_profiler.py
│   ├── 2-collections/       # Module 2: Collections & Dictionary Merge
│   │   └── collections_task.py
│   └── 3-string_objects/    # Module 3: String Manipulation & Text Cleaner
│       └── string_objects_task.py
│
└── tests/                   # Shared unit and integration tests (optional)


---

## 🚀 Getting Started

### Installation & Setup

1. **Clone the repository:**
   git clone https://github.com/luiz-mendes118/Python_for_DataQualityEngineers.git
   cd Python_for_DataQualityEngineers

2. **Open in PyCharm:**
   * Open PyCharm Community Edition.
   * Select **Open** and choose your cloned `Python_for_DataQualityEngineers` project directory.

3. **Create and activate a virtual environment:**
   * **macOS / Linux:**
     python3 -m venv venv
     source venv/bin/activate
   * **Windows:**
     python -m venv venv
     venv\Scripts\activate
   *(Note: PyCharm can also automatically configure your virtual environment when opening a new project).*

4. **Install dependencies:**
   pip install --upgrade pip
   pip install -r requirements.txt

---

## 📝 Course Modules & Progress

| Module / Task | Topic / Description | Timeline | Status | Directory / File |
| :---: | :--- | :---: | :---: | :--- |
| **Module 1** | **Python Basics & Data Profiling**<br>Essentials, Bubble Sort, Min/Max & Averages | Sep 23 – Sep 26, 2026 | ✅ Completed | `tasks/1-python_basics/` |
| **Module 2** | **Collections (Dictionary Merge)**<br>Lists, Dictionaries, Data Deduplication & Conflict Resolution | Sep 23 – Sep 26, 2026 | ✅ Completed | `tasks/2-collections/collections_task.py` |
| **Module 3** | **String Objects (Text Cleaner)**<br>String Manipulation, Normalization, Data Profiling & Whitespace Counter | Sep 23 – Sep 26, 2026 | ✅ Completed | `tasks/3-string_objects/string_objects_task.py` |
| **Module 4** | *Upcoming Data Quality & Validation Topics* | — | ⏳ Pending | — |

---

## 🧪 Running Tasks & Scripts

You can run your scripts directly from PyCharm or via the command line:

python tasks/1-python_basics/data_profiler.py
python tasks/2-collections/collections_task.py
python tasks/3-string_objects/string_objects_task.py

---

## 💡 Best Practices Implemented in This Repo

1. **Clean Code & PEP 8:** All Python scripts adhere to PEP 8 styling conventions.
2. **Type Hinting & Robustness:** Handling edge cases gracefully (e.g., division-by-zero checks, whitespace profiling, and case-insensitive typo replacements).
3. **Data Quality Focus:** Every task emphasizes data manipulation, validation, deduplication, and accuracy.
4. **Version Control:** Meaningful commit messages following conventional commit standards.

---

## 🤝 Contributing

This is a personal coursework repository, but feedback, suggestions, and discussions on data engineering best practices are always welcome! Feel free to open an issue or submit a pull request.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
