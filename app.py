from flask import*
import pymysql
import sms
app=Flask(__name__)

# connecting to the database
connection=pymysql.connect(host='localhost', user='root', password='', database='sokogardendb')
cursor= connection.cursor()

app.secret_key= "ewrtfyghujikitrerwsdfcvbjnkjuytresdxf"

@app.route('/')
def home():
    #cateogery clothes
    sql ='select* from products where product_category="Clothes"'
    cursor.execute(sql)
    Clothes=cursor.fetchall()

    #cateogery Smartphones
    sql2 ='select* from products where product_category="Smartphones"'
    cursor.execute(sql2)
    Smartphones=cursor.fetchall()

    #cateogery Electronics
    sql ='select* from products where product_category="Electronics"'
    cursor.execute(sql)
    Electronics=cursor.fetchall()

    #cateogery Others
    sql ='select* from products where product_category="Others"'
    cursor.execute(sql)
    Others=cursor.fetchall()

    

    return render_template('home.html',Clothes=Clothes,Smartphones=Smartphones, Electronics=Electronics,Others=Others)

# function to upload data to the database
@app.route('/upload', methods=['POST','GET'])
def upload():
    if request.method=='POST':
        product_name=request.form['product_name']
        product_desc=request.form['product_desc']
        product_cost=request.form['product_cost']
        product_category=request.form['product_category']
        product_image_name=request.files['product_image']
        product_image_name.save('static/images/'+product_image_name.filename)
        
        #   attaching data from the form to a variable in the python file 
        data=(product_name,product_desc,product_cost,product_category,product_image_name.filename)
        #  inserting to the database
        sql='insert into products(product_name,product_desc,product_cost,product_category,product_image_name) values(%s,%s,%s,%s,%s)'
        cursor.execute(sql,data)
        connection.commit()
        return render_template('upload.html',message_two='Product Uploaded Successfully')

    else:
        return render_template('upload.html',message_one='Please Upload Product')
# single item selection   
@app.route('/single/<product_id>')
def single(product_id):
    sql= 'select *from products where product_id=%s'
    cursor.execute(sql,product_id)
    product=cursor.fetchone()

    return render_template('single.html',product=product)

# register function
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        phone=request.form['phone']
        password1=request.form['password1']
        password2=request.form['password2']
        if len(password1)<8:
            return render_template('register.html',error='Password should be more than 8 characters')
        elif password1!=password2:
            return render_template('register.html',error='Password did not match check again..')
        else:
            data=(username,email,phone,password1)
            sql='insert into users(username,email,phone,password) values(%s,%s,%s,%s)'
            cursor.execute(sql,data)
            connection.commit()
            
            sms.send_sms(phone,'Thank for registering with Soko Garden')

            return render_template('register.html',message='Registered Succesfully....')
            
    else:
        return render_template('register.html', messager='Register to login')
    
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        data=(username,password)
        sql='select * from users where username=%s and password=%s'
        cursor.execute(sql,data)
        if cursor.rowcount==0:
            return render_template('login.html', error='Invalid Credentials')
        else:
            session['key']=username
            return redirect('/')
        
    else:
        return render_template('login.html')    
@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html', msg="You can login again")

# we only need one methost post since the is no condition being tested
@app.route('/mpesa', methods=['POST'])
def mpesa():
    # variable phone and amount will hold data from our payment form 
    phone=request.form['phone']
    amount=request.form['amount']
    # we import a module mpesa, where we have our function stk_push.
    import mpesa
    # we pass the phone variable and the amount variable to our stk_push fuchion which we imported
    mpesa.stk_push(phone,amount)
    # every fuction should have a retun hence an error will our hence we return a message to inform the buyer 
    # to cornfirm the payment from the phone and key in the  mpesa pin. after doing so one can go back to the 
    # to the home page using the / route
    return '<h3> Cornfirm payment from your phone, Delivery in minutes</h3>'\
    '<a href='/'>Back to Home page </a>'




app.run(debug=True,port=8005)