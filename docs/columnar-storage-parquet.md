# A Deep Dive into Columnar Storage: Why Parquet is a Game-Changer for Data Engineers# Understanding Columnar Storage Formats: A Practical Guide

Struggling with slow queries on large datasets? You're not alone. As data volumes grow, the tools and formats we use to store and access that data become critical. While row-oriented formats like CSV are familiar and easy to use, they often become a bottleneck for analytical workloads.Columnar storage formats like Parquet and ORC have revolutionized data engineering by offering significant advantages over traditional row-oriented formats like CSV. This blog post explores the key benefits of columnar storage, demonstrates its practical applications, and explains why it is the industry standard for analytical workloads.

In this post, we'll explore the world of columnar storage, a technology that fundamentally changes how we handle large-scale data. We'll break down why formats like Apache Parquet are the industry standard for data engineers and data scientists, and we'll walk through practical, hands-on examples to demonstrate the dramatic improvements in storage efficiency and query performance.---

Here’s what we’ll cover:## Introduction

- **The Core Concept:** An intuitive analogy to understand the difference between row and columnar storage.In the world of data engineering, the choice of storage format can have a profound impact on performance and efficiency. While row-oriented formats like CSV are common for data interchange, columnar formats are optimized for analytical queries. This post will:

- **Practical Comparison:** A head-to-head comparison of CSV and Parquet, looking at file size, and query speed.

- **The Power of Column Pruning:** A demonstration of how columnar formats speed up queries by reading only the data you need.- Explain the differences between row and column-oriented storage.

- **Schema Evolution:** How Parquet handles changes in your data structure over time.- Highlight the advantages of columnar formats.

* Provide hands-on demonstrations using Polars and Apache Arrow.

---

## Understanding Row vs Column-Oriented Storage

## The Phone Book Analogy: Understanding the Difference

Before we dive into code, let's use a simple analogy to understand the fundamental difference between row-oriented and column-oriented storage.

Imagine you have two different versions of a phone book:

1.  **Traditional Phone Book (Row-oriented)**

    - Each entry contains: `(Name, Address, Phone Number)`
    - Data is stored as complete records, one after another.
    - This is great for looking up all the information about one person. If you want to find John Doe's address and phone number, you find his entry, and all the data is right there.
    - However, it's very inefficient for analytical questions like "What is the most common street name in this phone book?" To answer that, you'd have to read every single record just to extract the address.

2.  **Specialized Index (Column-oriented)**
    - Instead of one big book, you have separate, specialized lists: one for all the names, one for all the addresses, and one for all the phone numbers.
    - Each type of data is stored together.
    - This structure is perfect for analytical queries. To find the most common street, you only need to look at the "addresses" list, completely ignoring the names and phone numbers. This dramatically reduces the amount of data you need to read.
    - Furthermore, because similar data is grouped together (e.g., a list of numbers), it can be compressed much more effectively.

This is precisely how row-oriented formats like CSV and columnar formats like Apache Parquet differ in how they lay out data on disk. Now, let's see this in practice.

---

## Core Advantages of Columnar Storage

### 1. I/O Efficiency (Column Pruning)

Columnar formats allow you to read only the columns needed for a query, drastically reducing I/O. This is particularly beneficial for wide datasets with many columns.

### 2. Compression Efficiency

Grouping similar data types together enables better compression ratios. For example, storing all integers together results in more efficient encoding.

### 3. Schema Evolution

Columnar formats like Parquet handle schema changes gracefully, allowing you to add or remove columns without breaking existing pipelines.

---

## Setting Up Our Experiment: Data Generation

To test the differences between CSV and Parquet, we first need a dataset. We'll generate a sample dataset using Python with the help of the `polars` and `numpy` libraries. Our dataset will have 100,000 rows and 50 columns, containing a mix of integer, float, categorical, and datetime data types. This variety will give us a realistic basis for our comparison.

First, let's set up our environment and import the necessary libraries.

