import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from io import BytesIO

# ---------------------------------------------------------
# POSTGRES CONNECTION
# ---------------------------------------------------------
def get_conn():
    return psycopg2.connect(
        host="localhost",
        database="techmart_db",
        user="postgres",
        password="Test_12345678",   # <-- PUT YOUR PASSWORD
        port=5432
    )

# ---------------------------------------------------------
# RUN QUERY
# ---------------------------------------------------------
def run_query(sql):
    conn = get_conn()
    try:
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        raise e

# ---------------------------------------------------------
# GET TABLE LIST
# ---------------------------------------------------------
def get_tables():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public';
    """)
    out = [t[0] for t in cur.fetchall()]
    conn.close()
    return out

# ---------------------------------------------------------
# GET COLUMNS FOR A TABLE
# ---------------------------------------------------------
def get_columns(tbl):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='{tbl}';
    """)
    out = [c[0] for c in cur.fetchall()]
    conn.close()
    return out

# ---------------------------------------------------------
# UI CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Premium SQL IDE", layout="wide")
st.title("🌟 Premium SQL IDE — TechMart PostgreSQL Query Builder")
st.write("A complete UI for building & executing SQL visually.")

# Load schema
tables = get_tables()

# ---------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------
left, right = st.columns([1.2, 2.3])

# ---------------------------------------------------------
# LEFT SIDE — QUERY BUILDER PANELS
# ---------------------------------------------------------

with left:
    st.header("🧩 Query Builder")

    # ----- Select tables -----
    selected_tables = st.multiselect("📦 Select table(s)", tables)

    if selected_tables:
        primary_table = selected_tables[0]
    else:
        primary_table = None

    # ----- SELECT Columns + Alias -----
    st.subheader("📑 Select Columns")

    selected_cols = []
    col_alias_map = {}

    if primary_table:
        for tbl in selected_tables:
            with st.expander(f"Columns from {tbl}", expanded=False):
                cols = get_columns(tbl)
                selected = st.multiselect(f"Select columns from {tbl}", cols, key=f"cols_{tbl}")

                for c in selected:
                    alias = st.text_input(f"Alias for {tbl}.{c}", value="", key=f"alias_{tbl}_{c}")
                    col_ref = f"{tbl}.{c}"
                    selected_cols.append(col_ref)
                    if alias.strip() != "":
                        col_alias_map[col_ref] = alias

    # ----- JOIN Builder -----
    st.subheader("🔗 Join Builder")

    join_clauses = []
    if len(selected_tables) > 1:
        for i in range(1, len(selected_tables)):
            t1 = selected_tables[i - 1]
            t2 = selected_tables[i]

            with st.expander(f"Join {t1} → {t2}", expanded=False):
                join_type = st.selectbox(
                    "Join Type",
                    ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"],
                    key=f"join_type_{t1}_{t2}"
                )
                t1_col = st.selectbox(f"{t1} column", get_columns(t1), key=f"{t1}_col_{i}")
                t2_col = st.selectbox(f"{t2} column", get_columns(t2), key=f"{t2}_col_{i}")

                join_clauses.append(f"{join_type} {t2} ON {t1}.{t1_col} = {t2}.{t2_col}")

    # ----- WHERE filter -----
    st.subheader("🔎 Filter (WHERE)")
    where_clause = st.text_area("Write conditions (optional)", "")

    # ----- GROUP BY -----
    st.subheader("📊 GROUP BY")
    group_cols = st.multiselect("Select group by columns", selected_cols)

    # ----- ORDER BY -----
    st.subheader("⬇ ORDER BY")
    order_cols = st.multiselect("Select columns to order", selected_cols)
    order_dir = st.selectbox("Order direction", ["ASC", "DESC"])

    # ----- Window Function -----
    st.subheader("🪟 Window Function")
    win_func = st.selectbox(
        "Choose window function",
        ["None", "ROW_NUMBER()", "RANK()", "DENSE_RANK()", "SUM()", "AVG()"]
    )
    win_over = ""
    if win_func != "None":
        win_over = st.text_input("OVER () clause", "ORDER BY id")

    # ----- CRUD -----
    st.subheader("⚙ Operation")
    op = st.selectbox("SQL Operation", ["SELECT", "UPDATE", "DELETE", "TRUNCATE", "DROP"])


# ---------------------------------------------------------
# RIGHT SIDE — SQL GENERATION + EXECUTION + RESULTS
# ---------------------------------------------------------

with right:
    st.header("📝 Generated SQL")

    sql = ""

    try:
        # ------------------------------------
        # SELECT Query Generator
        # ------------------------------------
        if op == "SELECT":

            # SELECT Columns
            if selected_cols:
                select_part = ", ".join(
                    [f"{c} AS {col_alias_map[c]}" if c in col_alias_map else c for c in selected_cols]
                )
            else:
                select_part = "*"

            sql = f"SELECT {select_part}\nFROM {primary_table}"

            # JOINs
            for j in join_clauses:
                sql += f"\n{j}"

            # WHERE
            if where_clause.strip() != "":
                sql += f"\nWHERE {where_clause}"

            # GROUP BY
            if group_cols:
                sql += "\nGROUP BY " + ", ".join(group_cols)

            # ORDER BY
            if order_cols:
                sql += "\nORDER BY " + ", ".join(order_cols) + f" {order_dir}"

            # WINDOW FUNCTION
            if win_func != "None":
                sql = sql.replace(
                    "SELECT",
                    f"SELECT {win_func} OVER ({win_over}) AS window_value, ",
                    1
                )

        # ------------------------------------
        # UPDATE
        # ------------------------------------
        elif op == "UPDATE":
            sql = f"UPDATE {primary_table} SET column=value"
            if where_clause:
                sql += f" WHERE {where_clause}"

        # ------------------------------------
        # DELETE
        # ------------------------------------
        elif op == "DELETE":
            sql = f"DELETE FROM {primary_table}"
            if where_clause:
                sql += f" WHERE {where_clause}"

        # ------------------------------------
        # TRUNCATE
        # ------------------------------------
        elif op == "TRUNCATE":
            sql = f"TRUNCATE TABLE {primary_table}"

        # ------------------------------------
        # DROP
        # ------------------------------------
        elif op == "DROP":
            sql = f"DROP TABLE {primary_table}"

    except Exception as e:
        st.error(f"❌ Error building SQL: {e}")

    # Show SQL
    st.code(sql, language="sql")

    # Execute Button
    if st.button("▶ Run Query"):
        try:
            df = run_query(sql)
            st.success("Query executed successfully!")

            # Show data
            st.dataframe(df, use_container_width=True)

            # Auto chart
            if df.shape[1] > 1:
                num_cols = df.select_dtypes(include='number').columns
                if len(num_cols) > 0:
                    fig = px.line(df, x=df.columns[0], y=num_cols[0])
                    st.plotly_chart(fig)

            # Export CSV
            csv = df.to_csv(index=False)
            st.download_button("⬇ Download CSV", csv, "result.csv", "text/csv")

        except Exception as e:
            st.error(f"❌ Query Error: {e}")