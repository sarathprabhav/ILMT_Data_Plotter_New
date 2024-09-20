import os
import glob
from astropy.io import fits
import psycopg2

def list_fits_files(directory):
    '''
    listing all the fits files in the directory
    to update on a daily basis use the specific date directory
    '''
    # Use glob to recursively find all .fits files
    fits_files = glob.glob(os.path.join(directory, '**', '*.fits'), recursive=True)
    return fits_files

def get_header(file_path,keyword):
    
    """
    Reading the respective header value
    """
    with fits.open(file_path) as hdul:
        primary_hdu = hdul[0]
        head = primary_hdu.header
        key = head.get(keyword)
        return key

header_list = ['DATE-OBS','UTSTART','RA', 'DEC', 'RA1', 'RA2', 'DEC1', 'DEC2', 'DEC-OBS', 'RA-OBS','FWHM', 'PSF-A', 'PSF-B', 'PSF-PA', 'RAERR', 'DECERR', 'POSERR',  'ZEROPT', 'ZPERR', 'MAGERR', 'SKY', 'PARAM2', 'PARAM7', 'PARAM48', 'PARAM49']
#column named differ from header list because of naming conventions
column_names = ['UID','DATE_OBS','UTSTART','RA', 'DEC', 'RA1', 'RA2', 'DEC1', 'DEC2', 'DEC_OBS', 'RA_OBS','FWHM', 'PSF_A', 'PSF_B', 'PSF_PA', 'RAERR', 'DECERR', 'POSERR',  'ZEROPT', 'ZPERR', 'MAGERR', 'SKY', 'PARAM2', 'PARAM7', 'PARAM48', 'PARAM49']

print(len(column_names))
directory = '/home/ilmt/HARDDISK2/Sarath/Database/Data'
print("Current Working Directory:", os.getcwd())
fits_files = list_fits_files(directory)

print("File list length ", len(fits_files))

# Generating values in the correct order to be populated to the database
value_tuples=[]
for file in fits_files:
    values = []
    time_stamp = get_header(file,"UTSTART").split(".")[0].replace(":","")
    date_stamp = file.split("/")[-1].split("-")[0]
    uid = int(date_stamp+time_stamp)
    values.append(uid)
    for key in header_list:
        values.append(get_header(file,key))
    value_tuples.append(tuple(values))



#==========DATABASE UPDATION=======

hostname = "localhost"
database = "ilmt_database"
username = 'ilmt_user'
pwd = "devasthal"
port_id = 5432


insert_script = "INSERT INTO fits_header_table( "
for i in range(len(column_names)):
    insert_script += column_names[i]+", "
insert_script = insert_script[:-2]+") VALUES ( "

for i in range(len(column_names)):
    insert_script += "%s,"
insert_script = insert_script[:-1] + ") ON CONFLICT (UID) DO NOTHING;"

print(insert_script)


conn = psycopg2.connect(host=hostname, dbname = database, user = username, password = pwd, port = port_id )
cur = conn.cursor()

if conn:
    print("Database connection established") 

for value in value_tuples:
    insert_values = value
    cur.execute(insert_script,insert_values)
    print(len(insert_values))
    conn.commit()
cur.close()
conn.close()