```python
# Import required libraries
import polars as pl
import numpy as np
import os
import time
from datetime import datetime, timedelta

# Configuration
SEED = 42
np.random.seed(SEED)

# File paths
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, "sample_data.csv")
PARQUET_PATH = os.path.join(DATA_DIR, "sample_data.parquet")

# Dataset parameters
N_ROWS = 100_000
N_COLS = 50
```

Now, here is the function we'll use to generate the DataFrame:

```python
def generate_sample_data(n_rows: int, n_cols: int) -> pl.DataFrame:
    """
    Generate a sample DataFrame with various data types.
    """
    n_per_type = n_cols // 4

    int_cols = {
        f"int_col_{i}": np.random.randint(0, 1000000, n_rows)
        for i in range(n_per_type)
    }
    float_cols = {
        f"float_col_{i}": np.random.normal(0, 1, n_rows)
        for i in range(n_per_type)
    }
    categories = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    cat_cols = {
        f"cat_col_{i}": np.random.choice(categories, n_rows)
        for i in range(n_per_type)
    }
    base_date = datetime(2023, 1, 1)
    date_cols = {
        f"date_col_{i}": [
            base_date + timedelta(days=np.random.randint(0, 365))
            for _ in range(n_rows)
        ]
        for i in range(n_per_type)
    }

    data = {**int_cols, **float_cols, **cat_cols, **date_cols}
    df = pl.DataFrame(data)
    return df

# Generate the sample dataset
print("Generating sample dataset...")
df = generate_sample_data(N_ROWS, N_COLS)
print(f"Generated dataset shape: {df.shape}")
```

With our dataset generated, we can now move on to the core of our comparison.

---

## Practical Demonstration

## CSV vs. Parquet: A Head-to-Head Comparison

Now that we have our dataset, let's write it to both a CSV file and a Parquet file and compare the results.

### Round 1: File Size

The first and most immediately obvious difference is the storage space required for each format.

```python
# Helper function for file size formatting
def format_size(size_in_bytes):
    """Convert size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} GB"

# Write to CSV and Parquet
print("Writing files...")
df.write_csv(CSV_PATH)
df.write_parquet(PARQUET_PATH)

# Compare file sizes
csv_size = os.path.getsize(CSV_PATH)
parquet_size = os.path.getsize(PARQUET_PATH)

print("\nFile size comparison:")
print(f"CSV size: {format_size(csv_size)}")
print(f"Parquet size: {format_size(parquet_size)}")
print(f"Compression ratio: {csv_size / parquet_size:.2f}x")
```

When you run this code, you'll see a significant difference. For our sample dataset, the output looks something like this:

```
File size comparison:
CSV size: 355.43 MB
Parquet size: 25.53 MB
Compression ratio: 13.92x
```

The Parquet file is nearly **14 times smaller** than the CSV file. This is because Parquet uses highly efficient, type-aware compression. By grouping data of the same type together, it can apply encoding strategies (like dictionary encoding for categorical data and run-length encoding for repeated values) that are far more effective than the generic compression that can be applied to a text-based format like CSV.

### Round 2: Full Read Performance

Next, let's see how long it takes to read the entire dataset back into memory from each file format. We'll use a simple decorator to time the operations.

```python
def measure_read_time(func):
    """Decorator to measure execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Time taken: {(end_time - start_time):.4f} seconds")
        return result
    return wrapper

# Read complete files
print("Reading complete CSV file:")
@measure_read_time
def read_csv():
    return pl.read_csv(CSV_PATH)

csv_df = read_csv()

print("\nReading complete Parquet file:")
@measure_read_time
def read_parquet():
    return pl.read_parquet(PARQUET_PATH)

parquet_df = read_parquet()
```

The results are again quite telling:

```
Reading complete CSV file:
Time taken: 0.9314 seconds

Reading complete Parquet file:
Time taken: 0.1458 seconds
```

Reading the Parquet file is over **6 times faster**. This is because the Parquet format is structured for efficient reading. It contains metadata that allows the reader to understand the structure of the file without having to parse the entire thing. CSV files, on the other hand, must be parsed line by line, which is a much slower process.

### The Power of Column Pruning

The real magic of columnar storage shines when you don't need to read the entire dataset. In most analytical queries, you're only interested in a small subset of columns. This is where **column pruning** (also known as column projection) comes into play.

