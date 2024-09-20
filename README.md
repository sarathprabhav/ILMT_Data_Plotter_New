# ILMT Fits Headrer : Web APP
Prepared by : Sarath Prabhavu J <br>
mail : sarathprabhav@gmail.com

The whole project can be divided into two parts 
1. Database Development
2. Web App Development

### Database Development

Files Mentioned are available in the database folder. 

Database has developed using PostgreSQL. The database consists of all the necessary parameters needed to be displayed in the web app. The Data base has been created using the **create_db.py** code.  The unique ID of the database   is created using the date of observation and time of observation. For example fits file corresponding to 2023 April 09 and time 22:17:22 is assigned with the *uid 20230409221722*. The following are the header fields
- Date of observation
- Right Ascencion 
- Declination
- RA_1
- Dec_1 
- RA_2
- Dec_2 
- Dec_obs 
- RA_obs
- FWHM 
- PSF_a 
- PSF_b 
- PSF_pa
- RA- Error
- Dec- Error
- Pos-Err 
- zeropt 
- Zp-Err
- sky 
- param2 
- param7
- param 48
- param 49 

Database Credentials 

<blockquote>
hostname = "localhost"<br>
database = "ilmt_database"<br>
username = 'ilmt_user'<br>
pwd = "devasthal"<br>
port_id = 5432<br>
</blockquote>
<br>
After creating the database, the database has to be updated with the curresponding values from the fits file. 

```
directory = '/home/ilmt/HARDDISK2/Sarath/Database/Data'
```
All these parameters are read from the fits files in the directory using Astropy and Upadated it to the database using the **update_db.py**. You can change the directory by changing the above line of code to desired location


### Copying data from IC1

 **rangedate_data_copy_new.sh** bash script can be used to copy data from IC1 to ICC2. In the bash script initial and final date can be selected and data will be copied and extracted to the desired directory. 

'''
initial_date = "20240101"<br>
final_date = "20240331"
'''
This extracted fits files can be added to database using update.py.

### Web App Development
Web app devolopment can be devided into three parts 

- Frontend Development
- Backend Development

#### Frontend Development

For frontend development I have used HTML and Javascript and Bootstrap. The HTML file is available in the templates directory. Javascript and CSS are available in the static directory. The frontend has options to choose a date range using calendar also discreet date inputs are also available. X axis also can be chosen from the dropdown menu. All the parameters mentioned above are available as the Y axis of the graph. Which can be selected using the tick boxes. Also the app has the functionality to choose multiple parameters simultaneously for the Y axis.

#### Backend Development
The backend runs in python package flask. It is possible to access information from the database using psycopg2 package and updated and send to the frontend on request. 