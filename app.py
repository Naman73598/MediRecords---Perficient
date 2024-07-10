from flask import Flask, request,send_file,jsonify
from DatabaseConnection.connection import create_connection,create_database
from DataExtraction.Extractdata import return_dataFrame,extract_data_from_json
from DataExtraction.convert_data import convert_into_Dataframe
from Tables.temp_table import create_temp_table
from adminapp import adminapp
from doctorapp import doctorapp
from recordsapp import recordsapp
from visualizationapp import visualizationapp
from Tables.admin_table import create_admin_table
from Tables.doctor_table import create_doctor_table
from flask_mysqldb import MySQL
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import requests
 
 
app=Flask(__name__)
mysql = MySQL(app)
 
app.config['JWT_SECRET_KEY'] = '123ath'
 
jwt = JWTManager(app)
 
#authentication
 
adminapp(app,mysql,jwt)
doctorapp(app,mysql,jwt)
recordsapp(app,mysql,jwt)
visualizationapp(app,mysql,jwt)
 
 
#insertion of datas
# record_json_path = "C:/PerficientProject/MediRecords-Seamless-Care-Starts-Here/Datasetjson/""
@app.route("/insert")
def insert():
    record_path1 = "C:/PerficientProject/MediRecords-Seamless-Care-Starts-Here/Dataset/"
   
    df = return_dataFrame(record_path1)
    df_filtered = df[df['Billing Amount'] >= 500]
    df_filtered=df_filtered.iloc[:,1:]
    data = [tuple(x) for x in df_filtered.to_numpy()]
   
    cur = mysql.connection.cursor()
    try:
        sql = "INSERT INTO Records (name, age, gender, bloodtype, medicalcondition, doctor, hospital, insuranceprovider, billingamount, roomnumber, admissiontype, medication, testresults, doctorid, doctorspecialization) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.executemany(sql, data)
        mysql.connection.commit()
        cur.close()
        return "Data Inserted Successfully", 200
    except Exception as e:
        print(f"Error occurred during insertion: {e}")
        return f"Error occurred: {e}", 404
 
 
 
 
 
#consuming api
@app.route("/fetchJsonData")
def fetch_json_data():
    try:
        response = requests.get('http://localhost:3000/patients')
        if response.status_code == 200:
            patients_data = response.json()
            return jsonify(patients_data)
        else:
            return jsonify({'error':'Failed to fetch data from json-server'}),response.status_code
    except Exception as e:
        return jsonify({'error':str(e)}), 500
 
 
@app.route("/insertJsonData")
def insert_json_data():
    try:
        response = requests.get('http://localhost:5000/fetchJsonData')
        if response.status_code == 200:
            patients_data = response.json()
           
            df = extract_data_from_json(patients_data)
            df_filtered = df[df['Billing Amount'] >= 500]
            data = [(row['Name'], row['Age'], row['Gender'], row['Blood Type'],
                     row['Medical Condition'], row['Doctor'], row['Hospital'],
                     row['Insurance Provider'], row['Billing Amount'], row['Room Number'],
                     row['Admission Type'], row['Medication'], row['Test Results'],row['doctor_id'],row['DoctorSpecialization']) for index, row in df_filtered.iterrows()]
           
            print(data)
           
            cur = mysql.connection.cursor()
            try:
                sql = "INSERT INTO Records (name, age, gender, bloodtype, medicalcondition, doctor, hospital, insuranceprovider, billingamount, roomnumber, admissiontype, medication, testresults,doctorid,doctorspecialization) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)"
                cur.executemany(sql, data)
                mysql.connection.commit()
                cur.close()
                return "Data Inserted Successfully",200
            except Exception as e:
                return "Error Occurred:{}".format(e),404
        else:
            return jsonify({'error':'Failed to fetch data from json-server'}), response.status_code
    except Exception as e:
        return jsonify({'error':str(e)}), 500
 
 
 
@app.route("/download_csv")
def download_csv():
    cur = mysql.connection.cursor()
    cur.execute("select * from records")
    result = cur.fetchall()
    df = convert_into_Dataframe(result,cur)
    cur.close()
    csv_data=df.to_csv(index=False)
    buffer=io.BytesIO()
    buffer.write(csv_data.encode())
    buffer.seek(0)
    return send_file(buffer,as_attachment=True,download_name="patient-details.csv",mimetype="text/csv")
 
 
 
if __name__ == "__main__":
    create_connection(app)
    print("Connection Created Successfully")
    if(create_database(mysql,app)):
        print("Database Created Successfully")
    if(create_admin_table(mysql,app)):
        print("Admin table Created Successfully")
    if(create_doctor_table(mysql,app)):
        print("Doctor table Created Successfully")
    if(create_temp_table(mysql,app)):
        print("Records table Created Successfully")
   
    app.run(debug=True)
 