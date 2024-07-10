
def create_doctor_table(mysql,app):
    app.config['MYSQL_DB'] = 'temporary'
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS doctor (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(50) NOT NULL,
                        specialization VARCHAR(100) NOT NULL)''')
            mysql.connection.commit()
            cur.close()
            return True
    except Exception as e:
        print(f"Error creating doctor table: {e}")
        return False
    