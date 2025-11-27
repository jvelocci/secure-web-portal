# *Originally a Team Project*
Cleaned up and re-uploaded here

# 1. Clone the repository
Clone repository then cd to project folder

# 2. Create a virtual environment
```python -m venv .venv```

# 3. Activate the virtual environment
Windows PowerShell:
```.\.venv\Scripts\Activate.ps1```
If you get an error about scripts being disabled, run this first:
```Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass```
Then activate again.

# 4. Install dependencies
```pip install -r requirements.txt```

# 5. Create the PostgreSQL database
Open a terminal and run:
```& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres```  
Sign into PostgreSQL then run the following:  
```CREATE DATABASE company_portal_db;```

# 6. Load the SQL file into the database
In PowerShell from the project directory:  
```& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d company_portal_db -f sql\company_v3.02.sql```  
```& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d company_portal_db -f sql\team_setup.sql```  
(Change the version number in the path if needed.)

# 7. Create Dotenv file to hold PostgreSQL credentials
* From the project directory create a new file named .env
    * (in Powershell, you can run ```New-Item -Path .env -ItemType File```)
* inside the .env file, enter the following (replace ```<your postgres password>``` with your postgres password):
    ```
    DB_USER=postgres
    DB_PASSWORD=<your postgres password>
    DB_HOST=localhost
    DB_PORT=5432
    ```
    * replace ```DB_USER```, ```DB_HOST```, and ```DB_PORT``` if your credentials do not match the defaults

# 8 Add the Test Account to the Database
From the main project directory, run the command below, and the one in step 9  
```python insert_user.py``` 
# 9. Run the Flask app
```python app.py```

# 10. Open a browser and go to:
http://127.0.0.1:5000/

You should see the Flask test page with the current date from the database.
If you get a connection error, make sure PostgreSQL is running and the password in app.py matches your local setup.