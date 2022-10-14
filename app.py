from flask import Flask,render_template,request,flash
from flask_sqlalchemy import SQLAlchemy
import pymysql
import pandas as pd
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
    return "成功！"



## 登录
@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        json = request.get_json()
        email = json['email']
        password = json['password']
        if email!=None and password!=None:
            sql = "SELECT * FROM customer WHERE email ='%s' and password ='%s'" % (email, password)
            result = db.session.execute(sql).fetchall()
            dataframe = pd.DataFrame(result)
            if dataframe.empty != True:
                End = 'login success'
            else:
                End = 'login failed'
        else:
            End = 'Error'
    return End






if __name__ == '__main__':
    app.run(debug=True)
