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
 
 
 
def adminapp(app,mysql,jwt):
   
    @app.route("/auth", methods=["POST"])
    def auth():
        if request.method == "POST":
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            cur = mysql.connection.cursor()
            try:
                cur.execute("SELECT id FROM admin WHERE username = %s and password = %s", (username, password,))
                result = cur.fetchone()
                if result:
                    access_token = create_access_token(identity=result[0])
                    return jsonify({'message': 'Admin logged in', 'access_token': access_token}), 200
                else:
                    return jsonify({'message': 'No such admin exists'}),404
            except Exception as e:
                return jsonify({'message': 'Error occurred: ' + str(e)})
            finally:
                cur.close()
 
        return jsonify({'message': 'Invalid request'})
 
    @app.route("/createAdmin", methods=["POST"])
    def create_admin():
        if request.method == "POST":
            username = request.json.get("username")
            password = request.json.get("password")
            email = request.json.get("email")
            confirmPassword = request.json.get("confirmPassword")
 
            if password != confirmPassword:
                return jsonify({"message": "Password doesn't match"}), 400
 
            cur = mysql.connection.cursor()
            try:
                cur.execute("SELECT username FROM admin WHERE username = %s", (username,))
                result = cur.fetchone()
                if result:
                    return jsonify({"message": "Admin with the same username already exists"}), 409
               
                cur.execute("INSERT INTO admin (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
                mysql.connection.commit()
                cur.execute("SELECT * FROM admin WHERE username = %s", (username,))
                inserted_admin = cur.fetchone()
 
                return jsonify({"message": "Admin created successfully", "user": inserted_admin}), 201  # 201 Created
            except Exception as err:
                return jsonify({"message": f"Database error: {err}"}), 500
            finally:
                cur.close()
 
        return jsonify({"message": "Method not allowed"}),405