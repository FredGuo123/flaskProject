import random

from flask import Flask,render_template,request,flash
from flask_sqlalchemy import SQLAlchemy
import pymysql
import pandas as pd
from datetime import datetime
import gpsd
import datetime
from math import radians, cos, sin, asin, sqrt
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
            sql1 = "SELECT type FROM customer WHERE email ='%s' and password ='%s'" % (email, password)
            result1 = db.session.execute(sql1).fetchall()
            dataframe1 = pd.DataFrame(result1)
            sql2 = "SELECT type FROM customer WHERE contact ='%s' and password ='%s'" % (email, password)
            result2 = db.session.execute(sql2).fetchall()
            dataframe2 = pd.DataFrame(result2)
            if dataframe1.empty!= True:
                type = dataframe1.at[0, 'type']
                if type==0:
                    End='customer'
                elif type==1:
                    End='operator'
                elif type==2:
                    End='manager'
            elif dataframe2.empty!= True:
                type = dataframe2.at[0, 'type']
                if type == 0:
                    End='customer'
                elif type == 1:
                    End='operator'
                elif type == 2:
                    End='manager'
            else:
                End='login failed'
        else:
            End='Error'
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

@app.route('/operator-hubdetails/',methods=['GET','POST'])
def operator_hubdetails():
    if request.method == 'POST':
        json = request.get_json()
        hub_name = json['hub_name']
        sql1 = "SELECT car_id, model_id, brand, seat, price FROM vehicle WHERE hub_id = (SELECT hub_id FROM hub WHERE hub_name='{}' or coordinate='{}')".format(hub_name, hub_name)
        result1 = db.session.execute(sql1)
        dataframe1 = pd.DataFrame(result1)
        dataframe1_json = dataframe1.to_json(orient="index",force_ascii=False)

        sql2 = "SELECT car_id, model_id, brand, seat, price FROM vehicle WHERE hub_id = (SELECT hub_id FROM hub WHERE hub_name='{}' or coordinate='{}') and status=0".format(hub_name, hub_name)
        result2 = db.session.execute(sql2)
        dataframe2 = pd.DataFrame(result2)
        dataframe2_json = dataframe2.to_json(orient="index", force_ascii=False)

        sql3 = "SELECT car_id, model_id, brand, seat, price FROM vehicle WHERE hub_id = (SELECT hub_id FROM hub WHERE hub_name='{}' or coordinate='{}') and status=1".format(
            hub_name, hub_name)
        result3 = db.session.execute(sql3)
        dataframe3 = pd.DataFrame(result3)
        dataframe3_json = dataframe3.to_json(orient="index", force_ascii=False)

        sql4 = "SELECT car_id, model_id, brand, seat, price FROM vehicle WHERE hub_id = (SELECT hub_id FROM hub WHERE hub_name='{}' or coordinate='{}') and status=2".format(
            hub_name, hub_name)
        result4 = db.session.execute(sql4)
        dataframe4 = pd.DataFrame(result4)
        dataframe4_json = dataframe4.to_json(orient="index", force_ascii=False)
    return {'cars_in_hub':dataframe1_json, 'cars_taken':dataframe2_json, 'New cars':dataframe3_json, 'car_need_repair':dataframe4_json}


@app.route('/user_profileediting/',methods=['GET','POST'])
def user_profileediting():
    if request.method == 'POST':
        json = request.get_json()
        cus_id = json['cus_id']
        email = json['email']
        password = json['password']
        type = json['type']
        name = json['name']
        last_name = json['last_name']
        driver_no = json['driver_no']
        expiry_date = json['expiry_date']
        contact = json['contact']
        emergency_name = json['emergency_name']
        emergency_contact = json['emergency_contact']
        sql1 = "DELETE FROM customer WHERE cus_id='{}'".format(cus_id)
        db.session.execute(sql1)
        db.session.commit()
        dataframe = pd.DataFrame()
        while dataframe.empty:
            sql1 = "SELECT COUNT(*) FROM customer"
            result1 = db.session.execute(sql1).fetchall()
            dataframe = pd.DataFrame(result1)
            cus_id_num = dataframe.at[0, 'COUNT(*)']
            cus_id = 'GLA' + str(cus_id_num+1)
            sql2 = "INSERT INTO customer(cus_id, email, password, type, name, last_name, driver_no, expiry_date, contact, emergency_name, emergency_contact) VALUES ( '{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                cus_id, email, password, type, name, last_name, driver_no, expiry_date, contact, emergency_name,
                emergency_contact)
            db.session.execute(sql2)
            db.session.commit()

    return 'Finish!'

