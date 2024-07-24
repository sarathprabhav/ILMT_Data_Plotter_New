from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    data = request.json
    functions = data['functions']
    x_range = data['x_range']
    fdate = data['fdate']  # Get the date input
    print("date is : ",fdate)
    x_values = np.linspace(0, x_range, 1000)
    y_values = {}
    
    if 'sin' in functions:
        y_values['sin'] = np.sin(np.radians(x_values)).tolist()
    if 'cos' in functions:
        y_values['cos'] = np.cos(np.radians(x_values)).tolist()
    if 'tan' in functions:
        y_values['tan'] = np.tan(np.radians(x_values)).tolist()

    return jsonify({'x': x_values.tolist(), 'y': y_values})

if __name__ == '__main__':
    app.run(debug=True)
