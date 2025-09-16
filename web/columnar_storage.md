# Plan: Notebook for Columnar Storage Formats

As the lead data engineer, I've outlined a plan for a new notebook to cover the crucial topic of columnar storage formats.

### 1. Is This Concept Important?

**Yes, absolutely.** Understanding columnar storage is fundamental for any data engineer. Row-oriented formats like CSV are common for data interchange, but for analytical queries, which form the backbone of our work, columnar formats like Parquet and ORC are the industry standard.

Adding this notebook is a high-priority task. It addresses a core concept that directly impacts storage efficiency and query performance, providing significant value to our audience.

### 2. Prerequisite Topics

To ensure learners get the most out of this notebook, they should first be familiar with:

1.  **Row-Oriented Formats:** A basic understanding of formats like CSV and JSON is necessary to appreciate the benefits of columnar storage. A brief introductory notebook comparing them could be a good precursor.
2.  **Basic Data Manipulation:** Familiarity with a DataFrame library (like Pandas or Polars) is essential for the practical exercises. The existing `graph_polars.ipynb` serves as a good foundation.

### 3. Key Concepts to Address

The notebook should be structured to cover the following aspects logically:

1.  **Introduction: The "Why"**
    *   Start with a simple analogy to explain the concept.

        ### The Analogy: Two Ways to Take Notes at a Conference

        Imagine you're at a conference with 1,000 attendees. Your job is to take notes on each person: their **Name**, their **Company**, and the **Topic** they're most interested in.

        ---

        #### 1. Row-Oriented Storage: The Index Card Method

        This is the traditional way you'd take notes.

        *   You get a stack of 1,000 index cards.
        *   For the first person you meet, you take one card and write down all their information:
            *   **Card 1:** `Name: Alice | Company: Acme Inc. | Topic: AI Ethics`
        *   For the second person, you do the same on a new card:
            *   **Card 2:** `Name: Bob | Company: Beta Corp. | Topic: Data Pipelines`
        *   ...and so on for all 1,000 attendees.

        Each card is a **row**, and all the information for a single attendee is physically grouped together.

        **Now, the boss asks a question: "How many attendees are interested in 'Data Pipelines'?"**

        To answer, you have to pick up *every single one of the 1,000 cards*, read the whole card (Name, Company, and Topic), and make a tick mark if the topic is "Data Pipelines". You're forced to read through a lot of data you don't need (Names and Companies) just to find the answer.

        ---

        #### 2. Columnar Storage: The Separate Notebooks Method

        This is a completely different way to organize the same information.

        *   Instead of index cards, you have three separate, single-subject notebooks: one labeled "Names", one "Companies", and one "Topics".
        *   When you meet the first person, you write their info in the corresponding notebook on the first line of each.
            *   **Names Notebook, Line 1:** `Alice`
            *   **Companies Notebook, Line 1:** `Acme Inc.`
            *   **Topics Notebook, Line 1:** `AI Ethics`
        *   When you meet the second person, you use the second line of each notebook:
            *   **Names Notebook, Line 2:** `Bob`
            *   **Companies Notebook, Line 2:** `Beta Corp.`
            *   **Topics Notebook, Line 2:** `Data Pipelines`

        The data for a single person is now spread out, but linked by its position (line number). Each notebook is a **column**.

        **Now, the boss asks the same question: "How many attendees are interested in 'Data Pipelines'?"**

        To answer, you completely ignore the "Names" and "Companies" notebooks. You only pick up the **"Topics" notebook** and scan down that single list, counting the occurrences of "Data Pipelines".

        This is incredibly fast because you only read the exact data required to answer the question.

        ---

        ### Why It Matters for Data Engineering

        | Feature | Row-Oriented (Index Cards) | Columnar (Notebooks) |
        | :--- | :--- | :--- |
        | **Use Case** | Best for **transactional** work (OLTP). E.g., "Show me everything about Alice." You just grab her one card. | Best for **analytical** work (OLAP). E.g., "What's the average of X across all users?" You just grab the "X" notebook. |
        | **Query Speed** | Slow for queries that only need a few columns from a wide table. | Extremely fast for analytical queries that aggregate or read a subset of columns. |
        | **Compression** | Harder to compress. Data on one card is diverse (text, numbers, dates). | Highly compressible. The "Topics" notebook has lots of repeating values, which are easy to compress. |
    *   Visually illustrate the difference between how data is laid out on disk for row vs. columnar formats.

