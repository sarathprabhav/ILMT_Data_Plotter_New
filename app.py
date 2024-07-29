from flask import Flask, render_template, request, jsonify
import numpy as np
import psycopg2
import pandas as pd
from datetime import datetime, timedelta


app = Flask(__name__)


# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "postgres"

# ======================== Functions =================
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

def generate_date_range(start_date_str, end_date_str):
    """
    Generate a string of dates between the start and end dates (inclusive).

    :param start_date_str: Start date as a string in the format 'YYYY-MM-DD'
    :param end_date_str: End date as a string in the format 'YYYY-MM-DD'
    :return:  dates as strings in the format 'YYYY-MM-DD'
    """
    # Convert the string dates to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Generate a list of dates between the start and end dates
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    quoted_dates = ','.join(f"'{date}'" for date in date_list)
    return quoted_dates

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
    x_param = data['x_range']
    fdate = data['fdate']  # Get the from date input
    fdate = '2023-01-31'
    tdate = data['tdate'] # Get the to date input
    tdate = '2023-12-01'
    disc_date = data['ddate'] # Get the discreet date input
    print("Disc date is : ",disc_date)
    
    date_string = generate_date_range(fdate,tdate) # Generate the date range as a string
    
    
    # Connect to the database and accuring the data
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Database Queries based on the input 
    
    y_params = ','.join(functions)
    
    if x_param == 'utstart':
        params = x_param +',' +y_params
    else:
        params = 'utstart,' + x_param + ',' + y_params
        
    query = f"SELECT date_obs,{params} FROM test_table2 WHERE date_obs in ({date_string})"

    print("================================================")
    #print(query)
    print(params)
    cur.execute(query,(fdate,))
    result = cur.fetchall()
    cur.close()
    conn.close()    

