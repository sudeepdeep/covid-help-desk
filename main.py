from flask import Flask, render_template, request, session
import pyrebase
from datetime import date
config = {
    'apiKey': "AIzaSyDot6z-ZvksuuehT1zljyBs5AIIw6lb8hA",
    'authDomain': "covid-portfolio.firebaseapp.com",
    'databaseURL': "https://covid-portfolio-default-rtdb.firebaseio.com",
    'projectId': "covid-portfolio",
    'storageBucket': "covid-portfolio.appspot.com",
    'messagingSenderId': "453340073703",
    'appId': "1:453340073703:web:e663727d69543b87931c42",
    'measurementId': "G-5551Q0FKC0"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()



app = Flask(__name__)
app.secret_key ="covidportfolio"



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin',methods = ['GET','POST'])
def admin():
    if request.method =="POST":
        name= request.form['uname']
        pwd = request.form['psw']

        if name == "admin@gmail.com" and pwd == "12345":
            session['loggedin'] = True
            return render_template('auth.html')
    return render_template('admin.html')


@app.route('/authentication')
def authentication():
    if 'loggedin' in session:
        return render_template('auth.html')
    else:
        return render_template('admin.html')

@app.route('/oxygen',methods=['GET','POST'])
def oxygen():
    if request.method == 'POST':
        dist = request.form['district']
        session['dist'] = dist
        return render_template('oxygenmandal.html', dist = dist)
    return render_template('oxygen.html')


@app.route('/res',methods = ['GET','POST'])
def res():
    if request.method == 'POST':
        dist= session['dist']
        man = request.form['mandal']
        tod = date.today()
        data = db.child(tod).child(dist).child(man).get()
        return render_template('res.html',data =data,mandal = man)

    return render_template('oxygen.html')

@app.route('/savedata', methods = ['GET','POST'])
def savedata():
    if 'loggedin' in session:
        if request.method == "POST":
            thisday = date.today()
            district  = request.form['district']
            mandal = request.form['mandals']
            oxybeds  = request.form['oxygenbeds']
            covidhsptls = request.form['covidhsptls']
            hsptlsaddress = request.form['hsptlsaddr']
            plasmadonors = request.form['plsmadonors']
            data = {
                'Oxygen Beds' : oxybeds,
                'Covid Hospitals': covidhsptls,
                'Hospitals Address' : hsptlsaddress,
                'Plasma Donors' : plasmadonors
            }
            db.child(thisday).child(district).child(mandal).push(data)
            return render_template('auth.html', message = "successfully updated..")


    return render_template('res.html')
if __name__ == '__main__':

    app.run(debug=True)