2.  **Core Advantages (The "How")**
    *   **I/O Efficiency (Column Pruning):** Demonstrate how analytical queries that select a subset of columns only read the data they need, drastically reducing I/O. This is the most important concept to land.
    *   **Compression Efficiency:** Show how grouping data of the same type (e.g., all integers, all strings) leads to much better compression ratios. Compare the file size of a dataset saved as CSV vs. Parquet.
    *   **Schema Evolution: The Key to Building Robust Data Pipelines**

        #### Part 1: What is Schema Evolution?

        A **schema** is the blueprint of your data: its column names and their data types (e.g., `user_id` is an Integer, `email` is a String). **Schema Evolution** is the inevitable reality that this blueprint will change over time as business needs evolve.

        It's one of the most critical concepts for data engineers because it's the difference between a brittle, high-maintenance data platform and a robust, agile one.

        Common types of schema changes include:
        *   **Adding a new column:** A safe, backward-compatible change. Old data can be read by new code, which will typically see `null` values for the new column.
        *   **Removing a column:** Can be a breaking change if downstream consumers expect it.
        *   **Renaming a column:** A breaking change.
        *   **Changing a column's data type:** A breaking change (e.g., changing a String to an Integer).

        Formats like Parquet are specifically designed to handle these changes gracefully, especially the most common case of adding new columns.

        #### Part 2: A Real-World Use Case

        **The Scenario:** Imagine we have an application with millions of users. When we first launched (V1), we only collected basic information. Our data pipeline processes files with this simple V1 schema:
        *   `user_id` (Integer)
        *   `username` (String)

        **The New Business Need:** The product team now wants to analyze user retention. To do this, they need to know when each user signed up. This requires adding a new column to our data, creating a V2 schema:
        *   `user_id` (Integer)
        *   `username` (String)
        *   `signup_date` (Date)

        **The Challenge with CSV:** If our data is in CSV files, our pipeline is in trouble. When our V2 processing code (which expects three columns) tries to read an old V1 file (which only has two), it will crash or produce corrupted data. We would be forced into a costly and risky manual data migration project.

        **The Parquet Solution:** Parquet files are **self-describing**. The schema is stored in the file's metadata. This allows us to build a robust pipeline that can inspect the data's schema *before* processing it, and adapt on the fly.

        #### Part 3: Code Demonstration - Brittle CSV vs. Robust Parquet

        This code simulates our V2 application trying to read an old V1 file.

        ```python
        import polars as pl
        from pathlib import Path
        import os

        # --- Setup: Define schemas and create a V1 data file ---
        V1_SCHEMA = {"user_id": pl.Int64, "username": pl.Utf8}
        V2_SCHEMA = {"user_id": pl.Int64, "username": pl.Utf8, "signup_date": pl.Date}
        CSV_V1_FILE = Path("user_v1.csv")
        PARQUET_V1_FILE = Path("user_v1.parquet")
        df_v1 = pl.DataFrame({"user_id": [1, 2], "username": ["alice", "bob"]})
        df_v1.write_csv(CSV_V1_FILE)
        df_v1.write_parquet(PARQUET_V1_FILE)

        # --- 1. The Brittle CSV Approach ---
        print("--- Attempting to process CSV with V2 logic (will fail) ---")
        try:
            # V2 app hardcodes the columns it wants. This fails because
            # `signup_date` does not exist in the V1 CSV.
            df = pl.read_csv(CSV_V1_FILE, columns=list(V2_SCHEMA.keys()))
        except Exception as e:
            print(f"FAILED to process {CSV_V1_FILE}. Error: {e}")

        # --- 2. The Robust Parquet Approach (Backward Compatibility) ---
        print("\n--- Robustly processing Parquet with V2 logic ---")
        # Step A: Read ONLY the schema from the Parquet file. This is fast.
        file_schema = pl.read_parquet_schema(PARQUET_V1_FILE)
        
        # Step B: Reconcile the actual schema with the expected V2 schema.
        expected_cols, present_cols = set(V2_SCHEMA.keys()), set(file_schema.keys())
        missing_cols = expected_cols - present_cols
        
        # Step C: Read present columns and add missing ones as null.
        df = pl.read_parquet(PARQUET_V1_FILE, columns=list(present_cols))
        if missing_cols:
            print(f"Schema difference detected. Missing: {missing_cols}. Adding them with nulls.")
            df = df.with_columns([
                pl.lit(None, dtype=V2_SCHEMA[col]).alias(col) for col in missing_cols
            ])
        
        df = df.select(list(V2_SCHEMA.keys())) # Ensure final column order
        print(f"Successfully processed {PARQUET_V1_FILE}. Final DataFrame:\n{df}")

        # Cleanup
        os.remove(CSV_V1_FILE); os.remove(PARQUET_V1_FILE)
        ```

        #### Part 4: The "Magic" Explained: `read_parquet_schema` vs. `read_csv(n_rows=0)`

        The key to the robust Parquet approach is the `pl.read_parquet_schema()` function. You might think the trick `pl.read_csv("file.csv", n_rows=0)` is equivalent, but it's not.

        The critical difference is **data types**.

        *   **`read_parquet_schema()`** reads the rich, typed schema stored in the Parquet metadata. It knows `user_id` is an `Int64`.
        *   **`read_csv(n_rows=0)`** only reads the header row. It has no information about types and defaults everything to `Utf8` (string).

        | Feature | `pl.read_csv(n_rows=0)` | `pl.read_parquet_schema()` |
        | :--- | :--- | :--- |
        | **Schema Info** | Returns only column **names**. | Returns column **names and data types**. |
        | **Data Types** | All columns default to `Utf8` (string). | Returns the true, accurate data types. |
        | **Reliability** | Relies on a **convention** (first line is a header). | Relies on a **specification** (schema is required). |

        This ability to retrieve a full, typed schema efficiently is what enables robust, adaptive data pipelines.

3.  **Practical Demonstration**
    *   Generate a sample dataset with a variety of data types and a significant number of columns.
    *   **Task 1 (File Size):** Write the dataset to both CSV and Parquet. Compare the resulting file sizes on disk.
    *   **Task 2 (Query Speed):** Run identical analytical queries against both files (e.g., an aggregation on one column after filtering on another). Time and compare the execution speed to highlight the performance gains.

### 4. Recommended Tools

*   **Primary Library: Polars**
    *   We should use **Polars** for this demonstration. It has native, high-performance readers for both CSV and Parquet, making the comparison direct and easy. It's also consistent with the existing `graph_polars.ipynb`.
*   **Underlying Technology: Apache Arrow**
    *   While we'll use Polars for the user-facing API, it's important to mention that **Apache Arrow** is the underlying technology that powers in-memory columnar analytics and the Parquet file format in the Python ecosystem. We should briefly explain its role as the "glue" that makes this ecosystem so efficient.
*   **Dataset:** We should use a dataset that is wider than it is long (e.g., 50 columns, 100,000 rows) to make the benefits of column pruning immediately obvious. The NYC Taxi dataset is a classic and effective choice for this.
