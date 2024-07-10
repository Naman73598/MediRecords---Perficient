from flask import Flask, request,send_file,jsonify
from DatabaseConnection.connection import create_connection,create_database
from DataExtraction.Extractdata import return_dataFrame,extract_data_from_json
from DataExtraction.convert_data import convert_into_Dataframe
from Tables.temp_table import create_temp_table
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
 
 
def doctorapp(app,mysql,jwt):
    @app.route("/insertdoctor")
    def insertDoctor():
        doctor_path2="C:/PerficientProject/MediRecords-Seamless-Care-Starts-Here/Datasetdoctor/"
        df=return_dataFrame(doctor_path2)
        print(df.columns)
        data=[tuple(x) for x in df.to_numpy()]
        cur=mysql.connection.cursor()
        Result=""
        try:
            sql="insert into doctor (id, name,specialization) values (%s, %s, %s)"
            cur.executemany(sql, data)
            mysql.connection.commit()
            cur.close()
            Result="Doctor Data Inserted Successfully"
        except Exception as e:
            Result="Error Occured:{}".format(e)
            return Result,404
       
        return Result,200
 
    @app.route("/addDoctor", methods=["POST"])
    def insert_doctor():
        data = request.get_json()
        name = data.get('name')
        specialization = data.get('specialization')
        try:
            cursor = mysql.connection.cursor()
   
            sql_select = "SELECT id FROM doctor ORDER BY id DESC LIMIT 1"
            cursor.execute(sql_select)
   
       
            res = cursor.fetchone()
            last_inserted_id = res[0]
   
        except Exception as e:
            print("Error found {}".format(e))
   
        id = last_inserted_id+1
   
        try:
            cur = mysql.connection.cursor()
            sql = "INSERT INTO doctor (id, name, specialization) VALUES (%s, %s, %s)"
            cur.execute(sql, (id, name, specialization))
            mysql.connection.commit()
            Result = "Doctor Data Inserted Successfully"
        except Exception as e:
            Result = "Error Occurred: {}".format(e)
            return Result, 404
        finally:
            cur.close()
   
        return Result, 200
   
   
    @app.route("/getDoctor/<int:id>", methods=["GET"])
    def get_doctor(id):
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM doctor WHERE id = %s", (id,))
            result = cur.fetchone()
   
            if result:
                return jsonify(result), 200
            else:
                return jsonify({'message': f"Doctor with ID {id} not found"}), 404
        except Exception as err:
            return jsonify({'message': f"Error: {err}"}), 500
        finally:
            cur.close()
   
    @app.route("/updateDoctor/<int:id>", methods=["PUT"])
    def update_doctor(id):
        data = request.get_json()
        name = data.get('name')
        specialization = data.get('specialization')
   
        try:
   
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM doctor WHERE id = %s", (id,))
            doctor = cur.fetchone()
       
            if not doctor:
                return jsonify({'message': "Doctor with ID {} does not exist".format(id)}), 404
       
            if doctor[1] == name and doctor[2] == specialization:
                return jsonify({'message': "Doctor data is already the same"}), 200
       
            sql = "UPDATE doctor SET name = %s, specialization = %s WHERE id = %s"
            cur.execute(sql, (name, specialization, id))
            mysql.connection.commit()
       
            return jsonify({'message': "Doctor Data Updated Successfully"}), 200
   
        except Exception as e:
            return jsonify({'message': "Error Occurred: {}".format(e)}), 500
   
        finally:
            cur.close()