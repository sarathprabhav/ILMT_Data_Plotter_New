from flask import Flask, render_template, request, jsonify
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "secret key"


# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "postgres"

# ======================== Functions =================
def get_db_connection():
    """
    Establishes a connection to a PostgreSQL database using the provided credentials.

    Parameters:
    None

    Returns:
    conn (psycopg2.extensions.connection): A connection object to the PostgreSQL database.
    """
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
def date_ip_to_db_string(disc_date):
    """Converts discreet date input to a database compatible string
    """
    disc_date_str = ""
    for i in disc_date:
        disc_date_str +=f"'{i}',"
     
    return disc_date_str[:-1] # Remove the trailing comma

def time_to_hours(time_obj):
    """
    Converts a time object to a float representing the time in hours.

    Parameters:
    time_obj (datetime.time): A time object representing the time to be converted.

    Returns:
    float: The time in hours. The result is a float value representing the total number of hours,
           minutes, and seconds in the input time object.
    """
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond * (1e-6)
    hours = total_seconds / 3600.0
    return hours

def dec_to_degree(dec_str):
    """
    Converts a declination string in the format 'Deg:Min:Sec' to a float representing the declination in degrees.

    Parameters:
    dec_str (str): A string representing the declination in the format 'deg:min:sec'. The string may start with a '+'
                   sign, which is ignored.

    Returns:
    float: The declination in degrees. The result is a float value representing the total number of degrees,
           minutes, and seconds in the input declination string.
    """
    dec = dec_str.replace('+',"").split(":")
    seconds = float(dec[0])*3600 + float(dec[1])*60+ float(dec[2])
    deg = seconds/3600
    return deg



@app.route('/')
def index():
    """
    This function is a route for the root URL ("/") of the web application.
    It renders the 'index.html' template when accessed.

    Parameters:
    None

    Returns:
    render_template: A function call to render the 'index.html' template.
    """
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    """
    This function handles the '/plot' route and generates a plot based on the input data.

    Parameters:
    - data (request.json): JSON data containing the parameters for the plot.

    Returns:
    - jsonify({'x':x_values , 'y': y_values, 'xlabel':param_names_dict[x_param] }): JSON response containing the x and y values for the plot, along with the x-axis label.
    """

    # Getting Data from the frontend
    data = request.json
    functions = data['functions']
    x_param = data['x_range']
    fdate = data['fdate']  # Get the from date input
    fdate = '2023-01-31'
    tdate = data['tdate'] # Get the to date input
    tdate = '2023-04-15'
    disc_date = data['ddate'].split(',')  # Get the discreet date input
    
    #formating date for database
    disc_date_str = date_ip_to_db_string(disc_date)             
    date_string = generate_date_range(fdate,tdate) # Generate the date range as a string

    # Connect to the database and retrieve the data
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Database Queries based on the input parameters
    y_params = ','.join(functions)
    
    if x_param == 'utstart':
        params = x_param +',' +y_params
    else:
        params = 'utstart,' + x_param + ',' + y_params
    
    if len(disc_date_str) == 2:
        query = f"SELECT date_obs,{params} FROM test_table2 WHERE date_obs in ({date_string})"
    else:
        query = f"SELECT date_obs,{params} FROM test_table2 WHERE date_obs in ({disc_date_str})"
    

    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()    

#------------------Cleaning and Data sending --------------------------------
    if result:
        # Cleaning up and converting the retrieved data to a pandas DataFrame
        if x_param == 'utstart':
            cols = ['date',x_param]+functions
        else:
            cols = ['date','utstart',x_param]+functions
        df = pd.DataFrame(result, columns=cols)
        df = df.sort_values(by=['date', 'utstart'])
        df.reset_index(inplace=True, drop=True)
        df['datetime'] = df.apply(lambda row: datetime.combine(row['date'], row['utstart']), axis=1)
        df = df.loc[:,~df.columns.duplicated()].copy()
    
    # Accessing x values from the DataFrame
    if x_param == 'utstart':
        #x_values = df['utstart'].apply(time_to_hours)
        # Creating JSON-serializable x values from datetime values
        x_values = df['datetime'].tolist()
        x_values = [str(i) for i in x_values]
        x_values = [i[0:i.index(".")] for i in x_values]
    elif x_param == 'param2':
        x_values = df['param2'].values.tolist()

    # Defining a dictionary to map parameter names to their descriptions
    param_names_dict = {
        'utstart': 'UT-Time at start of the exposure',
        'ra': 'RA of field centre, J2000 (hour)',
        'dec': 'DEC of field centre, J2000 (degree)',
        'ra1': 'RA of first pixel, J2000 (hour)',
        'dec1': 'Dec of first pixel, J2000 (degree)',
        'ra2': 'RA of last pixel, J2000 (hour)',
        'dec2': 'Dec of last pixel, J2000 (degree)',
        'dec_obs': 'Dec of field center at epoch of observation (degree)',
        'ra_obs': 'RA of field center at epoch of observation (hour)',
        'psf_a': 'Major axis of star images (arcsec)',
        'psf_b': 'Minor axis of star images (arcsec)',
        'psf_pa': 'Position angle of star images (deg)',
        'zeropt': 'Photometric magnitude zero point',
        'poserr': 'Estimated total error (arcsec)',
        'raerr': 'Estimated RA error (arcsec)',
        'decerr': 'Estimated dec error (arcsec)',
        'zperr': 'Estimated magnitude zero point error',
        'magerr': 'Estimated magnitude RMS error, bright stars',
        'fwhm': 'FWHM of star images (arcsec)',
        'sky': 'Sky background before performing sky subtraction',
        'param2': 'CCD Temperature (C)',
        'param7': 'CCD Chamber Pressure (Torr)',
        'param48': 'CryoTiger Pressure 1 (psi)',
        'param49': 'CryoTiger Pressure 2 (psi)'
    }

    # Initializing an empty dictionary to store y values
    y_values = {}
    
    # Grouping and processing y values based on the selected parameters
    #==============================GROUP 1============================
    if 'ra' in functions:
        y_values[param_names_dict['ra']] = df["ra"].apply(time_to_hours).tolist()
    if 'dec' in functions:
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
    
    #==============================GROUP 2============================
    if 'psf_a' in functions:
        y_values[param_names_dict['psf_a']] = df['psf_a'].tolist()
    if 'psf_b' in functions:
        y_values[param_names_dict['psf_b']] = df['psf_b'].tolist()
    if 'psf_pa' in functions:
        y_values[param_names_dict['psf_pa']] = df['psf_pa'].tolist()
    if 'zeropt' in functions:
        y_values[param_names_dict['zeropt']] = df['zeropt'].tolist()
        
    #==============================GROUP 3============================
    if 'poserr' in functions:
        y_values[param_names_dict['poserr']] = df['poserr'].tolist()
    if 'raerr' in functions:
        y_values[param_names_dict['raerr']] = df['raerr'].tolist()
    if 'decerr' in functions:
        y_values[param_names_dict['decerr']] = df['decerr'].tolist()
    if 'zperr' in functions:
        y_values[param_names_dict['zperr']] = df['zperr'].tolist()
    if 'magerr' in functions:
        y_values[param_names_dict['magerr']] = df['magerr'].tolist()
    
    #==============================GROUP 4============================
    if 'fwhm' in functions:
        y_values[param_names_dict['fwhm']] = df['fwhm'].tolist()
    if 'sky' in functions:
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


# Add more variables for x axis 
