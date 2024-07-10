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
 
 
def visualizationapp(app,mysql,jwt):
    @app.route("/piechartBloodGroup")
    def display_bloodGroups():
        cur = mysql.connection.cursor()
        cur.execute("select * from records")
        result = cur.fetchall()
 
        bloodGroup = [row[4] for row in result]
        unique_names_bloodGroup, name_counts_bloodGroup = np.unique(bloodGroup, return_counts=True)
 
        plt.figure(figsize=(8, 8))
        plt.pie(name_counts_bloodGroup, labels=unique_names_bloodGroup, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Blood Group')
 
        pie_chart_file_BG = "C:/PerficientProject/MediRecords-Seamless-Care-Starts-Here/static/Names_BG.png"
        plt.savefig(pie_chart_file_BG)
        plt.close()  
       
        return send_file(pie_chart_file_BG, mimetype='image/jpeg')
 
 
 
 
    @app.route("/piechartAge")
    def display_ageGroups():
 
        cur = mysql.connection.cursor()
        cur.execute("select age from records")
        rows = cur.fetchall()
        cur.close()
 
        df = pd.DataFrame(rows, columns=['Age'])
 
        bins = [0, 18, 50, np.inf]
        labels = ['Children (0-18)', 'Adults (19-50)', 'Old (50+)']
 
        age_groups = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
        age_group_counts = age_groups.value_counts().sort_index()
 
 
        plt.figure(figsize=(8, 8))
        plt.pie(age_group_counts, labels=age_group_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Age Groups')
 
 
        pie_chart_file_age = "C:/PerficientProject/MediRecords-Seamless-Care-Starts-Here/static/ageGroups_piechart.png"
        plt.savefig(pie_chart_file_age)
        plt.close()
 
        return send_file(pie_chart_file_age, mimetype='image/jpeg')
 
 
 
 
 
 
    @app.route("/barChartGender")
    def display_genders():
        cur = mysql.connection.cursor()
        cur.execute("select * from records")
        result = cur.fetchall()
 
        genders = [row[3] for row in result]
        unique_genders, genders_counts= np.unique(genders, return_counts=True)
 
        plt.figure(figsize=(10, 6))
        plt.bar(unique_genders, genders_counts, color='blue')
        plt.xlabel('genders')
        plt.ylabel('Count')
        plt.title('Distribution of genders')
        plt.xticks(rotation=45)
        plt.tight_layout()
 
        bar_chart_file_genders = "C:/PerficientProject/MediRecords-Seamless-Care-Starts-Here/static/Names_genders_bar.png"
        plt.savefig( bar_chart_file_genders)
        plt.close()
 
        return send_file(bar_chart_file_genders, mimetype='image/jpeg')
 
 
 
    @app.route("/barChartAdmission")
    def display_admission():
        cur = mysql.connection.cursor()
        cur.execute("select * from records")
        result = cur.fetchall()
 
        admissions = [row[11] for row in result]
        unique_admissions, admissions_counts= np.unique(admissions, return_counts=True)
 
        plt.figure(figsize=(10, 6))
        plt.bar(unique_admissions, admissions_counts, color='blue')
        plt.xlabel('Admissions')
        plt.ylabel('Count')
        plt.title('Distribution of Admissions')
        plt.xticks(rotation=45)
        plt.tight_layout()
 
        bar_chart_file_admissions = "C:/PerficientProject/MediRecords-Seamless-Care-Starts-Here/static/Names_admissions_bar.png"
        plt.savefig(bar_chart_file_admissions)
        plt.close()
 
        return send_file(bar_chart_file_admissions, mimetype='image/jpeg')
 
 
    @app.route("/piechartMedicalConditions")
    def display_medicalconditions():
        cur = mysql.connection.cursor()
        cur.execute("select * from records")
        result = cur.fetchall()
       
        names = [row[5] for row in result]
        unique_names, name_counts = np.unique(names, return_counts=True)
 
        plt.figure(figsize=(8, 8))
        plt.pie(name_counts, labels=unique_names, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Disease')
 
        pie_chart_file = "C:/PerficientProject/MediRecords-Seamless-Care-Starts-Here/static/Names.png"
        plt.savefig(pie_chart_file)
        plt.close()  
 
        return send_file(pie_chart_file, mimetype='image/jpeg')
 