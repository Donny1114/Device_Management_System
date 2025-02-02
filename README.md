# Device_Management_System
A device tracking system built with python



Run this command to install all needed libraries:
    pip install -r requirments.txt


To run this app from other pc in same network
    ## Other PC
1. Copy the whole folder project then create the virtual environment
    and create the virtual env 
    ## Create a virtual environment
    python -m venv venv

    ## Activate it (Windows)
    venv\Scripts\activate

2. Run pip install -r requirements.txt

 ## MYSQL
3. Your MySQL server allows remote connections (Check bind-address in my.ini or mysqld.cnf)
    C:\Program Files\MySQL\MySQL Server X.X\my.ini
    Add this in my.ini 
     [mysqld]
     bind-address = 0.0.0.0
    Restart the mysql services

4. CREATE USER 'remote_user'@'%' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON yourdatabase.* TO 'remote_user'@'%';
FLUSH PRIVILEGES;

5. Create a batch file (run_app.bat) in the same folder as main.py to just double click the file:
   @echo off
   cd /d "%~dp0"
   venv\Scripts\python.exe main.py
   pause



