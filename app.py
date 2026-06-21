from flask import Flask, render_template, request, redirect, session, url_for, flash, current_app, abort
import sqlite3
from dotenv import load_dotenv
load_dotenv()
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config
from extensions import mail, initDB, verifyConfirmationToken, sendConfirmationEmail
from trainStations import calculateLineSegment, addStations, lineStations  #addStations function will only add stations if they have been deleted.
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect
import subprocess
import hmac
import hashlib
import threading
import requests
import os

app = Flask(__name__)
app.config.from_object(Config)
mail.init_app(app)
app.secret_key = os.environ.get('SECRET_KEY')

#For Github and Python Anywhere integration
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '').encode()
PA_USERNAME = 'piccolif26'
PA_API_TOKEN = os.environ.get('PA_API_TOKEN', '')
PA_DOMAIN = "sydneystationkeeper-piccolif26.pythonanywhere.com"
REPO_PATH = '/home/piccolif26/AT3_SE_HSC_2026'

#Protecting my website from Cross Site Request Forgery
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
csrf = CSRFProtect(app) #I just imagine this function as a knight in front of a princess "I'll protect you!" in a very Brittish accent
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Strict'
)

#Getting database and making sure the stations table is populated
with app.app_context():
    initDB()
    addStations(app.config['DATABASE'])
    
#initialising globals used in various functions
global trainSets
trainSets = ["Waratah Series 2 | B Set", "Waratah Series 1 | A Set", "Millennium | M Set", "Alstom Metropolis", "Mariyung | D Set", "Tangara | T Set", "Oscar | H Set", "K Set"]

global stationsList
stationsList = ['Allawah', 'Arncliffe', 'Artarmon', 'Ashfield', 'Asquith', 'Auburn', 'Banksia', 'Bankstown', 'Bardwell Park', 'Beecroft', 'Berala', 'Berowra', 'Bella Vista', 'Beverly Hills', 'Bexley North', 'Birrong', 'Blacktown', 'Bondi Junction', 'Barangaroo', 'Burwood', 'Cabramatta', 'Campbelltown', 'Canley Vale', 'Caringbah', 'Carlton', 'Carramar', 'Casula', 'Castle Hill', 'Central', 'Chatswood', 'Cheltenham', 'Chester Hill', 'Cherrybrook', 'Circular Quay', 'Clarendon', 'Clyde', 'Como', 'Concord West', 'Cronulla', 'Croydon', 'Crows Nest', 'Denistone', 'Domestic Airport', 'Doonside', 'East Hills', 'East Richmond', 'Eastwood', 'Edgecliff', 'Edmondson Park', 'Emu Plains', 'Engadine', 'Epping', 'Erskineville', 'Fairfield', 'Flemington', 'Gadigal', 'Glenfield', 'Gordon', 'Granville', 'Green Square', 'Guildford', 'Gymea', 'Harris Park', 'Heathcote', 'Hills Showground', 'Holsworthy', 'Homebush', 'Hornsby', 'Hurstville', 'Ingleburn', 'International Airport', 'Jannali', 'Kellyville', 'Killara', 'Kings Cross', 'Kingsgrove', 'Kingswood', 'Kirrawee', 'Kogarah', 'Leightonfield', 'Leppington', 'Leumeah', 'Lewisham', 'Lidcombe', 'Lindfield', 'Liverpool', 'Loftus', 'Macarthur', 'Macdonaldtown', 'Macquarie Park', 'Macquarie Fields', 'Macquarie University', 'Marayong', 'Martin Place', 'Mascot', 'Meadowbank', 'Merrylands', 'Milsons Point', 'Minto', 'Miranda', 'Mortdale', 'Mount Colah', 'Mount Druitt', 'Mount Kuring-gai', 'Mulgrave', 'Museum', 'Narwee', 'Newtown', 'Normanhurst', 'North Strathfield', 'North Ryde', 'North Sydney', 'Norwest', 'Oatley', 'Olympic Park', 'Padstow', 'Panania', 'Parramatta', 'Pendle Hill', 'Pennant Hills', 'Penrith', 'Penshurst', 'Petersham', 'Pymble', 'Quakers Hill', 'Redfern', 'Regents Park', 'Revesby', 'Rhodes', 'Richmond', 'Riverstone', 'Riverwood', 'Rockdale', 'Rooty Hill', 'Roseville', 'Rouse Hill', 'Schofields', 'Sefton', 'Seven Hills', 'St James', 'St Leonards', 'St Marys', 'St Peters', 'Stanmore', 'Strathfield', 'Summer Hill', 'Sutherland', 'Sydenham', 'Tallawong', 'Tempe', 'Thornleigh', 'Toongabbie', 'Town Hall', 'Turramurra', 'Turrella', 'Victoria Cross', 'Villawood', 'Vineyard', 'Wahroonga', 'Waitara', 'Warrawee', 'Warwick Farm', 'Waterfall', 'Waterloo', 'Waverton', 'Wentworthville', 'Werrington', 'West Ryde', 'Westmead', 'Windsor', 'Wolli Creek', 'Wollstonecraft', 'Woolooware', 'Wynyard', 'Yagoona', 'Yennora']