Because a Parquet file stores data in columns, the reader can directly access and read only the columns you specify, completely skipping over the data for the columns you don't need. A CSV reader, in contrast, has to read every row and then discard the unwanted columns, which is far less efficient.

Let's test this by reading just 5 of our 50 columns.

```python
# Test column pruning with 5 columns
columns_to_read = df.columns[:5]

print(f"\nReading {len(columns_to_read)} columns from CSV:")
@measure_read_time
def read_csv_columns():
    return pl.read_csv(CSV_PATH, columns=columns_to_read)

csv_subset = read_csv_columns()

print(f"\nReading {len(columns_to_read)} columns from Parquet:")
@measure_read_time
def read_parquet_columns():
    return pl.read_parquet(PARQUET_PATH, columns=columns_to_read)

parquet_subset = read_parquet_columns()
```

The performance difference is staggering:

```
Reading 5 columns from CSV:
Time taken: 0.8951 seconds

Reading 5 columns from Parquet:
Time taken: 0.0287 seconds
```

Reading a subset of columns from the CSV file takes almost as long as reading the entire file. But with Parquet, the time taken is dramatically reduced—it's over **30 times faster** in this case. This is because the Parquet reader only had to read about 10% of the data, whereas the CSV reader still had to process the entire file.

This is the single most important advantage of columnar formats for analytical workloads. When you're querying a table with hundreds of columns but only need a few, the performance gains are enormous.

### Schema Evolution

```python
# Add a new column
df_new = df.with_columns([pl.lit("new_column").alias("extra_col")])
df_new.write_parquet("data/evolved_schema.parquet")

# Compare schemas
original_schema = pl.read_parquet(PARQUET_PATH).schema
new_schema = pl.read_parquet("data/evolved_schema.parquet").schema
print("Original schema:", original_schema)
print("New schema:", new_schema)
```

---

## Handling the Real World: Schema Evolution

Data is rarely static. Over time, you might need to add new columns to your dataset, remove old ones, or even change data types. Columnar formats like Parquet are designed to handle this **schema evolution** gracefully.

The schema (the structure of the data, including column names and types) is stored within the Parquet file itself. This self-describing nature makes it robust to changes.

Let's demonstrate by adding a new column to our DataFrame and saving it as a new Parquet file.

```python
# Add a new column
df_new = df.with_columns([
    pl.lit("new_value").alias("extra_col")
])

# Write to a new Parquet file
new_parquet_path = os.path.join(DATA_DIR, "evolved_schema.parquet")
df_new.write_parquet(new_parquet_path)

# Read the new file and check the schema
new_schema = pl.read_parquet(new_parquet_path).schema
print("New schema (with added column):")
print(new_schema)
```

You can read this new file, and the new column will be present. Crucially, older code that is not aware of the new column can still read the file and will simply ignore it. You can even select just the original columns from the new file, and column pruning will work as expected.

This flexibility is invaluable in production environments where data structures are constantly evolving.

## Conclusion: Why Columnar Storage is a Must-Know for Data Engineers

Through our practical demonstration, we've seen the clear and compelling advantages of using a columnar storage format like Parquet over a traditional row-oriented format like CSV for analytical workloads:

1.  **Drastically Smaller File Sizes:** Thanks to efficient, type-aware compression, Parquet files can be an order of magnitude smaller, saving significant storage costs.
2.  **Massively Faster Query Performance:** The ability to perform column pruning means that queries that select a subset of columns are significantly faster, as the reader only accesses the data it needs.
3.  **Built-in Schema Flexibility:** Parquet's self-describing nature allows it to handle schema evolution gracefully, a common requirement in real-world data pipelines.
4.  **Type Safety:** Parquet preserves data types, preventing the kind of errors that can crop up when reading and writing data to and from text-based formats.

While CSV still has its place for data interchange and simple, human-readable tables, for any serious analytical work, columnar storage is the undisputed champion. As a data engineer, mastering formats like Parquet is not just a good idea—it's a fundamental skill for building efficient, scalable, and robust data systems.
