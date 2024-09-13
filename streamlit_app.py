import streamlit as st
from pandas import DataFrame
from pymysql import connect

DB_HOST = "tellmoredb.cd24ogmcy170.us-east-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASS = "2yYKKH8lUzaBvc92JUxW"
DB_PORT = "3306"
DB_NAME = "claires"
CONVO_DB_NAME = "store_questions"

CLAIRE_DEEP_PURPLE = "#553D94"
CLAIRE_MAUVE = "#D2BBFF"

st.set_page_config(
    layout = 'wide', 
    initial_sidebar_state = 'collapsed',
    page_title = 'Store Manager App',
    page_icon = 'claires-logo.svg',
)

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'display_df_and_nlr' not in st.session_state:
    st.session_state['display_df_and_nlr'] = False

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""

def connect_to_db(db_name):
    return connect(
        host = DB_HOST,
        port = int(DB_PORT),
        user = DB_USER,
        password = DB_PASS,
        db = db_name
    )

def set_custom_css():
    custom_css = """
    <style>
        .st-emotion-cache-9aoz2h.e1vs0wn30 {
            display: flex;
            justify-content: center; /* Center-align the DataFrame */
        }
        .st-emotion-cache-9aoz2h.e1vs0wn30 table {
            margin: 0 auto; /* Center-align the table itself */
        }

        .button-container {
            display: flex;
            justify-content: flex-end; /* Align button to the right */
            margin-top: 10px;
        }

        .circular-button {
            border-radius: 50%;
            background-color: #553D94; /* Button color */
            color: white;
            border: none;
            padding: 10px 15px; /* Adjust size as needed */
            cursor: pointer;
        }

        .circular-button:hover {
            background-color: #452a7f; /* Slightly darker shade on hover */
        }
        </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def store_manager_app():
    with open(r'claires-logo.svg', 'r') as image:
        image_data = image.read()
    st.logo(image=image_data)

    store_questions = {
        "Select a query": None,
        "What is the sum of number of transactions this year compared to last year for the store THE PIKE OUTLETS?": {
            "sql": "SELECT SUM(f.TransactionCountTY) AS TotalTransactionsTY, SUM(f.TransactionCountLY) AS TotalTransactionsLY FROM fact_Basket f JOIN dim_Location_Latest l ON f.LocationLatestKey = l.LocationLatestKey WHERE l.LatestLocation = 'THE PIKE OUTLETS';",
            "nlr": "The data table returned indicates that for the latest location of the store, THE PIKE OUTLETS, there were a total of 7,213 transactions this year, while there were no transactions recorded last year. This suggests a significant increase in activity at this location compared to the previous year.",
            
        },
        "What are the net margins in USD for the store THE PIKE OUTLETS?": {
            "sql": "SELECT f.NetExVATUSDPlan FROM Fact_Store_Plan f JOIN dim_Location_Latest l ON f.LocationLatestKey = l.LocationLatestKey WHERE l.LatestLocation = 'THE PIKE OUTLETS';",
            "nlr": "The data table returned consists of a series of net margin values in USD for the store located at THE PIKE OUTLETS. The values are presented in a single column, with some margins appearing multiple times, indicating that there may be repeated entries for certain periods or transactions.\n\nThe margins range from as low as 0.0 to as high as 16700.54, suggesting a significant variation in performance. Notably, there are several entries with a value of 0.0, which may indicate periods of no profit or data not being recorded. The presence of multiple identical values, such as 10975.71 and 12232.21, could imply consistent performance during specific timeframes.\n\nOverall, this data provides a snapshot of the financial performance of the store, highlighting both profitable and unprofitable periods.",
        },
        "What is the net sales on July 31, 2023 compared to the same period last year for the store THE PIKE OUTLETS?":
        {
            "sql": "SELECT f.NetSaleLocal, f.NetSaleLocalLY FROM fact_Sale f JOIN dim_Calendar c ON f.CalendarKey = c.CalendarKey JOIN dim_Location_Latest l ON f.LocationLatestKey = l.LocationLatestKey WHERE l.LatestLocation = 'THE PIKE OUTLETS' AND c.CalendarDate = '2023-07-31';",
            "nlr": "On July 31, 2023, the net sales in USD for the latest location of the store THE PIKE OUTLETS were as follows: 65.00, 242.96, and 1197.18. In comparison, there were no net sales recorded for the same period last year."
        },
        "What is the Daily Sales Report (DSR) using our sales records for the store THE PIKE OUTLETS on July 31, 2023?": {
            "sql": "SELECT f.NetSaleLocal, f.NetSaleUSD, f.NetQuantity, c.CalendarDate FROM fact_Sale f JOIN dim_Calendar c ON f.CalendarKey = c.CalendarKey JOIN dim_Location_Latest l ON f.LocationLatestKey = l.LocationLatestKey WHERE l.LatestLocation = 'THE PIKE OUTLETS' AND c.CalendarDate = '2023-07-31';",
            "nlr": "The data table returned provides a summary of sales transactions for the store at THE PIKE OUTLETS on July 31, 2023. Each row represents a distinct sales record for that day.\n\nThe first row indicates a total sales amount of USD 65.00, with a quantity of 4 items sold. The second row shows sales of USD 242.96, also with a quantity of 4 items sold. The third row reflects a significantly higher total sales amount of USD 1,197.18, with a quantity of 153 items sold.\n\nAll entries are dated July 31, 2023, suggesting that these transactions occurred on the same day. This data illustrates the range of sales activity at the store, highlighting both lower and higher sales volumes for that date.",
        },
        "Compare the average sales revenue for the store THE PIKE OUTLETS with the average sales revenue for all stores in USA.": {
            "sql": "SELECT AVG(fs.NetSaleUSD) AS AverageSalesRevenue FROM fact_Sale fs JOIN dim_Location_Latest dl ON fs.LocationLatestKey = dl.LocationLatestKey WHERE dl.LatestLocation = 'THE PIKE OUTLETS' \nGROUP BY dl.LatestCountry\nUNION\nSELECT AVG(fs.NetSaleUSD) AS AverageSalesRevenue FROM fact_Sale fs JOIN dim_Location_Latest dl ON fs.LocationLatestKey = dl.LocationLatestKey WHERE dl.LatestCountry = 'USA';",
            "nlr": "The data table returned two values representing average sales revenue. The first value, approximately 450.18, corresponds to the average sales revenue for the store located at THE PIKE OUTLETS. The second value, approximately 471.99, represents the average sales revenue for all stores located in the USA. This comparison indicates that the average sales revenue for THE PIKE OUTLETS is lower than the average for all stores in the country.",
        },
        "What were the sales during the 'Autumn/Winter' season for the store THE PIKE OUTLETS?": {
            "sql": "SELECT dll.LatestLocation,SUM(f.NetSaleUSD) as TotalSales, d.Season, d.FiscalMonthName, d.FiscalYear \nFROM fact_Sale f JOIN dim_Calendar d ON f.CalendarKey = d.CalendarKey JOIN dim_Location_Latest dll ON f.LocationLatestKey =dll.LocationLatestKey WHERE d.Season = 'Autumn/Winter' AND f.LocationLatestKey = (SELECT LocationLatestKey FROM dim_Location_Latest dll WHERE dll.LatestLocation = 'THE PIKE OUTLETS') GROUP BY d.FiscalMonthName, d.FiscalYear ORDER BY d.FiscalYear DESC, d.FiscalMonthName;",
            "nlr": "The data table returned provides sales figures for the 'Autumn/Winter' season at the store located at THE PIKE OUTLETS. It shows two entries: the first entry indicates that in August 2023, the store achieved sales of USD 4,105.16 during the Autumn/Winter season. The second entry reveals that in January 2022, the store recorded sales of USD 3,522.25 for the same season. This data highlights the sales performance of THE PIKE OUTLETS during the Autumn/Winter season across two different years.",
        },
        "What is the average number of units sold per transaction at the store THE PIKE OUTLETS?": {
            "sql": "SELECT AVG(f.TransactionCountTY) AS AverageUnitsSold FROM fact_Basket f\nJOIN dim_Location_Latest d ON f.LocationLatestKey = d.LocationLatestKey\nWHERE d.LatestLocation = 'THE PIKE OUTLETS';",
            "nlr": "The data table returned indicates that the average number of units sold per transaction at the latest location of store THE PIKE OUTLETS is approximately 38.37. This figure suggests that, on average, each transaction at this location involves the sale of around 38 units.",
        },
    }

    if 'queries' not in st.session_state:
        st.session_state['queries'] = {}

    st.markdown(f"""
    <h4 style="background-color: {CLAIRE_DEEP_PURPLE}; color: white; padding: 10px;">
        STORE MANAGER
    </h4>
    """, unsafe_allow_html=True)

    store_name_id_placeholder = st.markdown(f"""
    <h4 style="background-color: {CLAIRE_MAUVE}; color: black; padding: 10px;">
    </h4>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        div.stButton {
            display: flex;
            justify-content: flex-end; /* Align button to the right */
            font-size: 30px; /* Increase font size */
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    store_name_id_placeholder.markdown(f"""
    <h4 style="background-color: {CLAIRE_MAUVE}; color: black; padding: 10px;">
        THE PIKE OUTLETS
    </h4>
    """, unsafe_allow_html=True)

    query_options = list(store_questions.keys())
    selected_query = st.selectbox("Select a query", query_options if query_options else ["Select a query"])

    if selected_query and selected_query != "Select a query":
        sql_query = store_questions[selected_query]["sql"]
        conn = connect_to_db(DB_NAME)
        cur = conn.cursor()
        cur.execute(sql_query)
        getDataTable = cur.fetchall()
        columns = [column[0] for column in cur.description]
        getDataTable = DataFrame(getDataTable, columns=columns)

        # st.dataframe(getDataTable)

        nlr = store_questions[selected_query]["nlr"]
        st.write(nlr)

# Main Application
set_custom_css()

# Load the STORE MANAGER app directly without sidebar or toggle
store_manager_app()
