from flask import Flask, request, jsonify, send_file
from db import get_date
from flask_cors import CORS
import os
import pandas as pd


app = Flask(__name__)
# app = Flask(__name__, static_folder="../public", static_url_path="/")

CORS(app)

cache_data = {}     
cache_day = {}

@app.route("/main", methods=["POST"])
def main():
    data = request.get_json()
    start_date = data.get("startDate")
    end_date = data.get("endDate")

    if not start_date or not end_date:
        return jsonify({
            "message": "กรุณากรอกข้อมูลให้ถูกต้อง",
            "status": 400
        }), 400
    try:
        print(f"🔄️ Start Process")
        result = get_date(start_date, end_date)
        print(f"🔄️ End Process")

        if result:
            global cache_data, cache_day
            cache_data = result
            cache_day = {
                "start": pd.to_datetime(start_date),
                "end": pd.to_datetime(end_date)
            }

            return jsonify({
                "message": "Success",
                "data": result,
                "status": 200
            }),200
        else:
            return jsonify({
                "message": "Failed",
                "status": 200
            }), 200
        
    except Exception as e:
        print("❌ Error get_Data:", e)
        return jsonify({"message": f"Error get_Data: {e}"}), 500

@app.route("/download", methods=["GET"])
def download_file():
    global cache_data, cache_day

    if not cache_data or not cache_day:
        return jsonify({"message": "⚠️ โหลดข้อมูลไม่สำเร็จ"}), 400
    
    print(f"🔄️ Start Download")

    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(downloads_path, exist_ok=True)

    start = cache_day.get("start")
    end = cache_day.get("end")
    name = f"Status_{start.day}_{start.strftime('%m')}_to_{end.day}_{end.strftime('%m')}.xlsx" if start and end else "Status.xlsx"
    filename = os.path.join(downloads_path, name)

    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for date, group in cache_data.items():
                df = pd.DataFrame(group)
                if "PAYMENT_DATE_RAW" in df.columns:
                    df.drop(columns=["PAYMENT_DATE_RAW"], inplace=True)
                df.to_excel(writer, sheet_name=date[:31], index=False)
                print(f"✅ เพิ่มข้อมูลลง sheet: {date} ({len(df)} rows)")
        print(f"📁 บันทึกไฟล์ : {filename}")

    except Exception as e:
        print("❌ Error writing Excel:", e)
        return jsonify({"message": f"Error writing Excel: {e}"}), 500
    
    print(f"🔄️ End Download")
    return send_file(filename, as_attachment=True), 200

@app.route("/")
def check():
    # return app.send_static_file("index.html")
    return jsonify(status="OK", message="Ready to use", permission="true")

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8001, debug=True)
