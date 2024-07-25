from flask import Flask, render_template, request, jsonify
import numpy as np
import psycopg2
import pandas as pd

app = Flask(__name__)


# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "postgres"


def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn


def time_to_hours(time_obj):
    # To convert RA to hours
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second +time_obj.microsecond*(1e-6)
    hours = total_seconds / 3600.0
    return hours

def dec_to_degree(dec_str):
    #to convert declinatiob string to float degree
    dec = dec_str.replace('+',"").split(":")
    seconds = float(dec[0])*3600 + float(dec[1])*60+ float(dec[2])
    deg = seconds/3600
    return deg






@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    
    # Getting Data from the frontend
    data = request.json
    functions = data['functions']
    x_range = data['x_range']
    fdate = data['fdate']  # Get the from date input
    tdate = data['tdate'] # Get the to date input
    disc_date = data['ddate'] # Get the discreet date input
    
    print("From date is : ",fdate)
    print("To date is : ",tdate)
    print("Disc date is : ",disc_date)
    print("function is : ",functions)
    
    
    # Connect to the database and accuring the data
    conn = get_db_connection()
    cur = conn.cursor()
    params = ','.join(functions)
    query = f"SELECT date_obs,utstart,{params} FROM test_table2 WHERE date_obs = %s"
    print(query)
    cur.execute(query,(fdate,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    #print("Testing 2 ",result)
    
    if result:
        
        #cleaningup and conversions accured data to pandas dataframe
        cols = ['date','utstart']+functions
        df = pd.DataFrame(result, columns=cols)
        df.sort_values(by = 'utstart', inplace=True)
        df.reset_index(inplace=True, drop=True)
    
    print(df.head())

    
    
    
    
    #x_values = np.linspace(0, x_range, 1000)
    #y_values = {}
    
    x_values = df['utstart'].apply(time_to_hours)
    y_values ={}

    y_values['raerr'] = df['raerr'].tolist()
    
    if 'sin' in functions:
        y_values['sin'] = np.sin(np.radians(x_values)).tolist()
    if 'cos' in functions:
        y_values['cos'] = np.cos(np.radians(x_values)).tolist()
    if 'tan' in functions:
        y_values['tan'] = np.tan(np.radians(x_values)).tolist()

    return jsonify({'x': x_values.tolist(), 'y': y_values})

if __name__ == '__main__':
    app.run(debug=True)
