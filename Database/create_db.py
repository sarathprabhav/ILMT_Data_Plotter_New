import psycopg2
hostname = "localhost"
database = "ilmt_database"
username = 'ilmt_user'
pwd = "devasthal"

port_id = 5432
cur = None
conn = None




column_names = ['UID','DATE_OBS','UTSTART','RA', 'DEC', 'RA1', 'RA2', 'DEC1', 'DEC2', 'DEC_OBS', 'RA_OBS','FWHM', 'PSF_A', 'PSF_B', 'PSF_PA', 'RAERR', 'DECERR', 'POSERR',  'ZEROPT', 'ZPERR', 'MAGERR', 'SKY', 'PARAM2', 'PARAM7', 'PARAM48', 'PARAM49']
data_types = ['varchar(20) PRIMARY KEY UNIQUE', 'DATE', 'TIME(6)', 'TIME(6)', 'VARCHAR(20)', 'TIME(6)', 'TIME(6)', 'VARCHAR(20)', 'VARCHAR(20)', 'VARCHAR(20)', 'TIME(6)', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL', 'DECIMAL']

create_table_script = "CREATE TABLE IF NOT EXISTS fits_header_table( "
for i in range(len(column_names)):
    create_table_script += column_names[i] +" " + data_types[i] +", "
create_table_script = create_table_script[:-2] + ");"


print(create_table_script)

try:
    conn = psycopg2.connect(host=hostname, dbname = database, user = username, password = pwd, port = port_id )
    cur = conn.cursor()

    cur.execute(create_table_script)


    conn.commit()



except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()