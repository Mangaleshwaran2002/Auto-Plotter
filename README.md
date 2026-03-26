# Auto-Plotter

An automated Exploratory Data Analysis (EDA) visualization tool built using **Python**, **Pandas**, **Matplotlib**, and **Seaborn**.

This project simplifies EDA by **automatically generating meaningful visualizations** based on dataset structure, data types, and quality checks.

## 🚀 Features

* 📥 Robust CSV loading with multiple encoding support
* 🔍 Automatic detection of:

  * Numeric columns
  * Categorical columns
* 🧠 Smart validation before plotting:

  * Skips ID-like columns
  * Avoids high-cardinality categorical data
  * Ensures only meaningful plots are generated
* 📊 Supported visualizations:

  * Histogram
  * Boxplot
  * Countplot
  * Pie chart
  * Scatter plot
  * Correlation heatmap
* 📁 Saves all plots in a `plots/` directory
* ⚡ Progress tracking with `tqdm`
* 🪵 Logging for transparency

## 📦 Installation (Using `uv`)

This project uses **`uv`** for fast and efficient environment management.

### 1️⃣ Install `uv`

```bash
pip install uv
```

or

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Create Virtual Environment

```bash
uv venv
```

### 3️⃣ Activate Environment

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 4️⃣ Install Dependencies

Using your existing `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

## 🧑‍💻 Usage

```python
from plotter import Plotter

# Initialize with dataset path
plotter = Plotter("data.csv")

# Preview dataset
print(plotter)

# Dataset summary
plotter.summary()

# Generate all plots
plotter.auto_plot()
```

## 📁 Output

All plots are saved in:

```
plots/
```

### Example Output

```
plots/
├── feature_histogram.png
├── feature_boxplot.png
├── category_countplot.png
├── category_pie.png
├── feature1_vs_feature2_scatter.png
└── correlation_heatmap.png
```

## 🧠 How It Works

### 🔹 Data Loading

* Attempts multiple encodings (`utf-8`, `latin1`, etc.)
* Prevents common CSV read errors

### 🔹 Column Classification

* **Numeric** → integers, floats
* **Categorical** → object, string, category, boolean

### 🔹 Smart Validation

#### 🚫 Automatically skips:

* ID-like columns (>95% unique values)
* Columns with too few unique values
* High-cardinality categorical columns

#### ✅ Ensures:

* Clean, readable, and meaningful plots only

## 📊 Plot Rules

| Plot Type    | Conditions                        |
| ------------ | --------------------------------- |
| Histogram    | Numeric, non-ID, enough variation |
| Boxplot      | Numeric with spread               |
| Countplot    | Categorical, low cardinality      |
| Pie Chart    | 2–8 categories                    |
| Scatter Plot | Two valid numeric columns         |
| Heatmap      | ≥ 2 numeric columns               |

## ⚙️ Class Overview

### `Plotter`

#### Core Methods

* `read_dataset()` → Load CSV safely
* `check_dtype()` → Detect numeric columns
* `is_id_column()` → Identify ID-like columns
* `is_high_cardinality()` → Detect excessive categories

#### Plot Methods

* `plot_histogram()`
* `plot_boxplot()`
* `plot_countplot()`
* `plot_pie()`
* `plot_scatter()`
* `plot_heatmap()`

#### Automation

* `auto_plot()` → Full EDA pipeline

#### Utility

* `summary()` → Dataset overview

## ⚠️ Limitations

* Supports only CSV files
* No missing value handling
* Static plots only (no interactivity)
* Large datasets may slow scatter plot generation

## 🔮 Future Improvements

* Support for Excel / JSON
* Interactive plots (Plotly)
* Auto-generated EDA reports (HTML/PDF)
* Parallel plot generation
* Feature insights & recommendations


## 🤝 Contributing

Contributions are welcome!

* Fork the repo
* Improve validation logic
* Add new visualizations



## 📜 License

This project is open-source and free to use.


## 💡 Summary

This tool helps you:

* ⏱ Save time on EDA
* 📊 Automatically generate relevant plots
* 🧹 Avoid noisy or useless visualizations

Perfect for:

* Data analysts
* ML preprocessing
* Quick dataset exploration
