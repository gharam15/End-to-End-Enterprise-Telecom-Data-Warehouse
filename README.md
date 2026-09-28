# Telecom Data Platform

An end-to-end **Data Engineering Platform** for telecom analytics, built to ingest data from multiple source systems, standardize it in a staging layer, transform it with dbt, orchestrate pipelines with Apache Airflow, store curated analytical models in PostgreSQL, and serve business dashboards through Metabase.

---

## Architecture

![Telecom Data Platform Architecture](<docs/images/telecom_architecture.png>)


The platform follows a layered architecture:

**Data Sources → Python Ingestion / ETL → PostgreSQL Staging → dbt Transformation → PostgreSQL Data Warehouse → Metabase**

Supporting platform components:

- **Apache Airflow** — orchestration, scheduling, retries, branching, source freshness, and final dbt tests
- **dbt Docs** — documentation, tests, metadata catalog, and lineage
- **GitHub** — source control and project repository
- **Docker Compose** — containerized local infrastructure

### Data Lineage & Architecture Views

![Data Lineage](<docs/images/Linage.PNG>)

![Lineage Graph](<docs/images/Linage Graph.PNG>)

---

## Data Sources

The project integrates four main source types:

| Source | Purpose |
|---|---|
| **OpenCellID REST API** | Telecom network cell information |
| **CSV Files** | CDR usage and customer support data |
| **Excel File** | IBM Telco CRM / churn dataset |
| **SQL Server** | Operational billing and CDR source tables |

### SQL Server source objects

- `dbo.billing_transactions`
- `dbo.cdr_usage_raw`
- `dbo.file_load_log`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Programming | Python |
| Operational Database | SQL Server |
| Staging & Data Warehouse | PostgreSQL |
| Transformation | dbt |
| Orchestration | Apache Airflow |
| Visualization | Metabase |
| Documentation & Lineage | dbt Docs |
| Containerization | Docker / Docker Compose |
| Version Control | Git / GitHub |

---

## Python Ingestion Layer

Custom Python scripts are used for extraction, loading, incremental ingestion, and metadata management.

### Main ingestion scripts

```text
scripts/ingestion/
├── ingest_network_to_postgres.py
├── load_cdr_to_sqlserver.py
├── ingest_cdr_to_postgres.py
├── generate_and_load_billing.py
├── ingest_billing_to_postgres.py
└── ingest_support_to_postgres.py
```

### ETL features

- API ingestion
- File ingestion
- Incremental loading
- Watermark logic
- `ingestion_timestamp`
- File load tracking
- Data standardization
- Metadata management

---

## PostgreSQL Staging Layer

Raw and standardized source data is loaded into the `staging` schema.

```text
staging.network_cells
staging.customers
staging.cdr_usage
staging.billing
staging.customer_support
```

The staging layer acts as the landing and standardization layer before analytical modeling.

---

## dbt Transformation Layer

dbt is used to transform, model, test, and document the telecom data.

### Staging models

```text
stg_network_cells
stg_customers
stg_cdr_usage
stg_billing
stg_customer_support
```

### Dimensions

```text
dim_customer
dim_date
dim_cell
dim_cdr_cell
dim_support_category
```

### Facts

```text
fact_billing
fact_cdr_usage
fact_customer_support
```

### Analytical marts

```text
mart_billing_summary
mart_customer_churn
mart_network_usage
mart_support_performance
```

### Important modeling rule

`dim_cell` and `dim_cdr_cell` represent different source domains:

- `dim_cell` → OpenCellID
- `dim_cdr_cell` → Telecom Italia CDR data

They are intentionally kept separate to avoid a false join.

---

## PostgreSQL Data Warehouse

The analytical warehouse is stored in PostgreSQL under the `dw` schema.

It contains:

- Dimension models
- Fact models
- Analytical marts
- Business-ready datasets
- Reusable KPI models

---

## Apache Airflow

Airflow orchestrates the end-to-end data platform.

### DAGs

```text
telecom_network_pipeline
telecom_cdr_pipeline
telecom_billing_pipeline
telecom_support_pipeline
telecom_master_pipeline
```

### Master pipeline flow

```text
Billing ──────┐
CDR ──────────┤
Support ──────┼──> Source Freshness ───> Final dbt Tests
Network ──────┘
```

### Airflow capabilities used

- Scheduled pipeline execution
- Parallel child DAG orchestration
- Retries
- Branching
- No-new-file logic for CDR ingestion
- Source freshness checks
- Final dbt validation
- Pipeline monitoring

### Airflow Pipeline Screenshots

#### Master Pipeline

![Airflow Master Pipeline](<docs/images/Airflow telecom master pipeline.PNG>)

#### Billing Pipeline

