import oracledb
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv() 
DB_CONFIG = {
    "username": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "dsn": os.getenv("DB_DSN"),
}

# Connect Oracle 
def get_oracle_connection():
    return oracledb.connect(
        user=DB_CONFIG["username"],
        password=DB_CONFIG["password"],
        dsn=DB_CONFIG["dsn"]
    )

def get_date(startDate: str, endDate: str):
    # Parameter
    endDate_formate = datetime.strptime(endDate, "%Y-%m-%d") + timedelta(days=1)
    endDate = endDate_formate.strftime("%Y-%m-%d")
    try:
        with get_oracle_connection() as connection:
            with connection.cursor() as cursor:
                query = """
                SELECT * FROM (
                SELECT * FROM (
                SELECT DISTINCT 
                    A.PLATE1 || ' ' || A.PLATE2 AS LICENSE, 
                    V.DESCRIPTION AS PROVINCE,
                    TO_CHAR(A.TRANSACTION_DATE, 'DD/MM/') || TO_CHAR(EXTRACT(YEAR FROM A.TRANSACTION_DATE) + 543) || TO_CHAR(A.TRANSACTION_DATE, ' HH24:MI:SS') AS TRANSACTION_DATE, 
                    TO_CHAR(B.PAYMENT_DATE, 'DD/MM/') || TO_CHAR(EXTRACT(YEAR FROM B.PAYMENT_DATE) + 543) || TO_CHAR(B.PAYMENT_DATE, ' HH24:MI:SS') AS PAYMENT_DATE, 
                    TO_CHAR(B.PAYMENT_DATE, 'YYYY-MM-DD') AS PAYMENT_DATE_RAW,
                    A.TRANSACTION_ID,
                    T.REF_TRANSACTION_ID,
                    A.INVOICE_NO,
                    T.REF_TAG_RFID,
                    B.STATUS,
                    B.PAYMENT_CHANNEL,
                    A.FEE_AMOUNT AS FEE
                FROM INVOICE_SERVICE.MF_INVOICE_DETAIL A
                LEFT JOIN INVOICE_SERVICE.MF_INVOICE B ON A.INVOICE_NO = B.INVOICE_NO
                LEFT JOIN CUSTOMER_SERVICE.MF_CUST_MASTER_VEHICLE_OFFICE V ON A.PROVINCE = V.CODE
                LEFT JOIN CUSTOMER_SERVICE.MF_CUST_VEHICLE_INFO C ON C.CUSTOMER_ID = B.CUSTOMER_ID
                LEFT JOIN CUSTOMER_SERVICE.MF_CUST_MEMBER_TRANSACTION T ON A.TRANSACTION_ID = T.TRANSACTION_ID
                WHERE B.PAYMENT_DATE >= TO_DATE(:start_date, 'YYYY-MM-DD')
                AND B.PAYMENT_DATE < TO_DATE(:end_date, 'YYYY-MM-DD')
                ) Q WHERE (Q.PAYMENT_CHANNEL = 'EASYPASS' OR Q.PAYMENT_CHANNEL = 'MPASS')
                ) R WHERE R.STATUS = 'PAYMENT_SUCCESS' AND R.FEE > 0
                """
                with connection.cursor() as cursor:
                    cursor.execute(query, {"start_date": startDate, "end_date": endDate})
                    rows = cursor.fetchall()
                    columns = [col[0] for col in cursor.description]
                    df = pd.DataFrame(rows, columns=columns)

                if df.empty:
                    print("⚠️ ไม่พบข้อมูล")
                    return "⚠️ not Found"
                else:
                    result = {}

                    grouped = df.groupby("PAYMENT_DATE_RAW")
                    for date, group in grouped:
                        sheet_name = f"{date}"
                        group.drop(columns=["PAYMENT_DATE_RAW"], inplace=True)
                        print(f"✅ ข้อมูล: {sheet_name} ({len(group)} rows)")
                        # เก็บเป็น JSON แยกตามวันที่
                        result[sheet_name] = group.to_dict(orient="records")

                    return result
    except Exception as e:
        print("เกิดข้อผิดพลาด:", e)
        return f"❌ เกิดข้อผิดพลาด: {e}"
        