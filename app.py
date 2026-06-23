from functools import wraps

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
#For Github and Python Anywhere integration
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '').encode()
PA_USERNAME = 'piccolif26'
PA_API_TOKEN = os.environ.get('PA_API_TOKEN', '')
PA_DOMAIN = "sydneystationkeeper-piccolif26.pythonanywhere.com"
REPO_PATH = '/home/piccolif26/AT3_SE_HSC_2026'

#Limiting requests to 15 per minute, less for login to prevent brute force attacks
limiter = Limiter(get_remote_address, app=app, default_limits=["15 per minute"])

#Protecting my website from Cross Site Request Forgery
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
csrf = CSRFProtect(app) #I just imagine this function as a knight in front of a princess "I'll protect you!" in a very Brittish accent
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Strict'
)

def login_required(f):
    """ Wrapper to enforce user login on routes; Redirects to login page if not authenticated.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "userID" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper
 
def admin_required(f):
    """ Wrapper to enforce admin login on routes; Redirects to index page if not authorized.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session["status"] != "admin":
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

#Getting database and making sure the stations table is populated
with app.app_context():
    initDB()
    addStations(app.config['DATABASE'])
    
#initialising globals used in various functions
global trainSets
trainSets = ["Waratah Series 2 | B Set", "Waratah Series 1 | A Set", "Millennium | M Set", "Alstom Metropolis", "Mariyung | D Set", "Tangara | T Set", "Oscar | H Set"]

global trainImages
trainImages = {
    "Waratah Series 2 | B Set": "waratah2",
    "Waratah Series 1 | A Set": "waratah1",
    "Millennium | M Set": "milenium",
    "Alstom Metropolis": "metropolis",
    "Mariyung | D Set": "mariyung",
    "Tangara | T Set": "tangara",
    "Oscar | H Set": "oscar"
}

global stationsList
stationsList = ['Allawah', 'Arncliffe', 'Artarmon', 'Ashfield', 'Asquith', 'Auburn', 'Banksia', 'Bankstown', 'Bardwell Park', 'Beecroft', 'Berala', 'Berowra', 'Bella Vista', 'Beverly Hills', 'Bexley North', 'Birrong', 'Blacktown', 'Bondi Junction', 'Barangaroo', 'Burwood', 'Cabramatta', 'Campbelltown', 'Canley Vale', 'Caringbah', 'Carlton', 'Carramar', 'Casula', 'Castle Hill', 'Central', 'Chatswood', 'Cheltenham', 'Chester Hill', 'Cherrybrook', 'Circular Quay', 'Clarendon', 'Clyde', 'Como', 'Concord West', 'Cronulla', 'Croydon', 'Crows Nest', 'Denistone', 'Domestic Airport', 'Doonside', 'East Hills', 'East Richmond', 'Eastwood', 'Edgecliff', 'Edmondson Park', 'Emu Plains', 'Engadine', 'Epping', 'Erskineville', 'Fairfield', 'Flemington', 'Gadigal', 'Glenfield', 'Gordon', 'Granville', 'Green Square', 'Guildford', 'Gymea', 'Harris Park', 'Heathcote', 'Hills Showground', 'Holsworthy', 'Homebush', 'Hornsby', 'Hurstville', 'Ingleburn', 'International Airport', 'Jannali', 'Kellyville', 'Killara', 'Kings Cross', 'Kingsgrove', 'Kingswood', 'Kirrawee', 'Kogarah', 'Leightonfield', 'Leppington', 'Leumeah', 'Lewisham', 'Lidcombe', 'Lindfield', 'Liverpool', 'Loftus', 'Macarthur', 'Macdonaldtown', 'Macquarie Park', 'Macquarie Fields', 'Macquarie University', 'Marayong', 'Martin Place', 'Mascot', 'Meadowbank', 'Merrylands', 'Milsons Point', 'Minto', 'Miranda', 'Mortdale', 'Mount Colah', 'Mount Druitt', 'Mount Kuring-gai', 'Mulgrave', 'Museum', 'Narwee', 'Newtown', 'Normanhurst', 'North Strathfield', 'North Ryde', 'North Sydney', 'Norwest', 'Oatley', 'Olympic Park', 'Padstow', 'Panania', 'Parramatta', 'Pendle Hill', 'Pennant Hills', 'Penrith', 'Penshurst', 'Petersham', 'Pymble', 'Quakers Hill', 'Redfern', 'Regents Park', 'Revesby', 'Rhodes', 'Richmond', 'Riverstone', 'Riverwood', 'Rockdale', 'Rooty Hill', 'Roseville', 'Rouse Hill', 'Schofields', 'Sefton', 'Seven Hills', 'St James', 'St Leonards', 'St Marys', 'St Peters', 'Stanmore', 'Strathfield', 'Summer Hill', 'Sutherland', 'Sydenham', 'Tallawong', 'Tempe', 'Thornleigh', 'Toongabbie', 'Town Hall', 'Turramurra', 'Turrella', 'Victoria Cross', 'Villawood', 'Vineyard', 'Wahroonga', 'Waitara', 'Warrawee', 'Warwick Farm', 'Waterfall', 'Waterloo', 'Waverton', 'Wentworthville', 'Werrington', 'West Ryde', 'Westmead', 'Windsor', 'Wolli Creek', 'Wollstonecraft', 'Woolooware', 'Wynyard', 'Yagoona', 'Yennora']

