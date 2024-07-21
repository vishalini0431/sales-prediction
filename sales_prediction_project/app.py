from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Ensure the uploads folder exists
uploads_dir = os.path.join(app.root_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

# Function to process the uploaded file and predict the most sold item
def predict_items(file_path):
    try:
        # Read Excel file
        df = pd.read_excel(file_path)

        # Ensure necessary columns exist in the dataframe
        required_columns = ['customer_id', 'item', 'quantity']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing '{col}' column in the Excel file")

        # Group by 'item' and sum quantities
        item_totals = df.groupby('item')['quantity'].sum()

        # Predict item with the highest total quantity
        most_sold_item = item_totals.idxmax()

        # Predict item likely to be sold next month (simple assumption)
        next_month_prediction = most_sold_item

        return most_sold_item, next_month_prediction

    except Exception as e:
        raise ValueError(f'Error processing file: {str(e)}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploader', methods=['POST'])
def uploader():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        file_path = os.path.join(uploads_dir, file.filename)
        file.save(file_path)

        # Predict item
        try:
            most_sold_item, next_month_prediction = predict_items(file_path)
            flash(f'Predicted most sold item: {most_sold_item}')
            flash(f'Item likely to be sold next month: {next_month_prediction}')
        except ValueError as ve:
            flash(f'Error processing file: {str(ve)}')

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
