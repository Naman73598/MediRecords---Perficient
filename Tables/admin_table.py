

def create_admin_table(mysql,app):
    app.config['MYSQL_DB'] = 'temporary'
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS admin (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        password VARCHAR(20) NOT NULL)''')
            mysql.connection.commit()
            cur.close()
            return True
    except Exception as e:
        print(f"Error creating admin table: {e}")
        return False
    
