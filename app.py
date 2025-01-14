from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Define the function for analyzing customer data
def analyze_customer_data(file_path):
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

    reorder_threshold_per_day = 5
    promo_threshold_per_day = 0

    results = []
    grouped = df.groupby("Customer Name")

    for customer, group in grouped:
        actions = []
        group = group.sort_values("Date")
        product_records = {}

        for _, row in group.iterrows():
            products = row.get("Products Selection", "")
            date = row["Date"]

            product_list = products.split(",")
            current_product = None

            for item in product_list:
                item = item.strip()
                try:
                    quantity = float(item)
                    if current_product:
                        if current_product not in product_records:
                            product_records[current_product] = {
                                "first": {"quantity": quantity, "date": date},
                                "last": {"quantity": quantity, "date": date},
                            }
                        else:
                            product_records[current_product]["last"] = {
                                "quantity": quantity,
                                "date": date,
                            }
                        current_product = None
                except ValueError:
                    current_product = item

        for product_name, record in product_records.items():
            first_record = record["first"]
            last_record = record["last"]

            first_quantity = first_record["quantity"]
            first_date = first_record["date"]
            last_quantity = last_record["quantity"]
            last_date = last_record["date"]

            days_between = (last_date - first_date).days or 1
            quantity_diff = first_quantity - last_quantity
            daily_quantity_change = quantity_diff / days_between

            if promo_threshold_per_day <= daily_quantity_change < reorder_threshold_per_day:
                actions.append(f"{product_name}: Needs Promo")
            elif daily_quantity_change >= reorder_threshold_per_day:
                actions.append(f"{product_name}: Reorder")

        if actions:
            results.append({
                "Customer Name": customer,
                "Actions": "; ".join(actions)
            })

    if results:
        results_df = pd.DataFrame(results)
        
        # Save the file to the static folder
        output_path = os.path.join(app.static_folder, 'customer_actions.xlsx')
        results_df.to_excel(output_path, index=False)
        return output_path
    else:
        return None


# Define routes for Flask
@app.route('/')
def home():
    return render_template("form.html")


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file uploaded!", 400

    file = request.files['file']

    if file.filename == '':
        return "No file selected!", 400

    file.save(file.filename)

    output_file = analyze_customer_data(file.filename)

    if output_file:
        return f"Analysis complete. Download your file <a href='/download'>here</a>."
    else:
        return "No actions to report."


@app.route('/download')
def download():
    # Link to the static folder
    return redirect(url_for('static', filename='customer_actions.xlsx'))


if __name__ == '__main__':
    app.run(debug=True)