global trainLines
trainLines = ["M1", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9"]

#Integrating 
@app.route('/git_pull', methods=['POST'])
@csrf.exempt #Exempt because Git Hub can't supply a token
def git_pull():
    # Verify GitHub's HMAC-SHA256 signature to authenticate the webhook sender
    signature = request.headers.get('X-Hub-Signature-256') or ''
    expected = 'sha256=' + hmac.new(WEBHOOK_SECRET, request.data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        abort(403)  # Reject requests with invalid signatures
 
    def deploy():
        # Pull latest code from the main branch
        subprocess.run(['git', '-C', REPO_PATH, 'fetch', 'origin'], capture_output=True, text=True)
        subprocess.run(['git', '-C', REPO_PATH, 'reset', '--hard', 'origin/main'], capture_output=True, text=True)
        # Reload the PythonAnywhere web app via their REST API
        requests.post(
            f'https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/webapps/{PA_DOMAIN}/reload/',
            headers={'Authorization': f'Token {PA_API_TOKEN}'}
        )
 
    # Run deploy on a background thread — response must be sent before reload kills the worker
    threading.Thread(target=deploy).start()
    return 'OK', 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        fName = escape(request.form['fName'])
        lName = escape(request.form['lName'])
        email = escape(request.form['email'])
        username = escape(request.form['username'])
        displayName = escape(request.form['displayName'])
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if not fName or not lName or not email or not username or not displayName or not password or not confirmPassword:
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        if password != confirmPassword:
            flash("Passwords do not match.", "error")
            return redirect(url_for('register'))

        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()

        cursor.execute('SELECT email, username, displayName FROM users WHERE email = ? OR username = ? OR displayName = ?', (email, username, displayName))
        results = cursor.fetchone()

        if results:
            existingEmail = results[0]
            existingUsername = results[1]
            existingDisplayName = results[2]
        else:
            existingEmail = None
            existingUsername = None
            existingDisplayName = None

        if existingEmail == email:
            flash("Email already exists. Please choose a different email.", "error")
            conn.close()
            return redirect(url_for('register'))
        if existingUsername == username:
            flash("Username already exists. Please choose a different username.", "error")
            conn.close()
            return redirect(url_for('register'))
        if existingDisplayName == displayName:
            flash("Display name already exists. Please choose a different display name.", "error")
            conn.close()
            return redirect(url_for('register'))

        #Is this something I should turn into a function?
        if len(fName) > 50:
            flash("First name is too long.", "error")
            conn.close()
            return redirect(url_for('register'))
        if len(lName) > 50:
            flash("Last name is too long.", "error")
            conn.close()
            return redirect(url_for('register'))
        if len(email) > 100:
            flash("Email is too long.", "error")
            conn.close()
            return redirect(url_for('register'))
        if len(username) > 50:
            flash("Username is too long.", "error")
            conn.close()
            return redirect(url_for('register'))
        if len(displayName) > 30:
            flash("Display name is too long.", "error")
            conn.close()
            return redirect(url_for('register'))

        cursor.execute('INSERT INTO users (fName, lName, email, username, displayName, password) VALUES (?, ?, ?, ?, ?, ?)',
                    (fName, lName, email, username, displayName, generate_password_hash(password)))
        conn.commit()
        conn.close()

        sendConfirmationEmail(email)

        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        usernameOrEmail = escape(request.form['usernameOrEmail'])
        password = request.form['password']

        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('SELECT password, username, id, status, icon, fName, lName, verified FROM users WHERE username = ? OR email = ?', (usernameOrEmail, usernameOrEmail))
        result = cursor.fetchone()
        conn.close()

        if result and result[7] == 0:
            flash("Please confirm your email before logging in.", "error")
            return redirect(url_for('login'))
        elif not result:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

        if result and check_password_hash(result[0], password):
            flash("Login successful!", "success")
            session['userID'] = result[2]
            session['fName'] = result[5]
            session['lName'] = result[6]
            session['username'] = result[1]
            session['status'] = result[3]
            session['icon'] = result[4]
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = verifyConfirmationToken(token)
    except Exception:
        flash("The confirmation link is invalid or has expired.", "error")
        return redirect(url_for('login'))

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET verified = 1, verifiedAt = CURRENT_TIMESTAMP WHERE email = ?', (email,))
    conn.commit()
    conn.close()

    flash("Email confirmed! You can now log in.", "success")
    return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/')
def index():
    global trainSets, stationsList
    if 'userID' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''
                SELECT trips.id, trips.created_at, trip_stops.stop_order, stations.name, trip_stops.line_segment, trip_stops.train_set
                FROM trips
                JOIN trip_stops
                ON trips.id = trip_stops.trip_id
                JOIN stations
                ON trip_stops.station_id = stations.id
                WHERE trips.user_id = ?
                ORDER BY trips.created_at DESC, trip_stops.stop_order ASC''', (session['userID'],))
    journeysTuple = cursor.fetchall()
    if not journeysTuple:
        return render_template('index.html', trains=trainSets, stations=stationsList, journeys=[])
    journeys = [list(row) for row in journeysTuple]
    currentID = journeys[0][0]
    currentTime = journeys[0][1]
    formattedJourneys = []
    individualJourney = []
    stationList = []
    lineList = []
    trainList = []
    for journey in journeys:
        if currentID != journey[0]:
            individualJourney.append(currentID)
            dateTimeObject = datetime.fromisoformat(currentTime)
            readableTime = dateTimeObject.strftime("%A, %B %d, %I:%M %p")
            individualJourney.append(readableTime)
            individualJourney.append(stationList)
            individualJourney.append(lineList)
            individualJourney.append(trainList)
            formattedJourneys.append(individualJourney)
            individualJourney = []
            currentID = journey[0]
            currentTime = journey[1]
            stationList = []
            lineList = []
            trainList = []
            stationList.append(journey[3])
            lineList.append(journey[4])
            trainList.append(journey[5])
        else:
            stationList.append(journey[3])
            lineList.append(journey[4])
            trainList.append(journey[5])

    individualJourney.append(currentID)
    dateTimeObject = datetime.fromisoformat(currentTime)
    readableTime = dateTimeObject.strftime("%A, %B %d, %I:%M %p")
    individualJourney.append(readableTime)
    individualJourney.append(stationList)
    individualJourney.append(lineList)
    individualJourney.append(trainList)
    formattedJourneys.append(individualJourney)
    
    return render_template('index.html', trains=trainSets, stations=stationsList, journeys=formattedJourneys)

@app.route('/submitJourney', methods=['POST'])
def submitJourney():
    if 'userID' not in session:
        flash("Please log in to submit a journey.", "error")
        return redirect(url_for('login'))
    firstStop = escape(request.form['startLocation'])
    middleStops = [escape(stop) for stop in request.form.getlist('middle')]
    lastStop = escape(request.form['endLocation'])
    
    firstTrain = escape(request.form['startSetDropdown'])
    middleTrains = [escape(train) for train in request.form.getlist('middleSetDropdown')]

    lineSegment = [escape(line) for line in request.form.getlist('lineChoice')]

    if not firstStop or not lastStop or not firstTrain:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for('index'))

    if firstStop not in stationsList or lastStop not in stationsList or any(s not in stationsList for s in middleStops):
        flash("Please select valid stations.", "error")
        return redirect(url_for('index'))

    if any(not t for t in middleTrains) or not firstTrain:
        flash("Please select a train for each stop.", "error")
        return redirect(url_for('index'))

    allStops = [firstStop] + middleStops + [lastStop]
    allTrains = [firstTrain] + middleTrains

    if len(lineSegment) != len(allStops) - 1:
        flash("Please complete all line segment selections.", "error")
        return redirect(url_for('index'))

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO trips (user_id, created_at) VALUES (?, ?)', (session['userID'], datetime.now()))
        trip_id = cursor.lastrowid

        for i in range(len(allStops) - 1):
            currentStop = allStops[i]
            currentTrain = allTrains[i] if i < len(allTrains) else None

            cursor.execute("SELECT id FROM stations WHERE name = ?", (currentStop,))
            row = cursor.fetchone()
            station_id = row[0] if row else None

            cursor.execute("INSERT INTO trip_stops (trip_id, station_id, stop_order, line_segment, train_set) VALUES (?, ?, ?, ?, ?)",
                           (trip_id, station_id, i, lineSegment[i], currentTrain))

        cursor.execute("SELECT id FROM stations WHERE name = ?", (lastStop,))
        row = cursor.fetchone()
        station_id = row[0] if row else None
        cursor.execute("INSERT INTO trip_stops (trip_id, station_id, stop_order, line_segment, train_set) VALUES (?, ?, ?, ?, ?)",
                       (trip_id, station_id, len(allStops) - 1, None, None))

        conn.commit()
    except:
        flash("Sorry, something went wrong when trying to save your trip. Please make sure your selections are correct, and stations connect on valid lines.", "error")
        redirect(url_for('index'))
    finally:
        conn.close()

    return redirect(url_for('index'))

'''1. Favourite train set 🚡
2. Favourite stations 🚡
3. Favourite Line 🚡
4. Most travelled day of the week (percieved harder)
5. Count number of trips created, compare with other users (anonymous) 🚡
6. Bunch of leaderboard stuff
7. total stations 🚡
8. count for each line 🚡
9. count for each train 🚡'''

@app.route('/stats')
def stats():
    
    global trainLines
    
    if 'userID' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    
    
    allStats = {}
    cursor.execute('''SELECT st.name, COUNT(ts.station_id) AS st_count
                   FROM stations AS st
                   JOIN trip_stops AS ts
                   ON ts.station_id = st.id
                   JOIN trips AS tr 
                   ON ts.trip_id = tr.id 
                   WHERE tr.user_id = ?
                   GROUP BY st.name
                   ORDER BY st_count DESC
                   LIMIT 10''', 
                   (session['userID'],))
    allStats['popStations'] = [list(row) for row in cursor.fetchall()]
    
    cursor.execute('''SELECT ts.train_set,
                   COUNT(ts.train_set) as train_set_count
                   FROM trip_stops AS ts
                   JOIN trips AS tr
                   ON ts.trip_id = tr.id
                   WHERE tr.user_id = ?
                   GROUP BY ts.train_set
                   ORDER BY train_set_count DESC
                   LIMIT 1
                   ''', 
                   (session['userID'],))
    results = cursor.fetchone()
    allStats['popTrain'] = list(results) if results else []

    cursor.execute('''SELECT ts.line_segment,
                   COUNT(ts.line_segment) AS line_count
                   FROM trip_stops AS ts
                   JOIN trips AS tr
                   ON tr.id = ts.trip_id
                   WHERE tr.user_id = ?
                   GROUP BY ts.line_segment
                   ORDER BY line_count DESC
                   LIMIT 1
                   ''',
                   (session['userID'],))
    results = cursor.fetchone()
    allStats['popLine'] = list(results) if results else []

    cursor.execute('''SELECT COUNT(station_id)
                   FROM trip_stops AS ts
                   JOIN trips AS tr
                   ON tr.id = ts.trip_id
                   WHERE tr.user_id = ?''',
                   (session['userID'],))
    results = cursor.fetchone()
    allStats['totalStations'] = list(results) if results else []

    cursor.execute('''SELECT line_segment, COUNT(line_segment) AS line_count
                   FROM trip_stops AS ts
                   JOIN trips AS tr
                   ON tr.id = ts.trip_id
                   WHERE tr.user_id = ?
                   GROUP BY ts.line_segment
                   ORDER BY line_count DESC''',
                   (session["userID"],))
    allStats['lineCounts'] = [list(row) for row in cursor.fetchall()]

    cursor.execute('''SELECT train_set, COUNT(train_set) AS train_count
                   FROM trip_stops AS ts
                   JOIN trips AS tr
                   ON tr.id = ts.trip_id
                   WHERE tr.user_id = ?
                   GROUP BY ts.train_set
                   ORDER BY train_count DESC''',
                   (session["userID"],))
    allStats['trainCounts'] = [list(row) for row in cursor.fetchall()]
    
    #AI used for this query, was unable to figure it out myself. Selects your rank based on number of trips logged and finds your place against other users.
    cursor.execute('''SELECT rank, trip_count 
                   FROM (
                        SELECT user_id,
                            COUNT(*) AS trip_count,
                            RANK() OVER (ORDER BY COUNT(*) DESC) AS rank
                        FROM trips
                        GROUP BY user_id
                        )
                   WHERE user_id = ? ''', 
                   (session['userID'],))
    results = cursor.fetchone()
    allStats["Leaderboard"] = [list(results)] if results else [[None, None]]
    
    
    
    print(allStats)
    conn.close()
    return render_template('statistics.html', allStats=allStats)

@app.route("/stations")
def stations():
    global trainLines
    
    if 'userID' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''SELECT DISTINCT st.name
                   FROM stations AS st
                   JOIN trip_stops AS ts
                   ON ts.station_id = st.id
                   JOIN trips AS tr
                   ON ts.trip_id = tr.id
                   WHERE tr.user_id = ?''',
                   (session['userID'],))
    stationsVisited = {row[0] for row in cursor.fetchall()}
    
    tracker = {line: [] for line in trainLines}
    for line, stations in lineStations.items():
        if line in tracker:
            for station in stations:
                tracker[line].append({'name': station, 'visited': station in stationsVisited})
    print(tracker)
    conn.close()
    return render_template("stations.html", tracker=tracker, trainLines=trainLines)

if __name__ == '__main__':
    app.run(debug=True)