#------------------Cleaning and Data sending --------------------------------
    if result:
        
        #cleaningup and conversions accured data to pandas dataframe
        if x_param == 'utstart':
            cols = ['date',x_param]+functions
        else:
            cols = ['date','utstart',x_param]+functions
        df = pd.DataFrame(result, columns=cols)
        df = df.sort_values(by=['date', 'utstart'])
        df.reset_index(inplace=True, drop=True)
        df['datetime'] = df.apply(lambda row: datetime.combine(row['date'], row['utstart']), axis=1)
    
    # accessing x values from dataframe
    if x_param == 'utstart':
        #x_values = df['utstart'].apply(time_to_hours)
        # Creating Jsonifyable x values from datetime values
        x_values = df['datetime'].tolist()
        x_values = [str(i) for i in x_values]
        x_values = [i[0:i.index(".")] for i in x_values]
    elif x_param == 'param2':
        x_values = df['param2'].values.tolist()

    
    
    param_names_dict = a = {'utstart': 'UT-Time at start of the exposure', 
                            'ra': 'RA of field centre, J2000 (hour)', 
                            'dec': 'DEC of field centre, J2000 (degree)', 
                            'ra1': 'RA of first pixel, J2000 (hour)', 
                            'dec1': 'Dec of first pixel, J2000 (degree)', 
                            'ra2': 'RA of last pixel, J2000 (hour)', 
                            'dec2': 'Dec of last pixel, J2000 (degree)', 
                            'dec_obs': 'Dec of field center at epoch of observation (degree)', 
                            'ra_obs': 'RA of field center at epoch of observation (hour)', 
                            'psf_a': 'major axis of star images (arcsec)', 
                            'psf_b': 'minor axis of star images (arcsec)', 
                            'psf_pa': 'position angle of star images (deg)', 
                            'zeropt': 'Photometric magnitude zero point', 
                            'poserr': 'Estimated total error (arcsec)', 
                            'raerr': 'Estimated RA error (arcsec)', 
                            'decerr': 'Estimated dec error (arcsec)', 
                            'zperr': 'Estimated magnitude zero point error', 
                            'magerr': 'Estimated magnitude RMS error, bright stars', 
                            'fwhm': 'FWHM of star images (arcsec)', 
                            'sky': 'sky background before performing sky subtraction', 
                            'param2': 'CCD Temperature (C)', 
                            'param7': 'CCD Chamber Pressure (Torr)', 
                            'param48': 'CryoTiger Pressure 1 (psi)', 
                            'param49': 'CryoTiger Pressure 2 (psi)'}
    y_values ={}
    
    y_list = ["utstart,ra,dec,ra1,dec1,ra2,dec2,dec_obs,ra_obs,psf_a,psf_b,psf_pa,zeropt,poserr,raerr,decerr,zperr,magerr,fwhm,sky,param2,param7,param48,param49"]
    
    #==============================GROUP 1============================
    if 'ra'in functions:
        y_values[param_names_dict['ra']] = df["ra"].apply(time_to_hours).tolist()
    if 'dec'in functions:
        y_values[param_names_dict['dec']] = df['dec'].apply(dec_to_degree).tolist()
    if 'ra1' in functions:
        y_values[param_names_dict['ra1']] = df['ra1'].apply(time_to_hours).tolist()
    if 'dec1' in functions:
        y_values[param_names_dict['dec1']] = df['dec1'].apply(dec_to_degree).tolist()
    if 'ra2' in functions:
        y_values[param_names_dict['ra2']] = df['ra2'].apply(time_to_hours).tolist()
    if 'dec2' in functions:
        y_values[param_names_dict['dec2']] = df['dec2'].apply(dec_to_degree).tolist()
    if 'dec_obs' in functions:
        y_values[param_names_dict['dec_obs']] = df['dec_obs'].apply(dec_to_degree).tolist()
    if 'ra_obs' in functions:
        y_values[param_names_dict['ra_obs']] = df['ra_obs'].apply(time_to_hours).tolist()
    
    #==============================Group 2 ============================
    if 'psf_a' in functions:
        y_values[param_names_dict['psf_a']] = df['psf_a'].tolist()
    if 'psf_b' in functions:
        y_values[param_names_dict['psf_b']] = df['psf_b'].tolist()
    if 'psf_pa' in functions:
        y_values[param_names_dict['psf_pa']] = df['psf_pa'].tolist()
    if 'zeropt' in functions:
        y_values[param_names_dict['zeropt']] = df['zeropt'].tolist()
        
    #=============================Group 3 =============================
    if 'poserr' in functions:
        y_values[param_names_dict['poserr']] = df['poserr'].tolist()
    if 'raerr' in functions:
        y_values[ param_names_dict['raerr']] = df['raerr'].tolist()
    if 'decerr' in functions:
        y_values[param_names_dict['decerr']] = df['decerr'].tolist()
    if 'zperr' in functions:
        y_values[ param_names_dict['zperr']] = df['zperr'].tolist()
    if 'magerr' in functions:
        y_values[param_names_dict['magerr']] = df['magerr'].tolist()
    
    #============================Group 4 =============================
    if 'fwhm' in functions:
        y_values[param_names_dict['fwhm']] = df['fwhm'].tolist()
    if'sky' in functions:
        y_values[param_names_dict['sky']] = df['sky'].tolist()
    if 'param2' in functions:
        y_values[param_names_dict['param2']] = df['param2'].tolist()
    if 'param7' in functions:
        y_values[param_names_dict['param7']] = df['param7'].tolist()
    if 'param48' in functions:
        y_values[param_names_dict['param48']] = df['param48'].tolist()
    if 'param49' in functions:
        y_values[param_names_dict['param49']] = df['param49'].tolist()
    
     
    print(x_values)
    return jsonify({'x':x_values , 'y': y_values, 'xlabel':param_names_dict[x_param] })
 
if __name__ == '__main__':
    app.run(debug=True)
# when choosing x axis other that time. The plot shows inconsistent results.
# This is because x axis will be plotted with sorted values of parameter. 
# Since we are using multiple variable to plot its not possible to show the Y axis units 
