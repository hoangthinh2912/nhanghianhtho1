
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import numpy as np

# =========================
# 1. READ EXCEL DATA
# =========================
file_path = "bank_revenue_data.xlsx"
df = pd.read_excel(file_path)

print("\n===== DATA PREVIEW =====")
print(df.head())

# =========================
# 2. BASIC ANALYSIS
# =========================
print("\n===== DESCRIPTIVE STATISTICS =====")
print(df.describe())

# =========================
# 3. VISUAL DASHBOARD
# =========================

# Revenue Trend
plt.figure(figsize=(10,5))
plt.plot(df["Month"], df["Revenue"], marker='o')
plt.xticks(rotation=45)
plt.title("Bank Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

# Revenue vs Loans
plt.figure(figsize=(7,5))
plt.scatter(df["Loans"], df["Revenue"])
plt.title("Loans vs Revenue")
plt.xlabel("Loans")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

# Correlation Heatmap
corr = df.drop(columns=["Month"]).corr()

plt.figure(figsize=(8,6))
plt.imshow(corr, interpolation='nearest')
plt.colorbar()
plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)
plt.yticks(range(len(corr.columns)), corr.columns)
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.show()

# =========================
# 4. AI REVENUE PREDICTION
# =========================

X = df[["Customers", "Loans", "Card_Spending", "App_Users", "Transactions"]]
y = df["Revenue"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("\n===== AI MODEL RESULT =====")
print("R2 Score:", round(r2_score(y_test, predictions), 4))
print("MAE:", round(mean_absolute_error(y_test, predictions), 2))

# =========================
# 5. FUTURE TREND PREDICTION
# =========================

future_data = pd.DataFrame({
    "Customers": [16000],
    "Loans": [7000],
    "Card_Spending": [2200000000],
    "App_Users": [13000],
    "Transactions": [210000]
})

future_revenue = model.predict(future_data)

print("\n===== NEXT PERIOD REVENUE FORECAST =====")
print("Predicted Revenue:", int(future_revenue[0]))

# =========================
# 6. AUTOMATIC AI COMMENTS
# =========================

print("\n===== AI BUSINESS INSIGHTS =====")

if df["Revenue"].iloc[-1] > df["Revenue"].iloc[0]:
    print("- Revenue shows an upward trend over time.")
else:
    print("- Revenue trend is decreasing.")

best_feature = corr["Revenue"].drop("Revenue").abs().idxmax()

print(f"- The factor most affecting revenue is: {best_feature}")

if corr["Revenue"]["Loans"] > 0.5:
    print("- Loan activity strongly contributes to bank revenue.")

if corr["Revenue"]["App_Users"] > 0.5:
    print("- Digital banking users significantly improve revenue.")

print("- AI model can support financial planning and business strategy.")
