from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def dashboard():

    if request.method == "POST":

        file = request.files["excel_file"]

        # Đọc Excel
        df = pd.read_excel(file, engine="openpyxl")

        # Chuyển dữ liệu sang số
        cols = [
            "Số khách hàng",
            "Số khoản vay",
            "Chi tiêu thẻ",
            "Người dùng app",
            "Số giao dịch",
            "Doanh thu"
        ]

        for col in cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Xóa dòng lỗi
        df = df.dropna()

        # AI train
        X = df[[
            "Số khách hàng",
            "Số khoản vay",
            "Chi tiêu thẻ",
            "Người dùng app",
            "Số giao dịch"
        ]]

        y = df["Doanh thu"]

        model = LinearRegression()
        model.fit(X, y)

        # Dự đoán
        future = pd.DataFrame({
            "Số khách hàng": [16000],
            "Số khoản vay": [7000],
            "Chi tiêu thẻ": [2200000000],
            "Người dùng app": [13000],
            "Số giao dịch": [210000]
        })

        predict = int(model.predict(future)[0])

        # Nhận xét AI
        if df["Doanh thu"].iloc[-1] > df["Doanh thu"].iloc[0]:
            nhan_xet = "Doanh thu đang tăng trưởng."
        else:
            nhan_xet = "Doanh thu đang giảm."

        return render_template(
            "index.html",

            months=df["Tháng"].astype(str).tolist(),
            revenues=[int(x) for x in df["Doanh thu"]],

            predict=f"{predict:,} VNĐ",
            nhan_xet=nhan_xet,

            tong_khach_hang=f"{int(df['Số khách hàng'].sum()):,}",
            tong_khoan_vay=f"{int(df['Số khoản vay'].sum()):,}",
            tong_chi_tieu_the=f"{int(df['Chi tiêu thẻ'].sum()):,} VNĐ",
            tong_nguoi_dung_app=f"{int(df['Người dùng app'].sum()):,}",
            tong_giao_dich=f"{int(df['Số giao dịch'].sum()):,}"
        )

    return render_template(
        "index.html",
        months=[],
        revenues=[],
        predict=None
    )

if __name__ == "__main__":
    app.run(debug=True)