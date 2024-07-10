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


app=Flask(__name__)
mysql = MySQL(app)


app.config['JWT_SECRET_KEY'] = '123ath' 

jwt = JWTManager(app)

#authentication 
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


#insertion of datas
# record_json_path = "C:/Final_Project/MediRecords-Seamless-Care-Starts-Here-main/Datasetjson/""
@app.route("/insert")
def insert():
    record_path1 = "C:/Final_Project/MediRecords-Seamless-Care-Starts-Here-main/Dataset/"
    
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


@app.route("/insertdoctor")
def insertDoctor():
    doctor_path2="C:/Final_Project/MediRecords-Seamless-Care-Starts-Here-main/Datasetdoctor/"
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



#visualization
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

    pie_chart_file_BG = "static/Names_BG.png"
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


    pie_chart_file_age = "static/ageGroups_piechart.png"
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

    bar_chart_file_genders = "static/Names_genders_bar.png"
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

    bar_chart_file_admissions = "static/Names_admissions_bar.png"
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

    pie_chart_file = "static/Names.png"
    plt.savefig(pie_chart_file)
    plt.close()  

    return send_file(pie_chart_file, mimetype='image/jpeg')


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


#crud operations -- doctors
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



