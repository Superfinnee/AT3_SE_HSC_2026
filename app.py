from flask import Flask, render_template, request, redirect, session, url_for, flash, current_app
import sqlite3
from dotenv import load_dotenv
load_dotenv()
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config
from extensions import mail, initDB, verifyConfirmationToken, sendConfirmationEmail
from trainStations import calculateLineSegment, addStations #If SQL Database is deleted, run this function to re-add stations from trainStations.py

app = Flask(__name__)
app.config.from_object(Config)
mail.init_app(app)

with app.app_context():
    initDB()
    addStations()
    
global trainSets
trainSets = ["Waratah Series 2 | B Set", "Waratah Series 1 | A Set", "Millennium | M Set", "Alstom Metropolis", "Mariyung | D Set", "Tangara | T Set", "Oscar | H Set", "K Set"]

global stationsList
stationsList = ['Allawah', 'Arncliffe', 'Artarmon', 'Ashfield', 'Asquith', 'Auburn', 'Banksia', 'Bankstown', 'Bardwell Park', 'Beecroft', 'Berala', 'Berowra', 'Bella Vista', 'Beverly Hills', 'Bexley North', 'Birrong', 'Blacktown', 'Bondi Junction', 'Barangaroo', 'Burwood', 'Cabramatta', 'Campbelltown', 'Canley Vale', 'Caringbah', 'Carlton', 'Carramar', 'Casula', 'Castle Hill', 'Central', 'Chatswood', 'Cheltenham', 'Chester Hill', 'Cherrybrook', 'Circular Quay', 'Clarendon', 'Clyde', 'Como', 'Concord West', 'Cronulla', 'Croydon', 'Crows Nest', 'Denistone', 'Domestic Airport', 'Doonside', 'East Hills', 'East Richmond', 'Eastwood', 'Edgecliff', 'Edmondson Park', 'Emu Plains', 'Engadine', 'Epping', 'Erskineville', 'Fairfield', 'Flemington', 'Gadigal', 'Glenfield', 'Gordon', 'Granville', 'Green Square', 'Guildford', 'Gymea', 'Harris Park', 'Heathcote', 'Hills Showground', 'Holsworthy', 'Homebush', 'Hornsby', 'Hurstville', 'Ingleburn', 'International Airport', 'Jannali', 'Kellyville', 'Killara', 'Kings Cross', 'Kingsgrove', 'Kingswood', 'Kirrawee', 'Kogarah', 'Leightonfield', 'Leppington', 'Leumeah', 'Lewisham', 'Lidcombe', 'Lindfield', 'Liverpool', 'Loftus', 'Macarthur', 'Macdonaldtown', 'Macquarie Park', 'Macquarie Fields', 'Macquarie University', 'Marayong', 'Martin Place', 'Mascot', 'Meadowbank', 'Merrylands', 'Milsons Point', 'Minto', 'Miranda', 'Mortdale', 'Mount Colah', 'Mount Druitt', 'Mount Kuring-gai', 'Mulgrave', 'Museum', 'Narwee', 'Newtown', 'Normanhurst', 'North Strathfield', 'North Ryde', 'North Sydney', 'Norwest', 'Oatley', 'Olympic Park', 'Padstow', 'Panania', 'Parramatta', 'Pendle Hill', 'Pennant Hills', 'Penrith', 'Penshurst', 'Petersham', 'Pymble', 'Quakers Hill', 'Redfern', 'Regents Park', 'Revesby', 'Rhodes', 'Richmond', 'Riverstone', 'Riverwood', 'Rockdale', 'Rooty Hill', 'Roseville', 'Rouse Hill', 'Schofields', 'Sefton', 'Seven Hills', 'St James', 'St Leonards', 'St Marys', 'St Peters', 'Stanmore', 'Strathfield', 'Summer Hill', 'Sutherland', 'Sydenham', 'Tallawong', 'Tempe', 'Thornleigh', 'Toongabbie', 'Town Hall', 'Turramurra', 'Turrella', 'Victoria Cross', 'Villawood', 'Vineyard', 'Wahroonga', 'Waitara', 'Warrawee', 'Warwick Farm', 'Waterfall', 'Waterloo', 'Waverton', 'Wentworthville', 'Werrington', 'West Ryde', 'Westmead', 'Windsor', 'Wolli Creek', 'Wollstonecraft', 'Woolooware', 'Wynyard', 'Yagoona', 'Yennora']

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
                ORDER BY trips.created_at DESC, trip_stops.stop_order ASC''')
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
    dateTimeObject = datetime.fromisoformat(journey[1])
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

    if firstStop not in stationsList or lastStop not in stationsList:
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
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
