# Contributing to Book Data Analysis

Thank you for your interest in contributing! Your help is appreciated and will make this project better for everyone.  

This document explains how to set up your environment, contribute code, and submit Pull Requests (PRs).

---

## 📥 Getting Started

### 1. Fork the repository
Click the **Fork** button on GitHub to create your personal copy of the repository.

### 2. Clone your fork
```bash
git clone https://github.com/YOUR_USERNAME/book_data_analysis.git
cd book_data_analysis
```

3. Create a virtual environment
```
python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows
```
4. Install dependencies
```
pip install -r requirements.txt

```


5. Run the app locally

```
streamlit run 4.app/app.py

```


The app will automatically use demo data (*_demo.parquet) if your local data files are missing.

## 🛠️ Making Changes

1. Create a new branch for your work:
```
git checkout -b feature/your-feature-name
```

2. Make your changes in this branch. Keep commits small and focused.

3. Test your code locally to ensure nothing breaks:

* ETL scripts (3.transformations)
* Streamlit app (4.app)

4. Add or update demo files if your changes involve new data outputs.

5. Commit your changes with a clear message:
```
git add .
git commit -m "Add new chart to visualize reading speed"
```
6. Push your branch to your fork:
```
git push origin feature/your-feature-name

```

7. Open a Pull Request (PR) on the main repository:
* Target branch: main
* Describe your changes clearly
* Link any relevant issues

## ✅ PR Guidelines

* Do not commit sensitive or private data.
* Keep code clean and consistent (follow existing Python style).
* Include comments or docstrings for new functions or classes.
* Test new features before submitting.
* Keep PRs focused on one specific task.

## 💡 Ideas for Contribution

* Add new visualizations or KPIs
* Improve the ETL pipeline
* Optimize data processing or performance
* Add automated tests
* Enhance the Streamlit user interface
* fix my spaghetti code 😂

## 🧹 Cleaning Up

After your PR is merged, you can safely delete your local branch:
```
git checkout main
git pull origin main
git branch -d feature/your-feature-name

```

Thank you for helping improve Book Data Analysis! 🎉