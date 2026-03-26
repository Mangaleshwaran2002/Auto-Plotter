from pathlib import Path
from typing import Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.api.types import is_numeric_dtype
from tqdm import tqdm

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

class Plotter:
    """
    Intelligent Auto-EDA visualization tool.

    This class loads a dataset and automatically generates
    meaningful visualizations by verifying whether the
    data is suitable for each type of plot.

    Supported visualizations
    ------------------------
    - Histogram
    - Boxplot
    - Countplot
    - Pie chart
    - Scatter plot
    - Correlation heatmap

    Generated plots are saved inside a `plots/` directory.
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize the Plotter object.

        Parameters
        ----------
        file_path : str or pathlib.Path
            Path or URL pointing to a CSV dataset.

        Notes
        -----
        During initialization:
        - The dataset is loaded.
        - Numeric and categorical columns are detected.
        - A folder named `plots` is created to store charts.
        """

        self.dataframe = self.read_dataset(file_path)

        self.numeric_columns = self.dataframe.select_dtypes(include="number").columns.tolist()
        self.categorical_columns = self.dataframe.select_dtypes(
            include=["object", "category", "string", "bool"]
        ).columns.tolist()

        self.output_dir = Path("plots")
        self.output_dir.mkdir(exist_ok=True)

    def __str__(self) -> str:
        """
        Return a readable preview of the dataset.

        Returns
        -------
        str
            String representation of the first few rows
            of the dataset.
        """

        return str(self.dataframe.head())

    def read_dataset(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load a CSV dataset from a file path or URL.

        The method attempts multiple encodings to avoid
        Unicode decoding errors when reading CSV files.

        Parameters
        ----------
        file_path : str or pathlib.Path
            Path or URL of the CSV dataset.

        Returns
        -------
        pandas.DataFrame
            Loaded dataset.

        Raises
        ------
        ValueError
            If the dataset cannot be read using the
            available encodings.
        """

        encodings = ["utf-8", "utf-8-sig", "latin1", "iso-8859-1", "cp1252"]

        for enc in encodings:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                logger.info(f"Dataset loaded using encoding: {enc}")
                return df
            except Exception:
                continue

        raise ValueError("Unable to read dataset with available encodings")

    def check_dtype(self, col_name: str) -> bool:
        """
        Determine whether a column contains numeric values.

        Parameters
        ----------
        col_name : str
            Name of the column to check.

        Returns
        -------
        bool
            True if the column is numeric,
            False if the column is categorical.
        """
        return is_numeric_dtype(self.dataframe[col_name])

    def is_id_column(self, col_name: str) -> bool:
        """
        Detect whether a column behaves like an ID column.

        ID columns usually contain nearly unique values
        for each row and do not provide useful information
        for visualization.

        Parameters
        ----------
        col_name : str
            Column name to evaluate.

        Returns
        -------
        bool
            True if the column is likely an ID column,
            otherwise False.
        """
        if len(self.dataframe) == 0:
            return False
        
        unique_ratio = self.dataframe[col_name].nunique() / len(self.dataframe)

        return unique_ratio > 0.95

    def is_high_cardinality(self, col_name: str, threshold: int = 20) -> bool:
        """
        Check whether a categorical column contains too many categories.

        Columns with high cardinality often produce unreadable plots.

        Parameters
        ----------
        col_name : str
            Column name to evaluate.

        threshold : int, default=20
            Maximum number of allowed unique categories.

        Returns
        -------
        bool
            True if the column exceeds the category threshold.
        """

        return self.dataframe[col_name].nunique() > threshold

    def is_valid_histogram(self, col_name: str) -> bool:
        """
        Verify whether a histogram is appropriate for a column.

        Conditions
        ----------
        - Column must be numeric
        - Column should not behave like an ID
        - Column should have sufficient unique values

        Parameters
        ----------
        col_name : str

        Returns
        -------
        bool
        """

        if not self.check_dtype(col_name):
            return False

        if self.is_id_column(col_name):
            return False

        if self.dataframe[col_name].nunique() < 5:
            return False

        return True

    def is_valid_countplot(self, col_name: str) -> bool:
        """
        Determine if a countplot is suitable for a column.

        Parameters
        ----------
        col_name : str

        Returns
        -------
        bool
            True if the column is categorical and
            does not have excessive categories.
        """

        if self.check_dtype(col_name):
            return False

        if self.is_high_cardinality(col_name):
            return False

        if self.dataframe[col_name].nunique() < 2:
            return False

        return True

    def is_valid_pie(self, col_name: str) -> bool:
        """
        Verify whether a pie chart is appropriate.

        Pie charts are only suitable when the number
        of categories is small.

        Parameters
        ----------
        col_name : str

        Returns
        -------
        bool
        """

        if self.check_dtype(col_name):
            return False

        if  self.dataframe[col_name].nunique() < 2:
            return False

        if  self.dataframe[col_name].nunique() > 8:
            return False

        return True

    def is_valid_scatter(self, col_x: str, col_y: str) -> bool:
        """
        Determine if a scatter plot between two columns
        is meaningful.

        Parameters
        ----------
        col_x : str
            Column for the X-axis.

        col_y : str
            Column for the Y-axis.

        Returns
        -------
        bool
        """

        if not (self.check_dtype(col_x) and self.check_dtype(col_y)):
            return False

        if self.is_id_column(col_x) or self.is_id_column(col_y):
            return False

        if self.dataframe[col_x].nunique() < 5:
            return False

        if self.dataframe[col_y].nunique() < 5:
            return False

        return True
    
    def is_valid_boxplot(self, col_name: str) -> bool:
        """
        Check whether a boxplot is appropriate for a column.

        Conditions
        ----------
        - Column must be numeric
        - Column should not behave like an ID
        - Column should have enough unique values
        - Column should not contain only null values
        """

        if not self.check_dtype(col_name):
            return False

        if self.is_id_column(col_name):
            return False

        series = self.dataframe[col_name].dropna()

        if len(series) == 0:
            return False

        if series.nunique() < 10:
            return False

        if series.std() == 0:
            return False

        return True

    def plot_histogram(self, col_name: str):
        """
        Generate and save a histogram for a numeric column.

        Parameters
        ----------
        col_name : str
            Column name to visualize.

        Notes
        -----
        The histogram is generated only if the column
        satisfies validation conditions.
        """

        if not self.is_valid_histogram(col_name):
            logger.info(f"Skipping histogram: {col_name}")
            return

        plt.figure()
        sns.histplot(self.dataframe[col_name], kde=True)
        plt.title(f"{col_name} Distribution")

        plt.savefig(self.output_dir / f"{col_name}_histogram.png")
        plt.close()

    def plot_boxplot(self, col_name: str):
        """
        Generate and save a boxplot for a numeric column.

        Parameters
        ----------
        col_name : str
            Column name to visualize.

        Notes
        -----
        Boxplots are useful for detecting outliers
        and understanding distribution spread.
        """

        if not self.is_valid_boxplot(col_name):
            print(f"Skipping boxplot: {col_name}")
            return

        series = self.dataframe[col_name].dropna()

        plt.figure()

        sns.boxplot(x=series)

        plt.title(f"{col_name} Boxplot")

        plt.savefig(self.output_dir / f"{col_name}_boxplot.png")
        plt.close()

    def plot_countplot(self, col_name: str):
        """
        Generate a countplot for a categorical column.

        Parameters
        ----------
        col_name : str
            Column name to visualize.
        """

        if not self.is_valid_countplot(col_name):
            logger.info(f"Skipping countplot: {col_name}")
            return

        plt.figure()
        order = self.dataframe[col_name].value_counts().index
        sns.countplot(x=self.dataframe[col_name], order=order)
        #sns.countplot(x=self.dataframe[col_name])

        plt.xticks(rotation=0)
        plt.title(f"{col_name} Countplot")

        plt.savefig(self.output_dir / f"{col_name}_countplot.png")
        plt.close()

    def plot_pie(self, col_name: str):
        """
        Generate a pie chart for a categorical column.

        Parameters
        ----------
        col_name : str
            Column name to visualize.
        """

        if not self.is_valid_pie(col_name):
            logger.info(f"Skipping pie chart: {col_name}")
            return

        data = self.dataframe[col_name].value_counts()

        plt.figure()

        plt.pie(
            data.values,
            labels=data.index,
            autopct="%1.1f%%",
            startangle=90
        )
        plt.title(f"{col_name} Distribution")

        plt.savefig(self.output_dir / f"{col_name}_pie.png")
        plt.close()

    def plot_scatter(self, col_x: str, col_y: str):
        """
        Generate scatter plot between two numeric columns.

        Parameters
        ----------
        col_x : str
            Column for X-axis.

        col_y : str
            Column for Y-axis.
        """

        if not self.is_valid_scatter(col_x, col_y):
            logger.info(f"Skipping scatter: {col_x} vs {col_y}")
            return

        plt.figure()

        sns.scatterplot(
            x=self.dataframe[col_x],
            y=self.dataframe[col_y]
        )

        plt.title(f"{col_x} vs {col_y}")

        plt.savefig(self.output_dir / f"{col_x}_vs_{col_y}_scatter.png")
        plt.close()

    def plot_heatmap(self):
        """
        Generate correlation heatmap for numeric features.

        Notes
        -----
        The heatmap shows pairwise correlations between
        numeric variables in the dataset.
        """

        if len(self.numeric_columns) < 2:
            return

        corr = self.dataframe[self.numeric_columns].corr()

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            corr,
            annot=True,
            cmap="coolwarm",
            fmt=".2f"
        )

        plt.title("Correlation Heatmap")

        plt.savefig(self.output_dir / "correlation_heatmap.png")
        plt.close()


    def auto_plot(self):
        """
        Automatically generate all suitable plots.

        Workflow
        --------
        1. Iterate through each column
        2. Skip ID-like columns
        3. Generate numeric plots (histogram + boxplot)
        4. Generate categorical plots (countplot + pie)
        5. Generate scatter plots for numeric column pairs
        6. Generate correlation heatmap
        """

        logger.info("Generating plots...")

        # Column-wise plots
        for col in tqdm(self.dataframe.columns,desc="plots"):
            
            if self.is_id_column(col):
                logger.warning(f"Skipping ID column: {col}")
                continue

            if self.check_dtype(col):
                self.plot_histogram(col)
                self.plot_boxplot(col)
            else:
                self.plot_countplot(col)
                self.plot_pie(col)

        # Scatter plots for numeric pairs
        numeric_cols = list(self.numeric_columns)

        for i in tqdm(range(len(numeric_cols)), desc="Scatter plots"):
            for j in range(i + 1, len(numeric_cols)):
                self.plot_scatter(numeric_cols[i], numeric_cols[j])

        # Heatmap
        self.plot_heatmap()

        print("All plots generated successfully.")
    
    def summary(self):
        """
        Give a short summary of the dataset
        """
        print("Rows:", self.dataframe.shape[0])
        print("Columns:", self.dataframe.shape[1])
        print("Numeric:", len(self.numeric_columns))
        print("Categorical:", len(self.categorical_columns))
