from flask import Flask, render_template, request, session
import pyrebase
from datetime import date
import os
from twilio.rest import Client
import random 
import string
import tweepy 
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import tweepy 
from itertools import islice 








firebase = pyrebase.initialize_app(config)
db = firebase.database()



app = Flask(__name__)
app.secret_key ="covidportfolio"

main_tweet = {}
tweet_data = {}
toda = date.today()
tweets  = tweepy.Cursor(api.search, q = "#covidtelugu", lang = 'en', since_date = toda, tweet_mode = 'extended').items(10)

list_tweet = [tweet for tweet in tweets]


lists = ['Image', 'Description', 'Username', 'location', 'Text', 'Following', 'Followers']







@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('index.html', types = 'Admin Logout')
    else:
        val = 0
        for i in list_tweet:
            

            username = i.user.screen_name
            description = i.user.description
            location = i.user.location
            try:
                text = i.retweeted_status.full_text
            except AttributeError:
                text = i.full_text
            following = i.user.friends_count
            followers = i.user.followers_count 
            img_url = i.user.profile_image_url

            
            tweet_data[f'Image{val}'] = img_url
            tweet_data[f'Username{val}'] = username
            tweet_data[f'description{val}'] = f'Description: {description}'
            tweet_data[f'location{val}'] = f'Location: {location}'
            
            tweet_data[f'Text{val}'] = f'Message: {text}' 
            tweet_data[f'Followers{val}'] = f'Followers:{followers}' 
            tweet_data[f'Following{val}'] = f'Following: {following}' 


            main_tweet[f'tweet{val}'] = tweet_data
            val = val+1



        new_tweet = main_tweet['tweet0']
        c_td = list(new_tweet)
        values = new_tweet.values()
        v_td = list(values)
        leng = len(new_tweet)
        r_list = []
        for i in range(leng):
            if i %7 == 0 and i != 1:
                r_list.append(i + 1)
        return render_template('index.html',md = main_tweet ,td = new_tweet, c_td = c_td, leng = leng, v_td  = v_td, r_list = r_list)


@app.route('/logout')
def logout():
    session.pop('loggedin')
    return render_template('index.html')
@app.route('/admin',methods = ['GET','POST'])
def admin():
    if 'loggedin' in session:
        return render_template('auth.html', types = 'Admin Logout')
    if request.method =="POST":
        name= request.form['uname']
        pwd = request.form['psw']

        if name == "admin@gmail.com" and pwd == "12345":
            session['loggedin'] = True
            return render_template('auth.html', types = 'Admin Logout')
    return render_template('admin.html')


@app.route('/authentication')
def authentication():
    if 'loggedin' in session:
        return render_template('auth.html', types = 'Admin Logout')
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
        session['man'] = man
        tod = date.today()
        data = db.child(tod).child(dist).child(man).get()
        new_data = {}
        for i in data.each():
            for a,b in i.val().items(): 
                if a == "Covid Hospitals" or a == "Oxygen Beds" or a == "Hospitals Address" or a == "Plasma Donors":
                    new_data[a] = b
        try:
            return render_template('res.html',data = new_data,mandal = man)
        except:  
            return render_template('oxygenmandal.html',data = "No Data Found/Uploaded")


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
            vaccine  = request.form['vaccine']
            quarantine = request.form['quarantine']
            data = {
                'Oxygen Beds' : oxybeds,
                'Covid Hospitals': covidhsptls,
                'Hospitals Address' : hsptlsaddress,
                'Plasma Donors' : plasmadonors,
                'vaccine centers' : vaccine,
                'quarantine address' : quarantine
            }
            db.child(thisday).child(district).child(mandal).push(data)
            return render_template('auth.html', message = "successfully updated..", types = 'Admin Logout')


    return render_template('res.html')


@app.route('/phoneverification',methods=['GET','POST'])
def phoneverification():
    if 'verified' in session:
        if request.method == 'POST':
            mandal = session['man']
            dist = session['dist']
            return render_template('oxyres.html',man = mandal,dist = dist)
    else:

        return render_template('phoneverify.html')


@app.route('/verify', methods=['GET','POST'])
def verify():
    if request.method == 'POST':
        phoneno = request.form['phone']
        session['phone'] = phoneno
        uid = ''.join([random.choice(string.digits) for n in range(6)])
        session['uid'] = uid
        message = client.messages \
        .create(
            body=uid,
            from_='+18187219075',
            to= f'+91{phoneno}'
        )

        print(message.sid)

        return render_template('verification.html',phn = phoneno)

    return render_template('phoneverify.html')

@app.route('/verification', methods = ['GET','POST'])
def verification():
    if request.method == 'POST':  
        uid = session['uid']
        code = request.form['code']

        if uid == code:
            mandal = session['man']
            dist = session['dist']
            session['verified'] = True
            return render_template('oxyres.html', man = mandal, dist = dist)

        else:
            return render_template('verification.html')

    return render_template('oxyres.html')

@app.route('/oxyreg',methods = ['GET','POST'])
def oxyreg():
    if request.method == 'POST':
        mandal = session['man']
        dist = session['dist']
        phone = session['phone']
        return render_template('oxyres.html', man = mandal, dist = dist, mobile = phone)

@app.route('/oxypatient', methods = ['GET','POST'])
def oxypatient():
    if request.method == 'POST':
        session.pop('verified')
        thisday = date.today()
        name= request.form['name']
        level = request.form['level']
        address = request.form['address']
        number = request.form['phone']
        if level <= '65':
            message = client.messages \
            .create(
                body=f"Patient name: {name}\n Oxygen Level : {level}\n Phone Number : {number}\n Address : {address}",
                from_='+18187219075',
                to= f'+916302053596'
            )
            session.pop('man')
            session.pop('dist')
            session.pop('phone')
            return render_template('oxyres.html',message = "Successfully submitted")

        else:
            data = {"oxy level" : level, 'address' : address, 'mobile' : number }
            db.child(thisday).child('oxypatients').push(data)
            session.pop('man')
            session.pop('dist')
            session.pop('phone')
            return render_template('oxyres.html', message = "Successfully submitted")

app.config['GOOGLEMAPS_KEY'] =  'AIzaSyD9WbXO3_YeXt0BO0zvy01dpEwdNuSmtps'
GoogleMaps(app)
@app.route("/maps")
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="labelsmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
            {
                'lat': 37.4500,
                'lng': -122.1350,
                'label': "X"
            },
            {
                'lat':  37.4419,
                'lng':  -122.1419,
                'label': "Y"
            },
            {
                'lat': 37.4300,
                'lng': -122.1400,
                'label': "Z"
            }
        ]
    )
    return render_template('example.html', mymap=mymap, sndmap=sndmap)


@app.route('/hsptldist', methods=['GET','POST'])
def hsptldist():
    if request.method == 'POST':
        toda = date.today()
        dist = request.form['hsptldist']
        try:
            hsptl = db.child(toda).child(dist).get()

            return render_template('hospitallist.html', data = hsptl, dist = dist)

        except:

            return render_template('hospitallist.html', data1 = "No Data Found", dist = dist)

    return render_template('hospitallist.html')


@app.route('/vaccination', methods=['GET','POST'])
def vaccination():
    if request.method == 'POST':
        toda = date.today()
        dist = request.form['vaccine']
        try:
            hsptl = db.child(toda).child(dist).get()

            return render_template('vaccinecenters.html', data = hsptl, dist = dist)

        except:

            return render_template('vaccinecenters.html', data1 = "No Data Found", dist = dist)

    return render_template('vaccinecenters.html')


@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':

    app.run(debug=True)