@app.route('/user-reportdefective/',methods=['GET', 'POST'])
def user_reportdefective():
    if request.method == 'POST':
        json = request.get_json()
        car_id = json['car_id']
        brand = json['brand']
        hub_id = json['hub_id']
        problem = json['problem']
        comments = json['comments']
        sql1 = "UPDATE vehicle SET status=REPLACE(status, {}, {}) where car_id ='{}'" .format(0, 2, car_id)
        db.session.execute(sql1)
        db.session.commit()

    return "Success!"

@app.route('/user-return/',methods=['GET', 'POST'])
def user_return():
    if request.method == 'POST':
        json = request.get_json()
        car_id = json['car_id']

        sql1 = "SELECT COUNT(*) FROM transaction"
        result1 = db.session.execute(sql1).fetchall()
        dataframe1 = pd.DataFrame(result1)
        tn_id_num = dataframe1.at[0, 'COUNT(*)']
        tn_id = 'GLA' + str(tn_id_num+1)

        sql2 = "SELECT hub_id FROM vehicle WHERE car_id='{}'".format(car_id)
        result2 = db.session.execute(sql2).fetchall()
        dataframe2 = pd.DataFrame(result2)
        from_hub_id = dataframe2.at[0, 'hub_id']

        to_hub_id = json['to_hub_id']
        cus_id = json['cus_id']
        from_timestamp = json['from_timestamp']
        to_timestamp = json['to_timestamp']

        from_timestamp_date = datetime.datetime.strptime(from_timestamp, '%Y-%m-%d %H:%M')
        to_timestamp_date = datetime.datetime.strptime(to_timestamp, '%Y-%m-%d %H:%M')
        duration = to_timestamp_date-from_timestamp_date
        day = duration.days
        hour = duration.seconds / 3600
        total_hour = day*24+hour
        sql6 = "SELECT price FROM vehicle WHERE car_id='{}'".format(car_id)
        result6 = db.session.execute(sql6).fetchall()
        dataframe6 = pd.DataFrame(result6)
        car_price = dataframe6.at[0, 'price']
        total_price = total_hour*car_price

        sql3 = "INSERT INTO transaction(tn_id, from_hub_id, to_hub_id, cus_id, from_timestamp, to_timestamp, car_id, total_price) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', {})".format(tn_id, from_hub_id, to_hub_id, cus_id, from_timestamp, to_timestamp, car_id, total_price)
        db.session.execute(sql3)
        db.session.commit()

        sql4 = "UPDATE vehicle SET status=REPLACE(status, {}, {}) where car_id ='{}'".format(0, 1, car_id)
        db.session.execute(sql4)
        db.session.commit()

        sql5 = "UPDATE vehicle SET hub_id=REPLACE(hub_id, '{}', '{}') where car_id ='{}'".format(from_hub_id, to_hub_id, car_id)
        db.session.execute(sql5)
        db.session.commit()


        return "Finish"

@app.route('/operator-movevehicles/show-cars-in-hub/', methods=['GET', 'POST'])
def operator_movevehicles():
    if request.method == 'POST':
        json = request.get_json()
        hub_name = json['hub_name']
        sql1 = "SELECT car_id FROM vehicle WHERE hub_id=(SELECT hub_id FROM hub WHERE hub_name='{}')".format(hub_name)
        result1 = db.session.execute(sql1)
        dataframe1 = pd.DataFrame(result1)
        dataframe1_json = dataframe1.to_json(orient="index", force_ascii=False)
    return dataframe1_json