![Airflow Billing Pipeline](<docs/images/Airflow telecom billing pipeline.PNG>)

#### CDR Pipeline

![Airflow CDR Pipeline](<docs/images/Airflow telecom cdr pipeline.PNG>)

#### Network Pipeline

![Airflow Network Pipeline](<docs/images/Airflow telecom network pipeline.PNG>)

#### Support Pipeline

![Airflow Support Pipeline](<docs/images/Airflow telecom support pipeline.PNG>)

---

## Data Quality

The platform includes multiple validation layers.

### dbt tests

- Not-null tests
- Unique tests
- Accepted value tests
- Business-rule tests

Examples:

- Billing amounts must not be negative
- CDR activity metrics must not be negative
- Customer support values must be within valid ranges

### Source freshness

Freshness monitoring is configured for:

- `network_cells`
- `cdr_usage`

---

## dbt Docs / Data Catalog

dbt Docs is used for:

- Model descriptions
- Source documentation
- Data tests
- Metadata catalog
- Data lineage
- Dependency graph

Current project metadata:

```text
17 models
5 sources
58 tests
```

### dbt Model Screenshots

#### Customer Billing Fact

![dbt fact billing](<docs/images/dbt fact_billing.PNG>)

#### CDR Cell Dimension

![dbt dim cdr cell](<docs/images/dbt dim_cdr_cell.PNG>)

#### Network Cell Dimension

![dbt dim cell](<docs/images/dbt dim_cell.PNG>)

#### Billing Staging Model

![dbt staging billing](<docs/images/dbt stg_billing.PNG>)

---

## Metabase Dashboards

The final analytical layer is visualized using Metabase.

### Dashboards

1. **Telecom Executive Dashboard**
2. **Billing & Revenue Dashboard**
3. **Customer & Support Dashboard**
4. **Network Usage Dashboard**

### Analytics delivered

- Revenue KPIs
- Billing trends
- Payment status analysis
- Customer churn analysis
- Support performance
- Satisfaction analysis
- Network usage trends
- SMS / call / internet activity
- Top CDR cells

### Dashboard Screenshots

#### Telecom Executive Dashboard

![Telecom Executive Dashboard](<docs/images/Telecom Executive Dashboard.PNG>)

#### Billing & Revenue Dashboard

![Billing and Revenue Dashboard](<docs/images/Biling & Revenue Dashboard.PNG>)

#### Customer & Support Dashboard

![Customer and Support Dashboard](<docs/images/Customer & Support Dashboard.PNG>)

#### Network Usage Dashboard

![Network Usage Dashboard](<docs/images/Network Usage Dashboard.PNG>)

---

## Docker & Docker Compose

The complete platform runs in containers using Docker Compose.

### Services

```text
PostgreSQL
SQL Server
Apache Airflow
dbt
Metabase
dbt Docs
```

Docker provides:

- Isolated services
- Persistent volumes
- Internal service networking
- Port mapping
- Reproducible local setup

---

## Project Structure

```text
telecom-data-platform/
│
├── airflow/
│   └── dags/
│
├── data/
│   ├── raw/
│   └── landing/
│
├── dbt/
│   ├── telecom_dbt/
│   │   ├── models/
│   │   ├── tests/
│   │   └── dbt_project.yml
│   └── profiles.yml
│
├── docs/
│   └── images/
│
├── scripts/
│   └── ingestion/
│
├── .env
├── Dockerfile.airflow
├── docker-compose.yml
└── README.md
```

---

## Running the Project

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd telecom-data-platform
```

### 2. Create `.env`

Create the environment file locally and add the required credentials.

> Do not commit `.env` to GitHub.

### 3. Start the platform

```bash
docker compose up -d --build
```

### 4. Check services

```bash
docker compose ps
```

### 5. Run dbt

```bash
docker exec -it telecom_airflow bash -lc '
cd /opt/airflow/dbt/telecom_dbt &&
dbt run &&
dbt test
'
```

### 6. Generate dbt Docs

```bash
docker exec -it telecom_airflow bash -lc '
cd /opt/airflow/dbt/telecom_dbt &&
dbt docs generate
'
```

---

## Local Services

| Service | URL |
|---|---|
| Airflow | `http://127.0.0.1:8081` |
| Metabase | `http://127.0.0.1:3000` |
| dbt Docs | `http://127.0.0.1:8085` |

---


## Project Goals

This project demonstrates practical experience with:

- Multi-source ingestion
- Python ETL
- Operational SQL Server integration
- PostgreSQL staging and warehousing
- Incremental data loading
- Dimensional modeling
- dbt transformations
- Data quality testing
- Airflow orchestration
- Data catalog and lineage
- Dockerized infrastructure
- BI dashboard development

---

## Author

**Data Engineering Portfolio Project**
