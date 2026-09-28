import os
import random

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Load CRM source data
crm_path = "data/raw/crm/Telco_customer_churn.xlsx"

crm_df = pd.read_excel(crm_path)


# Standardize column names
crm_df.columns = (
    crm_df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


# Select required billing fields
billing_base = crm_df[
    [
        "customerid",
        "contract",
        "payment_method",
        "monthly_charges",
        "total_charges",
        "tenure_months"
    ]
].copy()


# Latest allowed billing month
end_date = pd.Timestamp("2026-12-01")

billing_records = []


# Generate billing records
for _, row in billing_base.iterrows():

    customer_id = row["customerid"]
    tenure_months = int(row["tenure_months"])

    if tenure_months <= 0:
        continue

    # Generate historical billing periods ending in Dec 2026
    start_date = end_date - pd.DateOffset(
        months=tenure_months - 1
    )

    billing_dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS"
    )

    for invoice_date in billing_dates:

        billing_period = invoice_date.strftime("%Y-%m")

        # Make generated payment status deterministic
        random.seed(
            f"{customer_id}-{billing_period}"
        )

        payment_status = random.choice(
            [
                "Paid",
                "Paid",
                "Paid",
                "Pending",
                "Late"
            ]
        )

        monthly_charges = float(
            row["monthly_charges"]
        )

        late_fee = (
            round(monthly_charges * 0.05, 2)
            if payment_status == "Late"
            else 0
        )

        total_amount = round(
            monthly_charges + late_fee,
            2
        )

        billing_records.append(
            {
                "customer_id": customer_id,
                "invoice_date": invoice_date.date(),
                "due_date": (
                    invoice_date
                    + pd.Timedelta(days=14)
                ).date(),
                "billing_period": billing_period,
                "monthly_charges": monthly_charges,
                "total_amount": total_amount,
                "payment_status": payment_status,
                "payment_method": row["payment_method"],
                "late_fee": late_fee,
                "contract": row["contract"],
            }
        )


# Create billing dataframe
billing_df = pd.DataFrame(
    billing_records
)


# Validate generated data
print(
    "Generated rows:",
    len(billing_df)
)

print(
    "Billing period:",
    billing_df["invoice_date"].min(),
    "->",
    billing_df["invoice_date"].max()
)


# Load environment variables
load_dotenv()

sqlserver_password = os.getenv(
    "SQLSERVER_SA_PASSWORD"
)

if not sqlserver_password:
    raise ValueError(
        "SQLSERVER_SA_PASSWORD was not found in .env"
    )


# SQL Server connection
connection_url = URL.create(
    "mssql+pyodbc",
    username="sa",
    password=sqlserver_password,
    host="127.0.0.1",
    port=1433,
    database="telecom_source_db",
    query={
        "driver": "ODBC Driver 18 for SQL Server",
        "TrustServerCertificate": "yes",
        "Encrypt": "yes"
    }
)


engine = create_engine(
    connection_url,
    fast_executemany=True
)


# Load billing data into SQL Server
billing_df.to_sql(
    "billing_transactions",
    con=engine,
    schema="dbo",
    if_exists="append",
    index=False,
    chunksize=5000
)


print(
    "Billing data loaded successfully into SQL Server."
)

print(
    "Rows loaded:",
    len(billing_df)
)