global trainLines
trainLines = ["M1", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9"]

def journeyTupleToList(journeysTuple):
    journeys = [list(row) for row in journeysTuple]
    currentID = journeys[0][0]
    currentTime = journeys[0][1]
    #Setting up data structures
    formattedJourneys = []
    individualJourney = []
    stationList = []
    lineList = []
    trainList = []
    #Iterating through the journeys tuple, which is ordered by trip ID and stop order, to convert it into a list of journeys, where each journey contains a list of stations, line segments and train sets for that journey. 
    #This structure is easier to work with in Jinja when displaying the journeys on the front end.
    for journey in journeys:
        if currentID != journey[0]: #If the trip ID changes, we know we are on a new journey, so we need to append the previous journey to the list and reset our data structures for the new journey.
            individualJourney.append(currentID)
            dateTimeObject = datetime.fromisoformat(currentTime)
            readableTime = dateTimeObject.strftime("%A, %B %d, %I:%M %p")
            individualJourney.append(readableTime)
            individualJourney.append(stationList)
            individualJourney.append(lineList)
            individualJourney.append(trainList)
            formattedJourneys.append(individualJourney)
            #Resetting data structures for the new journey
            individualJourney = []
            currentID = journey[0]
            currentTime = journey[1]
            stationList = []
            lineList = []
            trainList = []
            #Appending the first station, line segment and train set for the new journey
            stationList.append(journey[3])
            lineList.append(journey[4])
            trainList.append(journey[5])
        else:
            #If the trip ID is the same, we are on the same journey, so we just need to append the station, line segment and train set to the current journey's data structures.
            stationList.append(journey[3])
            lineList.append(journey[4])
            trainList.append(journey[5])

    #Appending the final journey after the loop, since the loop only appends when it detects a change in trip ID, so the final journey won't be appended within the loop.
    individualJourney.append(currentID)
    dateTimeObject = datetime.fromisoformat(currentTime)
    readableTime = dateTimeObject.strftime("%A, %B %d, %I:%M %p")
    
    #The final iteration is constructed here, appending the time, station list, line list and train list to the individual journey.
    individualJourney.append(readableTime)
    individualJourney.append(stationList)
    individualJourney.append(lineList)
    individualJourney.append(trainList)
    
    #Finally, appending the final journey to the list of formatted journeys.
    formattedJourneys.append(individualJourney)
    return formattedJourneys

#Integrating GITHUB to python anywhere deployment, so that when I push code to Github, it automatically updates the website without me having to manually log in and pull the changes, making development and iteration much smoother.
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

#If the user does not have an account, they first view this page to sign up, then post to this function to input their details into the system, then they can log in.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        #escaping for data sanitisation
        fName = escape(request.form['fName'])
        lName = escape(request.form['lName'])
        email = escape(request.form['email'])
        username = escape(request.form['username'])
        displayName = escape(request.form['displayName'])
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        #confirming they have filled in all fields - backend verification
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

        #Making sure there isn't another account with the same username
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

        #More backend data validation
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

        try:
            sendConfirmationEmail(email)
        except Exception:
            flash("Failed to send confirmation email. Please try again. This could be because you are a student on school wifi", "error")
            conn.close()
            return redirect(url_for('login'))

        
        
        cursor.execute('INSERT INTO users (fName, lName, email, username, displayName, password) VALUES (?, ?, ?, ?, ?, ?)',
                    (fName, lName, email, username, displayName, generate_password_hash(password)))
        cursor.execute('INSERT INTO action_log (action, table_name, id_in_table) VALUES (?, ?, ?)', ("register", "users", cursor.lastrowid))
        
        conn.commit()
        conn.close()

        flash("Registration successful! Please chech your emails to confirm.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

#The default page people see when they visit the website, to Login
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Rate limit: prevents brute-force credential attacks (AVAILABILITY / AUTHENTICATION)
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

        #storing the data in the session cookies for easy access
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

#This is the route to confirm your email, making sure you are a real human.
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
@login_required
def index():
    global trainSets, stationsList, trainImages    

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    
    #selecting all trips based on the user id
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
        return render_template('index.html', name=session['fName'], trains=trainSets, stations=stationsList, journeys=[], trainImages=trainImages, status=session['status'])
    
    #turn this into a function
    #This section of code converts the tuple returned from SQL to python lists to provide to Jinja in HTML
    formattedJourneys = journeyTupleToList(journeysTuple)
    
    
    #structure of formattedJourneys: [[ID, Date, [Station1, Station2, ... StationN,], [Line1, LineN, None], [Train1, TrainN, None]], [*Same thing but for ID 8*]] etc
    #formattedJourneys is a list of journeys, where each journey is a list containing the journey ID, the date of the journey, a list of stations in the journey, a list of line segments for each station (None for the last station), and a list of train sets for each station (None for the last station). 
    #The lists are all in order so the first station corresponds to the first line segment and train set etc. This structure allows for easy iteration in Jinja to display the journeys in a user-friendly way.

    return render_template('index.html', name=session['fName'], trains=trainSets, stations=stationsList, journeys=formattedJourneys, status=session['status'], trainImages=trainImages)

#To submit a journey, a post request is sent to this function.
@app.route('/submitJourney', methods=['POST'])
@login_required
def submitJourney():
    if 'userID' not in session:
        flash("Please log in to submit a journey.", "error")
        return redirect(url_for('login'))
    #Getting and sanitising inputs
    firstStop = escape(request.form['startLocation'])
    middleStops = [escape(stop) for stop in request.form.getlist('middle')]
    lastStop = escape(request.form['endLocation'])
    
    firstTrain = escape(request.form['startSetDropdown'])
    middleTrains = [escape(train) for train in request.form.getlist('middleSetDropdown')]

    lineSegment = [escape(line) for line in request.form.getlist('lineChoice')]
    
    #Input validation
    if not firstStop or not lastStop or not firstTrain:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for('index'))

    #Making sure that the station inputted is included in the list of stations, input validation
    if firstStop not in stationsList or lastStop not in stationsList or any(s not in stationsList for s in middleStops):
        flash("Please select valid stations.", "error")
        return redirect(url_for('index'))

    #More input validation
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
    #Validating that train set and line segment inputs are from the allowed whitelist, not arbitrary user strings
    if firstTrain not in trainSets or any(t not in trainSets for t in middleTrains):
        flash("Please select a valid train set.", "error")
        conn.close()
        return redirect(url_for('index'))

    if any(line not in trainLines for line in lineSegment):
        flash("Please select valid line segments.", "error")
        conn.close()
        return redirect(url_for('index'))

    try:
        #Starts by creating a new trip ID
        cursor.execute('INSERT INTO trips (user_id, created_at) VALUES (?, ?)', (session['userID'], datetime.now()))
        trip_id = cursor.lastrowid
        #only need to log the creation of the trip, not each individual station, since if the trip is created, we can assume the stations are added, and if there is an error, the trip won't be created and thus no false data will be logged.
        cursor.execute('INSERT INTO action_log (action, table_name, id_in_table) VALUES (?, ?, ?)', ("created new trip", "trips", trip_id))


        #For each segment, this for loop inserts the station into the trip_stations table.
        for i in range(len(allStops) - 1):
            currentStop = allStops[i]
            currentTrain = allTrains[i] if i < len(allTrains) else None

            #Getting station ID to reference in trip_stations
            cursor.execute("SELECT id FROM stations WHERE name = ?", (currentStop,))
            row = cursor.fetchone()
            station_id = row[0] if row else None

            #Finally, inserting the individual station into the trip_stops table
            cursor.execute("INSERT INTO trip_stops (trip_id, station_id, stop_order, line_segment, train_set) VALUES (?, ?, ?, ?, ?)",
                           (trip_id, station_id, i, lineSegment[i], currentTrain))

        #Uniquely for the last stop, since there won't be a connecting line nor train, so just need to insert it into the table as is, only once.
        cursor.execute("SELECT id FROM stations WHERE name = ?", (lastStop,))
        row = cursor.fetchone()
        station_id = row[0] if row else None
        cursor.execute("INSERT INTO trip_stops (trip_id, station_id, stop_order, line_segment, train_set) VALUES (?, ?, ?, ?, ?)",
                       (trip_id, station_id, len(allStops) - 1, None, None))

        conn.commit()
    except Exception:
        flash("Sorry, something went wrong when trying to save your trip. Please make sure your selections are correct, and stations connect on valid lines.", "error")
        return redirect(url_for('index'))
    finally:
        conn.close()

    return redirect(url_for('index'))

@app.route('/stats')
@login_required
def stats():
    
    global trainLines
    
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    
    
    allStats = {}
    #Users most popular Station
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
    
    #Users most popular train set
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

    #Users most popular line segment
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

    #Total stations visited by the user across all their trips
    cursor.execute('''SELECT COUNT(station_id)
                   FROM trip_stops AS ts
                   JOIN trips AS tr
                   ON tr.id = ts.trip_id
                   WHERE tr.user_id = ?''',
                   (session['userID'],))
    results = cursor.fetchone()
    allStats['totalStations'] = list(results) if results else []

    #Total line segments travelled by the user across all their trips
    cursor.execute('''SELECT line_segment, COUNT(line_segment) AS line_count
                   FROM trip_stops AS ts
                   JOIN trips AS tr
                   ON tr.id = ts.trip_id
                   WHERE tr.user_id = ?
                   GROUP BY ts.line_segment
                   ORDER BY line_count DESC''',
                   (session["userID"],))
    allStats['lineCounts'] = [list(row) for row in cursor.fetchall()]

    #Total train sets travelled by the user across all their trips
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
    
    conn.close()
    return render_template('statistics.html', name=session['fName'], allStats=allStats, status=session['status'])

@app.route("/stations")
@login_required
def stations():
    global trainLines
    
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
    
    #This section of code creates a data structure to easily display the stations the user has visited on each line, and which they haven't visited. 
    # It iterates through each line and station, checking if the station has been visited by the user, and appending it to the tracker dictionary with a visited status. 
    # This allows for easy display in Jinja to show which stations on each line the user has visited.
    tracker = {line: [] for line in trainLines}
    for line, stations in lineStations.items():
        if line in tracker:
            for station in stations:
                tracker[line].append({'name': station, 'visited': station in stationsVisited})
    conn.close()
    print(stationsVisited)
    return render_template("stations.html", name=session['fName'], tracker=tracker, trainLines=trainLines, status=session["status"])

#The following routes are for user management, allowing admins to view all users, toggle their admin status, and delete users. 
#These routes are protected by the @admin_required decorator, ensuring only users with admin privileges can access them. 
#Additionally, there are safeguards in place to protect the SuperAdmin account from being modified or deleted by other admins, enforcing a strict hierarchy of privileges (AUTHORISATION).
@app.route("/manageUsers", methods=["GET"])
@login_required
@admin_required
def manageUsers():
    """
    Displays the user management table, allowing admins to view all registered
    users and toggle their roles. SuperAdmin also has access to user deletion.
    Protected by checkAdmin() — unauthorised access redirects to /.
    """

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()

    # Fetch display fields only — password hashes are deliberately excluded
    cursor.execute("SELECT fname, lname, email, username, status FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT status, username FROM users WHERE id = ?", (session['userID'],))
    userStatus = cursor.fetchone()
    conn.close()

    return render_template(
        'manageUsers.html',
        name=session['fName'],
        users=users,
        status=userStatus[0] if userStatus else None,
        username=userStatus[1] if userStatus else None
    )

#This route allows admins to toggle a user's role between 'user' and 'admin'.
@app.route("/toggleAdmin", methods=["POST"])
@login_required
@admin_required
def toggleAdmin():
    """
    Toggles a user's role between 'user' and 'admin'.

    SECURITY:
      - Attempting to toggle SuperFinnee's account punishes the operator
        by revoking THEIR OWN admin privileges — a deliberate deterrent
        against misuse of the most privileged account (AUTHORISATION).
      - The current status is checked before toggling to ensure the action
        is idempotent — calling toggle twice returns to the original state.
    """

    username = escape(request.form.get("username"))
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()

    # Attempting to toggle the SuperAdmin triggers a privilege revocation of the operator
    if username == "SuperFinnee" and session["username"] != "SuperFinnee":
        flash("Let's not do that. Your admin privileges have been revoked.", "error")
        cursor.execute("UPDATE users SET status = 'user' WHERE id = ?", (session['userID'],))
        cursor.execute('INSERT INTO action_log (action, table_name, id_in_table) VALUES (?, ?, ?)', ("Somebody tried to revoke the admin privileges of the owner", "users", session['userID']))
        conn.commit()
        conn.close()
        return redirect('/')

    # Read current role, then flip it
    cursor.execute("SELECT status FROM users WHERE username = ?", (username,))
    userStatus = cursor.fetchone()
    if userStatus and userStatus[0] == 'admin':
        cursor.execute("UPDATE users SET status = 'user' WHERE username = ?", (username,))
        cursor.execute('INSERT INTO action_log (action, table_name, id_in_table) VALUES (?, ?, ?)', (f"revoked admin privileges from {username}", "users", session['userID']))
    else:
        cursor.execute("UPDATE users SET status = 'admin' WHERE username = ?", (username,))
        cursor.execute("INSERT INTO action_log (action, table_name, id_in_table) VALUES (?, ?, ?)", (f"granted admin privileges to {username}", "users", session['userID']))
    conn.commit()
    conn.close()
    return redirect('/manageUsers')

#This route allows the SuperAdmin to permanently delete a user account from the database. 
# It includes safeguards to prevent deletion of the SuperAdmin account and revokes admin privileges from any user attempting to delete the SuperAdmin, enforcing strict AUTHORISATION controls.
@app.route("/deleteUser", methods=["POST"])
@login_required
@admin_required
def deleteUser():
    """
    Permanently deletes a user account from the database.
    Restricted to the SuperAdmin account only — the most destructive action
    available, so it requires the highest privilege tier (AUTHORISATION).
    SuperFinnee's own account is protected from deletion.
    """
    

    username = escape(request.form.get("username"))

    if username == "SuperFinnee":
        flash("Let's not do this one again. It was embarrassing the first time.", "error")
        return redirect('/manageUsers')

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()

    # Only SuperFinnee can delete user accounts (highest privilege tier)
    if session["username"] != 'SuperFinnee':
        conn.close()
        flash("You do not have permission to perform this action.", "error")
        return redirect('/manageUsers')
    
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    cursor.execute("INSERT INTO action_log (action, table_name, id_in_table) VALUES (?, ?, ?)", (f"deleted user {username}", "users", session['userID']))
    conn.commit()
    conn.close()
    flash(f'User {username} has been deleted.', 'success')
    return redirect('/manageUsers')

#This route allows admins to download the action log as a CSV file, providing transparency and accountability for all actions recorded in the system. 
#The log includes details such as the action performed, the table affected, the ID of the record involved, and a timestamp, allowing admins to review historical actions and monitor for any suspicious activity.
@app.route("/downloadActionLog", methods=["GET", "POST"])
@login_required
@admin_required
def downloadActionLog():
    """
    Admins can download the action log as a CSV file.
    The log includes all actions recorded in the action_log table, allowing accountability.
    """

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM action_log")
    logs = cursor.fetchall()
    conn.close()

    # Converting logs to CSV format for readability in excel
    csv_data = "ID,Action,Table Name,ID in Table,Timestamp\n"
    csv_data += "\n".join([f"{log[0]},{log[1]},{log[2]},{log[3]},{log[4]}" for log in logs])

    # Generating CSV as a downloadable file
    return (
        csv_data,
        200,
        {
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=action_log.csv",
        },
    )

if __name__ == '__main__':
    app.run(debug=True)
