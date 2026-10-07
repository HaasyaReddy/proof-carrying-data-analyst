import os
import pandas as pd


DATA_FOLDER = "data"


# ============================================================
# 1. LOAD DATA FILES
# ============================================================

def load_data_files():

    datasets = {}

    if not os.path.exists(DATA_FOLDER):

        print("ERROR: 'data' folder not found.")

        return datasets


    for filename in os.listdir(DATA_FOLDER):

        file_path = os.path.join(
            DATA_FOLDER,
            filename
        )

        try:

            if filename.lower().endswith(".csv"):

                df = pd.read_csv(file_path)

            elif filename.lower().endswith(".xlsx"):

                df = pd.read_excel(file_path)

            elif filename.lower().endswith(".xls"):

                df = pd.read_excel(file_path)

            else:

                continue


            datasets[filename] = df

            print(f"Loaded: {filename}")
            print(f"Rows: {len(df)}")
            print(f"Columns: {len(df.columns)}")
            print()


        except Exception as e:

            print(
                f"Could not load {filename}: {e}"
            )


    return datasets


# ============================================================
# 2. PROFILE DATASET
# ============================================================

def profile_dataset(filename, df):

    profile = {

        "filename": filename,

        "rows": len(df),

        "columns": list(df.columns),

        "data_types": {},

        "missing_values": {},

        "duplicate_rows": int(
            df.duplicated().sum()
        ),

        "sample": df.head(5).to_dict(
            orient="records"
        )
    }


    for column in df.columns:

        profile["data_types"][column] = (
            str(df[column].dtype)
        )

        missing = int(
            df[column].isna().sum()
        )

        profile["missing_values"][column] = missing


    return profile


# ============================================================
# 3. DETECT DATA TRAPS
# ============================================================

def detect_data_traps(datasets):

    traps = []


    for filename, df in datasets.items():

        # ----------------------------------------------------
        # Duplicate rows
        # ----------------------------------------------------

        duplicate_count = int(
            df.duplicated().sum()
        )


        if duplicate_count > 0:

            traps.append({

                "type": "DUPLICATE_ROWS",

                "file": filename,

                "message":
                f"{duplicate_count} duplicate row(s) "
                f"found in {filename}."
            })


        # ----------------------------------------------------
        # Missing values
        # ----------------------------------------------------

        for column in df.columns:

            missing_count = int(
                df[column].isna().sum()
            )


            if missing_count > 0:

                traps.append({

                    "type": "MISSING_VALUES",

                    "file": filename,

                    "column": str(column),

                    "message":
                    f"Column '{column}' contains "
                    f"{missing_count} missing value(s)."
                })


        # ----------------------------------------------------
        # Possible duplicate IDs
        # ----------------------------------------------------

        possible_id_columns = [

            column
            for column in df.columns
            if "id" in str(column).lower()

        ]


        for column in possible_id_columns:

            duplicate_ids = int(
                df[column].duplicated().sum()
            )


            if duplicate_ids > 0:

                traps.append({

                    "type": "DUPLICATE_ID",

                    "file": filename,

                    "column": str(column),

                    "message":
                    f"Column '{column}' contains "
                    f"{duplicate_ids} repeated ID value(s)."
                })


    return traps


# ============================================================
# 4. CREATE DATA CONTEXT
# ============================================================

def create_data_context(datasets):

    context = []


    for filename, df in datasets.items():

        profile = profile_dataset(
            filename,
            df
        )


        context.append(
            "\n=============================="
        )

        context.append(
            f"FILE: {filename}"
        )

        context.append(
            "=============================="
        )

        context.append(
            f"Rows: {profile['rows']}"
        )

        context.append(
            "Columns: "
            + ", ".join(
                map(
                    str,
                    profile["columns"]
                )
            )
        )

        context.append(
            f"Duplicate rows: "
            f"{profile['duplicate_rows']}"
        )


        context.append(
            "\nData types:"
        )


        for column, dtype in profile[
            "data_types"
        ].items():

            context.append(
                f"- {column}: {dtype}"
            )


        context.append(
            "\nMissing values:"
        )


        for column, count in profile[
            "missing_values"
        ].items():

            if count > 0:

                context.append(
                    f"- {column}: {count}"
                )


        context.append(
            "\nSample records:"
        )


        for row in profile[
            "sample"
        ]:

            context.append(
                str(row)
            )


    return "\n".join(context)