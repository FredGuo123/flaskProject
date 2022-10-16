import random

from flask import Flask,render_template,request,flash
from flask_sqlalchemy import SQLAlchemy
import pymysql
import pandas as pd
from datetime import datetime
pymysql.install_as_MySQLdb()


app = Flask(__name__, template_folder="template")
app.secret_key='hehe'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234567890@127.0.0.1/glasgow_progsd_teamproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 注册
@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        json = request.get_json()
        email = json['email']
        password1 = json['password1']
        password2 = json['password2']
        type = json['type']
        name = json['name']
        last_name = json['last_name']
        driver_no = json['driver_no']
        expiry_date = json['expiry_date']
        # expiry_date = (datetime.strptime(expiry_date, '%Y/%m/%d')).date()
        contact = json['contact']
        emergency_name = json['emergency_name']
        emergency_contact = json['emergency_contact']
        dataframe = pd.DataFrame()
        while dataframe.empty:
            sql1 = "SELECT COUNT(*) FROM customer"
            result1 = db.session.execute(sql1).fetchall()
            dataframe = pd.DataFrame(result1)
            cus_id_num = dataframe.at[0, 'COUNT(*)']
            cus_id = 'GLA' + str(cus_id_num)

            if email!=None and password1!=None and password2!=None:
                if password1 == password2:
                    sql1 = "INSERT INTO customer(cus_id, email, password, type, name, last_name, driver_no, expiry_date, contact, emergency_name, emergency_contact) VALUES ( '{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}')" .format(cus_id, email, password1, type, name, last_name, driver_no, expiry_date, contact, emergency_name, emergency_contact)
                    db.session.execute(sql1)
                    db.session.commit()
                else:
                    print('You password is not same!')
            else:
                print('You enter is wrong!')
    return "Finish！"




## 登录
@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        json = request.get_json()
        email = json['email']
        password = json['password']
        if email!=None and password!=None:
            sql1 = "SELECT * FROM customer WHERE email ='%s' and password ='%s'" % (email, password)
            result1 = db.session.execute(sql1).fetchall()
            dataframe1 = pd.DataFrame(result1)
            sql2 = "SELECT * FROM customer WHERE contact ='%s' and password ='%s'" % (email, password)
            result2 = db.session.execute(sql2).fetchall()
            dataframe2 = pd.DataFrame(result2)
            if dataframe1.empty!= True:
                End = 'login success'
            elif dataframe2.empty!= True:
                End = 'login success'
            else:
                End = 'login failed'
        else:
            End = 'Error'
    return End

@app.route('/forget/',methods=['GET','POST'])
def forget():
    if request.method == 'POST':
        json = request.get_json()
        email = json['email']
        # vercode = json['vercode']
        password1 = json['password1']
        password2 = json['password2']
        if email != None:
            sql1 = "SELECT * FROM customer WHERE email ='%s'" % (email)
            result1 = db.session.execute(sql1).fetchall()
            dataframe1 = pd.DataFrame(result1)
            sql2 = "SELECT * FROM customer WHERE contact ='%s'" % (email)
            result2 = db.session.execute(sql2).fetchall()
            dataframe2 = pd.DataFrame(result2)
            if dataframe1.empty!=True or dataframe2.empty!=True:
                if password1 == password2:
                    if dataframe1.empty!=True:
                        password_old = dataframe1.at[0, 'password']
                        sql3 = "UPDATE customer SET password=REPLACE(password, '%s', '%s') where email ='%s' OR contact ='%s'" % (password_old, password1, email, email)
                        db.session.execute(sql3)
                        db.session.commit()
                    elif dataframe2.empty!=True:
                        password_old = dataframe2.at[0, 'password']
                        sql4 = "UPDATE customer SET password=REPLACE(password, '%s', '%s') where email ='%s' OR contact ='%s'" % (password_old, password1, email, email)
                        db.session.execute(sql4)
                        db.session.commit()
                else:
                    print('The two password is not the same')
            else:
                print('No such user!')
        else:
            print('You input nothing correct!')
    return 'Finish'




if __name__ == '__main__':
    app.run(debug=True)
