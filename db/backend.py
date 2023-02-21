import mysql.connector
import json
import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
from pydantic import BaseModel
from datetime import datetime
from typing import List, Union,Optional
from dotenv import load_dotenv
import os 

load_dotenv() 
mysql_pass = os.getenv("MYSQL_ROOT_PASSWORD")


app = FastAPI()

@app.get('/')
def hello_world():
    return 'Hello, Docker!'

@app.post('/widgets')
def get_widgets():
    mydb = mysql.connector.connect(
        host="appsqldb",
        user="root",
        password=mysql_pass,
        database="requests_info"
    )
    cursor = mydb.cursor()


    cursor.execute("SELECT * FROM widgets")

    row_headers=[x[0] for x in cursor.description] #this will extract row headers

    results = cursor.fetchall()
    json_data=[]
    for result in results:
        json_data.append(dict(zip(row_headers,result)))

    cursor.close()
   
    return {"data":json_data}

@app.post('/initdb')
def db_init():
    mydb = mysql.connector.connect(
        host="appsqldb",
        user="root",
        password=mysql_pass
    )
    cursor = mydb.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS requests_info;")
    cursor.close()
    mydb = mysql.connector.connect(
        host="appsqldb",
        user="root",
        password=mysql_pass,
        database="requests_info"
    )
    cursor = mydb.cursor()

    #cursor.execute("DROP TABLE IF EXISTS widgets")
    cursor.execute("CREATE TABLE IF NOT EXISTS widgets (request VARCHAR(200), prompt VARCHAR(200), datetime DATETIME(6), runtime FLOAT, error VARCHAR(2500))")
    cursor.close()

    return 'init database'

class req_info(BaseModel):
    req_type: str
    prompt: Optional[str] = None
    runtime: Optional[float] = None
    error: Optional[str] = None


@app.post('/insert')   
def get_widgets(API_req: req_info):
    mydb = mysql.connector.connect(
        host="appsqldb",
        user="root",
        password=mysql_pass,
        database="requests_info"
    )
    
    cursor = mydb.cursor()
    now = datetime.utcnow()
    cursor.execute("INSERT INTO widgets VALUE (%s, %s, %s, %s, %s)",(API_req.req_type, API_req.prompt, now.strftime('%Y-%m-%d %H:%M:%S'), API_req.runtime, API_req.error))
    mydb.commit()

    return 
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8509)