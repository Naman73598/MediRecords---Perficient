def create_temp_table(mysql, app):
    app.config['MYSQL_DB'] = 'temporary'
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS Records (
                            ID INT PRIMARY KEY,
                            Name VARCHAR(50),
                            Age INT,
                            Gender VARCHAR(10),
                            BloodType VARCHAR(50),
                            MedicalCondition VARCHAR(50) ,
                            Doctor VARCHAR(50),
                            Hospital VARCHAR(50),
                            InsuranceProvider VARCHAR(50),
                            BillingAmount INT,
                            RoomNumber INT,
                            AdmissionType VARCHAR(50) ,
                            Medication VARCHAR(50),
                            TestResults VARCHAR(50) ,
                            DoctorID INT ,
                            DoctorSpecialization VARCHAR(10) ,
                            FOREIGN KEY (DoctorID) REFERENCES doctor(id)
                        );''')
            mysql.connection.commit()
            cur.close()
            return True
    except Exception as e:
        print(f"Error creating temp table: {e}")
        return False

