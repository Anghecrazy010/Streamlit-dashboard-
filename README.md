# 📊 Canceled Orders Dashboard

Interactive **Streamlit** dashboard to analyze invoiced, ordered and canceled quantities, with filters by period, warehouse, customer and product family.

🔗 **Live demo:** https://gkddhgkcjkc6jvgqj7fmzy.streamlit.app

> This version uses **sample data** (`data/pedidos_demo.csv`). The original dashboard was fed by SQL from a private network, so that source was replaced with a CSV file to make the project publicly shareable. The app interface and data column names are in Spanish.

## What it shows

- **Key metrics:** invoiced, ordered and canceled quantity for the selected period.
- **Donut chart (% quantity):** share of invoiced vs. canceled quantity.
- **Top 10 customers** by ordered quantity (Plotly bar chart).
- **Filtered data preview** in an expandable table.

### Available filters (sidebar)

| Filter | Behavior |
| --- | --- |
| Year | Single select (defaults to the most recent year) |
| Month | Single select |
| Warehouse | Multi-select (empty = all) |
| Customers | Multi-select (empty = all) |
| Family | Multi-select (empty = all) |

## How the percentage is calculated

```
% invoiced = invoiced quantity / (ordered quantity + canceled quantity) × 100
```

The result is rounded to two decimals and shown in the sidebar donut. If there is no data for the selected filters, the percentage is 0.

## Data

The file `data/pedidos_demo.csv` contains the columns the dashboard uses:

| Column | Description |
| --- | --- |
| `FECHA CREACION` | Order creation date (parsed as a date on load) |
| `CLIENTE` | Customer (empty values are shown as "Sin cliente") |
| `ALMACEN` | Warehouse |
| `FAMILIA` | Product family |
| `CANTIDAD ORDENADA` | Ordered quantity |
| `CANTIDAD FACTURADA` | Invoiced quantity |
| `CANTIDAD CANCELADA` | Canceled quantity |

## Tech stack

- Python
- [Streamlit](https://streamlit.io/)
- Pandas
- Plotly
- Requests (for the optional Auth0 login)

## Project structure

```
.
├── app_prod.py          # Streamlit application
├── requirements.txt     # Dependencies
└── data/
    └── pedidos_demo.csv # Sample data
```

## Run locally

1. Clone the repository and move into the project folder.

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app_prod.py
   ```

5. Open http://localhost:8501 in your browser.

## Optional Auth0 login

The demo is **public by default**. Auth0 login is only enabled when an `[auth0]` section exists in the Streamlit secrets. In that case the app shows a sign-in screen, the user's name and picture in the sidebar, and a sign-out button.

To enable it, create `.streamlit/secrets.toml` (do not commit it to the repository):

```toml
[auth0]
domain = "your-tenant.auth0.com"
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "http://localhost:8501"   # optional
```

If `redirect_uri` is not set, the app defaults to the demo URL on Streamlit Cloud. When running locally, set `redirect_uri` and also add it to the *Allowed Callback URLs* of your Auth0 application.

## Author

**Anghelo Rodríguez** · [GitHub](https://github.com/Anghecrazy010) · [LinkedIn](https://linkedin.com/in/anghelo-rodríguez-388045225)
