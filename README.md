# Football Data ETL Project - Short Kings

A Jupyter-based project for Extract, Transform, Load (ETL) operations on football data. This project provides a structured environment for analyzing football statistics, player performance, and team metrics.

## 📋 Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Components](#project-components)
- [Contributing](#contributing)
- [License](#license)

## 📁 Project Structure

```
Brief-2-ETL-donnees-footballistiques-Short-Kings/
│
├── notebooks/              # Jupyter notebooks for analysis
│   └── 01_getting_started.ipynb
│
├── data/                   # Data directory
│   ├── raw/               # Raw data files
│   └── processed/         # Processed/cleaned data
│
├── src/                    # Source code and utilities
│   ├── __init__.py
│   └── etl_utils.py       # ETL utility functions
│
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── LICENSE                # Project license
└── README.md              # This file
```

## 🔧 Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package installer) - Usually comes with Python
- **Git** - [Download Git](https://git-scm.com/downloads)

### Verify Installation

```bash
python --version    # Should show Python 3.8 or higher
pip --version       # Should show pip version
git --version       # Should show git version
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Simplon-DE-P1-2025/Brief-2-ETL-donnees-footballistiques-Short-Kings.git
cd Brief-2-ETL-donnees-footballistiques-Short-Kings
```

### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment helps isolate project dependencies.

**On Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your terminal prompt, indicating the virtual environment is active.

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:
- Jupyter Notebook & JupyterLab
- pandas, numpy (data manipulation)
- matplotlib, seaborn (visualization)
- requests, beautifulsoup4 (data extraction)
- And more...

### 4. Verify Installation

```bash
jupyter --version
python -c "import pandas; import numpy; print('All packages installed successfully!')"
```

## 📊 Usage

### Starting Jupyter Notebook

#### Option 1: Classic Jupyter Notebook

```bash
jupyter notebook
```

This will open Jupyter in your default web browser at `http://localhost:8888/`

#### Option 2: JupyterLab (Modern Interface)

```bash
jupyter lab
```

This will open JupyterLab in your default web browser at `http://localhost:8888/lab`

### Running the Getting Started Notebook

1. Navigate to the `notebooks/` directory in the Jupyter interface
2. Open `01_getting_started.ipynb`
3. Run cells sequentially by clicking "Run" or pressing `Shift + Enter`

### Working with Your Own Data

1. **Place your raw data files** in the `data/raw/` directory
2. **Load the data** in your notebook using:
   ```python
   from etl_utils import load_csv_data
   df = load_csv_data('../data/raw/your_data_file.csv')
   ```
3. **Process and analyze** your data using the provided utilities
4. **Save processed data** to `data/processed/` directory

### Using Custom Utilities

The `src/etl_utils.py` module provides helpful functions:

```python
from etl_utils import (
    load_csv_data,      # Load data from CSV
    clean_dataframe,    # Clean and preprocess data
    save_data,          # Save data in various formats
    get_data_summary    # Get data statistics
)
```

## 🧩 Project Components

### Notebooks

- **01_getting_started.ipynb**: Introduction to the project with sample football data analysis

### Source Code

- **src/etl_utils.py**: Reusable ETL utility functions for data processing

### Data

- **data/raw/**: Store your original, unmodified data files here
- **data/processed/**: Store cleaned and processed data files here

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🆘 Troubleshooting

### Common Issues

**Issue: `jupyter: command not found`**
- Solution: Make sure your virtual environment is activated and Jupyter is installed

**Issue: Module import errors in notebook**
- Solution: Ensure the virtual environment kernel is selected in Jupyter
- In Jupyter: Kernel → Change Kernel → Python 3 (venv)

**Issue: Port 8888 already in use**
- Solution: Use a different port: `jupyter notebook --port 8889`

### Getting Help

If you encounter any issues:
1. Check that all dependencies are installed correctly
2. Verify your Python version is 3.8 or higher
3. Make sure your virtual environment is activated
4. Check the [Issues](https://github.com/Simplon-DE-P1-2025/Brief-2-ETL-donnees-footballistiques-Short-Kings/issues) page for similar problems

## 📚 Additional Resources

- [Jupyter Documentation](https://jupyter.org/documentation)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/)

---

**Happy Data Analysis! ⚽📊**
