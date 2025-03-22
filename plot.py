import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from adjustText import adjust_text

# === Config ===
csv_date = "2025-03-22"
filename = f"data/meritech_comps_{csv_date}.csv"
x_column = "% YoY Growth - NTM Revenue"
y_column = "EV / NTM Revenue"
retention_column = "Net Dollar Retention"

# Companies to label
whitelist = [
    'Blend Labs', '*Braze', 'DigitalOcean', 'Fastly', 'GitLab', 'Monday',
    'nCino', '*Salesforce', '*Snowflake', '*UiPath', 'Confluent'
]

# === Read & Clean ===
df = pd.read_csv(filename)
df = df[~df["Name"].isin(["Mean", "Median"])]

# Helper to convert string values to numbers
def to_number(val):
    if isinstance(val, str):
        val = val.strip()
        negative = False
        if val.startswith("(") and val.endswith(")"):
            negative = True
            val = val[1:-1]
        val = val.replace("%", "").replace("x", "").replace(",", "").replace("$", "")
        try:
            num = float(val)
            return -num if negative else num
        except:
            return None
    return val

# Convert columns
df[x_column] = df[x_column].apply(to_number)
df[y_column] = df[y_column].apply(to_number)
df[retention_column] = df[retention_column].apply(to_number)

# Scale percentage-based columns to base 100 (e.g., 10% => 110)
df[x_column] = df[x_column].apply(lambda x: 100 + x if pd.notnull(x) else None)
df[retention_column] = df[retention_column].apply(lambda x: x if pd.notnull(x) else None)

# === Data Filtering ===
# 1. For raw EV vs YoY Growth
df_valid = df[(df[x_column].notna()) & (df[y_column].notna())].copy()

# 2. For log(x) EV vs YoY Growth
df_log = df_valid[df_valid[x_column] > 0].copy()
df_log[f"log({x_column})"] = np.log(df_log[x_column])

# 3. For Net Dollar Retention vs YoY Growth
df_ret = df[(df[x_column].notna()) & (df[retention_column].notna())].copy()

# === Plotting Function ===
def plot_regression(x_vals, y_vals, labels, xlabel, ylabel, title, filename):
    model = LinearRegression()
    model.fit(x_vals, y_vals)

    slope = model.coef_[0]
    intercept = model.intercept_
    r_squared = model.score(x_vals, y_vals)

    plt.figure(figsize=(12, 6))
    plt.scatter(x_vals, y_vals, label="Data points", alpha=0.7)

    # Label whitelisted companies
    texts = []
    for i in range(len(x_vals)):
        name = labels[i]
        if name in whitelist:
            plt.scatter(x_vals[i][0], y_vals[i], color='orange', edgecolor='black', zorder=5)
            texts.append(plt.text(x_vals[i][0], y_vals[i], name, fontsize=8, color="black"))

    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))

    # Regression line
    x_range = np.linspace(x_vals.min(), x_vals.max(), 100).reshape(-1, 1)
    y_pred = model.predict(x_range)
    plt.plot(x_range, y_pred, color='red',
             label=f"y = {slope:.2f}x + {intercept:.2f}\nR² = {r_squared:.2f}")

    # Final plot setup
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"✅ Saved: {filename}")

# === 1. EV / NTM Revenue vs YoY Growth (raw) ===
plot_regression(
    x_vals=df_valid[[x_column]].values,
    y_vals=df_valid[y_column].values,
    labels=df_valid["Name"].tolist(),
    xlabel=f"{x_column} (Base 100)",
    ylabel=y_column,
    title=f"{y_column} vs {x_column} Regression ({csv_date})",
    filename=f"plots/regression_raw_{x_column.replace('/', '_')}_vs_{y_column.replace('/', '_')}.png"
)

# === 2. EV / NTM Revenue vs log(YoY Growth) ===
plot_regression(
    x_vals=df_log[[f"log({x_column})"]].values,
    y_vals=df_log[y_column].values,
    labels=df_log["Name"].tolist(),
    xlabel=f"log({x_column})",
    ylabel=y_column,
    title=f"{y_column} vs log({x_column}) Regression ({csv_date})",
    filename=f"plots/regression_log_{x_column.replace('/', '_')}_vs_{y_column.replace('/', '_')}.png"
)

# === 3. Net Dollar Retention vs YoY Growth (raw) ===
plot_regression(
    x_vals=df_ret[[x_column]].values,
    y_vals=df_ret[retention_column].values,
    labels=df_ret["Name"].tolist(),
    xlabel=f"{x_column} (Base 100)",
    ylabel=f"{retention_column} (Base 100)",
    title=f"{retention_column} vs {x_column} Regression ({csv_date})",
    filename=f"plots/regression_raw_{x_column.replace('/', '_')}_vs_{retention_column.replace('/', '_')}.png"
)