@app.route('/operator-movevehicles/deliver-cars-to-hub/', methods=['GET', 'POST'])
def deliver_cars_to_hub():
    if request.method =='POST':
        json = request.get_json()
        hub_name = json['hub_name']
        car_id = json['car_id']
        sql1 = "SELECT hub_id FROM hub WHERE hub_name='{}'".format(hub_name)
        result1 = db.session.execute(sql1)
        dataframe1 = pd.DataFrame(result1)
        hub_id = dataframe1.at[0, 'hub_id']

        sql2 = "SELECT hub_id FROM vehicle WHERE car_id='{}'".format(car_id)
        result2 = db.session.execute(sql2).fetchall()
        dataframe2 = pd.DataFrame(result2)
        from_hub_id = dataframe2.at[0, 'hub_id']

        sql3 = "UPDATE vehicle SET hub_id=REPLACE(hub_id, '{}', '{}') where car_id ='{}'".format(from_hub_id, hub_id, car_id)
        db.session.execute(sql3)
        db.session.commit()

    return "Finish!"

@app.route('/operator-repairlist/', methods=['GET'])
def operator_repairlist():
    if request.method == 'GET':
        sql1 = "SELECT car_id, model_id, brand, seat, hub_id FROM vehicle WHERE status=2"
        result1 = db.session.execute(sql1)
        dataframe1 = pd.DataFrame(result1)
        dataframe1_json = dataframe1.to_json(orient="index", force_ascii=False)
    return dataframe1_json

@app.route('/operator-repairvehicles/', methods=['POST'])
def operator_repairvehicles():
    if request.method == 'POST':
        json = request.get_json()
        car_id = json['car_id']
        sql1 = "SELECT a.model_id, a.brand, seat, b.coordinate FROM vehicle a, hub b WHERE a.car_id='{}' and a.hub_id=b.hub_id".format(car_id)
        result1 = db.session.execute(sql1)
        dataframe1 = pd.DataFrame(result1)
        dataframe1_json = dataframe1.to_json(orient="index", force_ascii=False)
    return dataframe1_json

@app.route('/operator-repairvehicles/repaired/', methods=['POST'])
def repaired():
    if request.method == 'POST':
        json = request.get_json()
        car_id = json['car_id']
        sql1 = "UPDATE vehicle SET status=REPLACE(status, {}, {}) where car_id ='{}'".format(2, 1, car_id)
        db.session.execute(sql1)
        db.session.commit()
    return "Success!"

@app.route('/user-pay/', methods=['POST'])
def user_pay():
    if request.method == 'POST':
        json = request.get_json()
        car_id = json['car_id']
        from_timestamp = json['from_timestamp']
        to_timestamp = json['to_timestamp']
        sql1 = "SELECT a.model_id, a.brand, b.total_price FROM vehicle a, transaction b WHERE a.car_id='{}' and a.car_id=b.car_id and b.from_timestamp='{}' and b.to_timestamp".format(car_id, from_timestamp, to_timestamp)
        result1 = db.session.execute(sql1)
        dataframe1 = pd.DataFrame(result1)
        dataframe1_json = dataframe1.to_json(orient="index", force_ascii=False)
        return dataframe1_json

@app.route('/user-cardetails/', methods=['POST'])
def user_cardetails():
    if request.method == 'POST':
        json = request.get_json()
        car_id = json['car_id']
        sql1 = "SELECT a.model_id, a.brand, a.seat, b.hub_name, b.coordinate FROM vehicle a, hub b WHERE a.car_id='{}' and a.hub_id=b.hub_id".format(car_id)
        result1 = db.session.execute(sql1)
        dataframe1 = pd.DataFrame(result1)
        dataframe1_json = dataframe1.to_json(orient="index", force_ascii=False)
        return dataframe1_json

if __name__ == '__main__':
    app.run(debug=True)
