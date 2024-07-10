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
 
 
def recordsapp(app,mysql,jwt):
    @app.route("/addPatient/<int:doctor_id>/<int:admin_id>", methods=["POST"])
    @jwt_required()
    def add_patient(doctor_id,admin_id):
        data = request.get_json()
        current_user_id = get_jwt_identity()
        print(current_user_id)
        if(current_user_id!=admin_id):
            return jsonify({"Message":"This is the wrong user"})
 
        try:
            cur=mysql.connection.cursor()
            cur.execute("select name,specialization from doctor where id=%s",(doctor_id,))
            result=cur.fetchone()
            cur.close()
        except Exception as e:
            return jsonify({'message':"No person with the id has been registerd as doctor"})
        try:
            cursor = mysql.connection.cursor()
 
            sql_select = "SELECT id FROM Records ORDER BY id DESC LIMIT 1"
            cursor.execute(sql_select)
 
           
            res = cursor.fetchone()
            if result:
                last_inserted_id = res[0]
                print(f"Last inserted ID: {last_inserted_id}")
            else:
                print("No records found")
        except Exception as e:
            print("Error found {}".format(e))
       
        doctor=result[0]
        id = last_inserted_id+1
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        bloodtype = data.get('bloodtype')
        medicalcondition = data.get('medicalcondition')
        hospital = data.get('hospital')
        insuranceprovider = data.get('insuranceprovider')
        billingamount = data.get('billingamount')
        roomnumber = data.get('roomnumber')
        admissiontype = data.get('admissiontype')
        medication = data.get('medication')
        testresults = data.get('testresults')
        doctor_id=doctor_id
        specialization = result[1]
 
        cur=mysql.connection.cursor()
        content=""
        if billingamount<500:
            content="Billing amount should be greater than or equal to 500"
            return jsonify(content),400
 
        try:
            cur.execute("select id from records where id=%s", (id,))
            result = cur.fetchone()
            if result:
                content = "Person with the same ID already exists"
            else:
                cur.execute("INSERT INTO Records (id, name, age, gender, bloodtype, medicalcondition, doctor, hospital, insuranceprovider, billingamount, roomnumber, admissiontype, medication, testresults,doctorid,doctorspecialization) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)",
                            (id, name, age, gender, bloodtype, medicalcondition,doctor, hospital, insuranceprovider, billingamount, roomnumber, admissiontype, medication, testresults,doctor_id,specialization))
                mysql.connection.commit()
                content = "Patient added successfully"
                cur.execute("select * from records")
                all_records= cur.fetchall()
                return jsonify(all_records),200
           
        except Exception as err:
            content = "Error: {}".format(err)
        finally:
            cur.close()
 
        return jsonify({'message':content})
 
    @app.route("/getPatient/<int:id>", methods=["GET"])
    def get_patient(id):
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM Records WHERE id = %s", (id,))
            result = cur.fetchone()
 
            if result:
                return jsonify(result)
            else:
                return jsonify({'message': f"Patient with ID {id} not found"}), 404
        except Exception as err:
            return jsonify({'message': f"Error: {err}"}), 500
        finally:
            cur.close()
 
 
    @app.route("/updatePatient/<int:id>", methods=["PUT"])
    def update_patient(id):
        cur = mysql.connection.cursor()
        # print(doctor_id)
        try:
            if request.method == "PUT":
                new_testresults = request.json.get("testresults")
                if not new_testresults:
                    return jsonify({'message': "No 'testresults' provided in request body"}), 400
 
                cur.execute("UPDATE Records SET testresults = %s WHERE id = %s", (new_testresults, id))
                mysql.connection.commit()
 
                if cur.rowcount > 0:
                    updated_patient = {"id": id, "testresults": new_testresults}
                    return jsonify({'message': f"Test results updated for patient with ID {id}", 'updated_patient': updated_patient})
                else:
                    return jsonify({'message': f"Patient with ID {id} not found"}), 404
 
        except Exception as err:
            return jsonify({'message': f"Database error: {err}"}), 500
        finally:
            cur.close()
 
    @app.route("/deletePatient/<int:id>", methods=["DELETE"])
    def delete_patient(id):
        if request.method == "DELETE":
            cur = mysql.connection.cursor()
            try:
                cur.execute("SELECT * FROM Records WHERE id = %s", (id,))
                result = cur.fetchone()
                if not result:
                    return jsonify({"message": f"Patient with ID {id} not found"}), 404
 
                cur.execute("DELETE FROM Records WHERE id = %s", (id,))
                mysql.connection.commit()
                return jsonify({"message": f"Patient with ID {id} deleted successfully"}), 200
 
            except Exception as err:
                return jsonify({"message": f"Database error: {err}"}), 500
            finally:
                cur.close()
 
        return jsonify({"message": "Method not allowed"}), 405