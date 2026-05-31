function togglePassword() {
  var x = document.getElementById("password");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

function toggleConfirmPassword() {
  var x = document.getElementById("confirmPassword");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}


const addStationButton = document.getElementById("add-btn")
addStationButton.addEventListener("click", () => {
  const container = document.getElementById("middleStops")
  const wrapper = document.createElement("div")
  wrapper.className = 'stop-row'

  const label = document.createElement("label")
  label.textContent = "Interchange Station: \u{1F50E}"
  wrapper.appendChild(label)

  const input = document.createElement("select")
  input.name = "middle"
  input.required = true
  const stations = ['Allawah', 'Arncliffe', 'Artarmon', 'Ashfield', 'Asquith', 'Auburn', 'Banksia', 'Bankstown', 'Bardwell Park', 'Beecroft', 'Berala', 'Berowra', 'Bella Vista', 'Beverly Hills', 'Bexley North', 'Birrong', 'Blacktown', 'Bondi Junction', 'Barangaroo', 'Burwood', 'Cabramatta', 'Campbelltown', 'Canley Vale', 'Caringbah', 'Carlton', 'Carramar', 'Casula', 'Castle Hill', 'Central', 'Chatswood', 'Cheltenham', 'Chester Hill', 'Cherrybrook', 'Circular Quay', 'Clarendon', 'Clyde', 'Como', 'Concord West', 'Cronulla', 'Croydon', 'Crows Nest', 'Denistone', 'Domestic Airport', 'Doonside', 'East Hills', 'East Richmond', 'Eastwood', 'Edgecliff', 'Edmondson Park', 'Emu Plains', 'Engadine', 'Epping', 'Erskineville', 'Fairfield', 'Flemington', 'Gadigal', 'Glenfield', 'Gordon', 'Granville', 'Green Square', 'Guildford', 'Gymea', 'Harris Park', 'Heathcote', 'Hills Showground', 'Holsworthy', 'Homebush', 'Hornsby', 'Hurstville', 'Ingleburn', 'International Airport', 'Jannali', 'Kellyville', 'Killara', 'Kings Cross', 'Kingsgrove', 'Kingswood', 'Kirrawee', 'Kogarah', 'Leightonfield', 'Leppington', 'Leumeah', 'Lewisham', 'Lidcombe', 'Lindfield', 'Liverpool', 'Loftus', 'Macarthur', 'Macdonaldtown', 'Macquarie Park', 'Macquarie Fields', 'Macquarie University', 'Marayong', 'Martin Place', 'Mascot', 'Meadowbank', 'Merrylands', 'Milsons Point', 'Minto', 'Miranda', 'Mortdale', 'Mount Colah', 'Mount Druitt', 'Mount Kuring-gai', 'Mulgrave', 'Museum', 'Narwee', 'Newtown', 'Normanhurst', 'North Strathfield', 'North Ryde', 'North Sydney', 'Norwest', 'Oatley', 'Olympic Park', 'Padstow', 'Panania', 'Parramatta', 'Pendle Hill', 'Pennant Hills', 'Penrith', 'Penshurst', 'Petersham', 'Pymble', 'Quakers Hill', 'Redfern', 'Regents Park', 'Revesby', 'Rhodes', 'Richmond', 'Riverstone', 'Riverwood', 'Rockdale', 'Rooty Hill', 'Roseville', 'Rouse Hill', 'Schofields', 'Sefton', 'Seven Hills', 'St James', 'St Leonards', 'St Marys', 'St Peters', 'Stanmore', 'Strathfield', 'Summer Hill', 'Sutherland', 'Sydenham', 'Tallawong', 'Tempe', 'Thornleigh', 'Toongabbie', 'Town Hall', 'Turramurra', 'Turrella', 'Victoria Cross', 'Villawood', 'Vineyard', 'Wahroonga', 'Waitara', 'Warrawee', 'Warwick Farm', 'Waterfall', 'Waterloo', 'Waverton', 'Wentworthville', 'Werrington', 'West Ryde', 'Westmead', 'Windsor', 'Wolli Creek', 'Wollstonecraft', 'Woolooware', 'Wynyard', 'Yagoona', 'Yennora']

  const blankOption = document.createElement("option")
  blankOption.value = ""
  input.appendChild(blankOption)

  for (const station of stations) {
    if (station === 'Select A Station') continue
    const option = document.createElement("option")
    option.value = station
    option.textContent = station
    input.appendChild(option)
  }

  const select = document.createElement("select")
  select.name = "middleSetDropdown"
  select.required = true
  const trainSets = ["Select A Train", "Waratah Series 2 | B Set", "Waratah Series 1 | A Set", "Millennium | M Set", "Alstom Metropolis", "Mariyung | D Set", "Tangara | T Set", "Oscar | H Set", "K Set"]
  for (const train of trainSets) {
    const option = document.createElement("option")
    option.value = train
    option.textContent = train
    select.appendChild(option)
  }

  const removeButton = document.createElement("button")
  removeButton.type = "button"
  removeButton.textContent = "X"
  removeButton.addEventListener("click", () => {
    wrapper.remove()
    // CHANGED: Recalculate after a stop is removed, since the journey has changed
    updateJourney()
  })

  wrapper.appendChild(input)
  wrapper.appendChild(removeButton)
  wrapper.appendChild(document.createElement("br"))
  wrapper.appendChild(document.createElement("br"))
  wrapper.appendChild(select)
  wrapper.appendChild(document.createElement("br"))
  wrapper.appendChild(document.createElement("br"))
  container.appendChild(wrapper)


  $(input).select2({ placeholder: 'Select a station', allowClear: false })


  $(input).on('change', updateJourney)
})


const stationLines = {'Allawah': ['T4'], 'Arncliffe': ['T4'], 'Artarmon': ['T1', 'T9'], 'Ashfield': ['T2', 'T3'], 'Asquith': ['T1'], 'Auburn': ['T1', 'T2'], 'Banksia': ['T4'], 'Bankstown': ['T6'], 'Bardwell Park': ['T8'], 'Beecroft': ['T9'], 'Berala': ['T3', 'T6'], 'Berowra': ['T1'], 'Bella Vista': ['M1'], 'Beverly Hills': ['T8'], 'Bexley North': ['T8'], 'Birrong': ['T6'], 'Blacktown': ['T1', 'T5'], 'Bondi Junction': ['T4'], 'Barangaroo': ['M1'], 'Burwood': ['T2', 'T3', 'T9'], 'Cabramatta': ['T2', 'T3', 'T5'], 'Campbelltown': ['T8'], 'Canley Vale': ['T2', 'T5'], 'Caringbah': ['T4'], 'Carlton': ['T4'], 'Carramar': ['T3'], 'Casula': ['T2', 'T5'], 'Castle Hill': ['M1'], 'Central': ['T1', 'T2', 'T3', 'T4', 'T7', 'T8', 'T9', 'M1'], 'Chatswood': ['T1', 'M1'], 'Cheltenham': ['T9'], 'Chester Hill': ['T3'], 'Cherrybrook': ['M1'], 'Circular Quay': ['T2', 'T3', 'T8'], 'Clarendon': ['T1', 'T5'], 'Clyde': ['T1', 'T2'], 'Como': ['T4'], 'Concord West': ['T9'], 'Cronulla': ['T4'], 'Croydon': ['T2', 'T3'], 'Crows Nest': ['M1'], 'Denistone': ['T9'], 'Domestic Airport': ['T8'], 'Doonside': ['T1'], 'East Hills': ['T8'], 'East Richmond': ['T1', 'T5'], 'Eastwood': ['T9'], 'Edgecliff': ['T4'], 'Edmondson Park': ['T2', 'T5'], 'Emu Plains': ['T1'], 'Engadine': ['T4'], 'Epping': ['T9', 'M1'], 'Erskineville': ['T8'], 'Fairfield': ['T2', 'T5'], 'Flemington': ['T2', 'T3'], 'Gadigal': ['M1'], 'Glenfield': ['T2', 'T5', 'T8'], 'Gordon': ['T1', 'T9'], 'Granville': ['T1', 'T2'], 'Green Square': ['T8'], 'Guildford': ['T2', 'T5'], 'Gymea': ['T4'], 'Harris Park': ['T1', 'T2', 'T5'], 'Heathcote': ['T4'], 'Hills Showground': ['M1'], 'Holsworthy': ['T8'], 'Homebush': ['T2', 'T3'], 'Hornsby': ['T1', 'T9'], 'Hurstville': ['T4'], 'Ingleburn': ['T8'], 'International Airport': ['T8'], 'Jannali': ['T4'], 'Kellyville': ['M1'], 'Killara': ['T1', 'T9'], 'Kings Cross': ['T4'], 'Kingsgrove': ['T8'], 'Kingswood': ['T1'], 'Kirrawee': ['T4'], 'Kogarah': ['T4'], 'Leightonfield': ['T3'], 'Leppington': ['T2', 'T5'], 'Leumeah': ['T8'], 'Lewisham': ['T2', 'T3'], 'Lidcombe': ['T1', 'T2', 'T3', 'T6', 'T7'], 'Lindfield': ['T1', 'T9'], 'Liverpool': ['T2', 'T3', 'T5'], 'Loftus': ['T4'], 'Macarthur': ['T8'], 'Macdonaldtown': ['T2', 'T3'], 'Macquarie Park': ['M1'], 'Macquarie Fields': ['T8'], 'Macquarie University': ['M1'], 'Marayong': ['T1', 'T5'], 'Martin Place': ['T4', 'M1'], 'Mascot': ['T8'], 'Meadowbank': ['T9'], 'Merrylands': ['T2', 'T5'], 'Milsons Point': ['T1', 'T9'], 'Minto': ['T8'], 'Miranda': ['T4'], 'Mortdale': ['T4'], 'Mount Colah': ['T1'], 'Mount Druitt': ['T1'], 'Mount Kuring-gai': ['T1'], 'Mulgrave': ['T1', 'T5'], 'Museum': ['T2', 'T3', 'T8'], 'Narwee': ['T8'], 'Newtown': ['T2', 'T3'], 'Normanhurst': ['T9'], 'North Strathfield': ['T9'], 'North Ryde': ['M1'], 'North Sydney': ['T1', 'T9'], 'Norwest': ['M1'], 'Oatley': ['T4'], 'Olympic Park': ['T7'], 'Padstow': ['T8'], 'Panania': ['T8'], 'Parramatta': ['T1', 'T2', 'T5'], 'Pendle Hill': ['T1', 'T5'], 'Pennant Hills': ['T9'], 'Penrith': ['T1'], 'Penshurst': ['T4'], 'Petersham': ['T2', 'T3'], 'Pymble': ['T1'], 'Quakers Hill': ['T1', 'T5'], 'Redfern': ['T1', 'T2', 'T3', 'T4', 'T8', 'T9'], 'Regents Park': ['T3', 'T6'], 'Revesby': ['T8'], 'Rhodes': ['T9'], 'Richmond': ['T1', 'T5'], 'Riverstone': ['T1', 'T5'], 'Riverwood': ['T8'], 'Rockdale': ['T4'], 'Rooty Hill': ['T1'], 'Roseville': ['T1', 'T9'], 'Rouse Hill': ['M1'], 'Schofields': ['T1', 'T5'], 'Sefton': ['T3'], 'Seven Hills': ['T1', 'T5'], 'St James': ['T2', 'T3', 'T8'], 'St Leonards': ['T1', 'T9'], 'St Marys': ['T1'], 'St Peters': ['T8'], 'Stanmore': ['T2', 'T3'], 'Strathfield': ['T1', 'T2', 'T3', 'T7', 'T9'], 'Summer Hill': ['T2', 'T3'], 'Sutherland': ['T4'], 'Sydenham': ['T4', 'T8', 'M1'], 'Tallawong': ['M1'], 'Tempe': ['T4'], 'Thornleigh': ['T9'], 'Toongabbie': ['T1', 'T5'], 'Town Hall': ['T1', 'T2', 'T3', 'T4', 'T8', 'T9'], 'Turramurra': ['T1'], 'Turrella': ['T8'], 'Victoria Cross': ['M1'], 'Villawood': ['T3'], 'Vineyard': ['T1', 'T5'], 'Wahroonga': ['T1'], 'Waitara': ['T1'], 'Warrawee': ['T1'], 'Warwick Farm': ['T2', 'T3', 'T5'], 'Waterfall': ['T4'], 'Waterloo': ['M1'], 'Waverton': ['T1', 'T9'], 'Wentworthville': ['T1', 'T5'], 'Werrington': ['T1'], 'West Ryde': ['T9'], 'Westmead': ['T1', 'T5'], 'Windsor': ['T1', 'T5'], 'Wolli Creek': ['T4', 'T8'], 'Wollstonecraft': ['T1', 'T9'], 'Woolooware': ['T4'], 'Wynyard': ['T1', 'T2', 'T3', 'T8', 'T9'], 'Yagoona': ['T6'], 'Yennora': ['T2', 'T5']}


function calculateLineSegment(start, end) {
  const startLines = stationLines[start]
  const endLines = stationLines[end]
  const journeyLines = []

  for (const line of startLines) {
    if (endLines.includes(line)) {
      journeyLines.push(line)
    }
  }
  return journeyLines
}



function updateJourney() {

  const start = document.getElementById("startLocation").value
  const end = document.getElementById("endLocation").value

  const middleSelects = document.querySelectorAll('#middleStops select[name="middle"]')
  const middleValues = Array.from(middleSelects).map(s => s.value)

  const allStations = [start, ...middleValues, end]

  const segments = []
  for (let i = 0; i < allStations.length - 1; i++) {
    const from = allStations[i]
    const to = allStations[i + 1]

    // CHANGED: Skip this pair if either station is empty,
    // instead of aborting the whole function
    if (from === "" || to === "") continue

    const lines = calculateLineSegment(from, to)
    segments.push({ from, to, lines })
  }

  // If nothing is calculable yet, clear results and wait
  if (segments.length === 0) {
    document.getElementById("journey-results").textContent = ""
    return
  }

  const resultsDiv = document.getElementById("journey-results")
  resultsDiv.innerHTML = segments.map(seg => {
    const lineList = seg.lines.length > 0
      ? seg.lines.join(", ")
      : "⚠️ No shared line"
    return `<p>${seg.from} → ${seg.to}: <strong>${lineList}</strong></p>`
  }).join("")
}
