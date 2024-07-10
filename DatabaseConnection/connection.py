from flask_mysqldb import MySQL

def create_connection(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'password123'

def create_database(mysql,app):
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("create database if not exists temporary")
            cur.close()
            return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False



