import json
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else "trains.db"

# ---------------------------------------------------------------------------
# Station data: (stop_id, name, lines, platforms)
# ---------------------------------------------------------------------------

STATIONS = [
# ---- A ------------------------------------------------------------------
("ALW", "Allawah",              ["T4"],                                 [1, 2, 3, 4]),
("ARN", "Arncliffe",            ["T4"],                                 [1, 2, 3, 4]),
("ATM", "Artarmon",             ["T1", "T9"],                           [1, 2]),
("ASH", "Ashfield",             ["T2", "T3"],                           [1, 2, 3, 4, 5]),
("ASQ", "Asquith",              ["T1"],                                 [1, 2]),
("AUB", "Auburn",               ["T1", "T2"],                           [1, 2, 3, 4]),
# ---- B ------------------------------------------------------------------
("BKS", "Banksia",              ["T4"],                                 [1, 2, 3, 4]),
("BNK", "Bankstown",            ["T6"],                                 [1, 2, 3, 4]),
("BPK", "Bardwell Park",        ["T8"],                                 [1, 2]),
("BCF", "Beecroft",             ["T9"],                                 [1, 2]),
("BEJ", "Berala",               ["T3", "T6"],                           [1, 2]),
("BEW", "Berowra",              ["T1"],                                 [1, 2, 3]),
("BLV", "Bella Vista",          ["M1"],                                 [1, 2]),   # Metro
("BVH", "Beverly Hills",        ["T8"],                                 [1, 2]),
("BXN", "Bexley North",         ["T8"],                                 [1, 2]),
("BIO", "Birrong",              ["T6"],                                 [1, 2]),
("BAK", "Blacktown",            ["T1", "T5"],                           [1, 2, 3, 4, 5, 6, 7]),
("BJN", "Bondi Junction",       ["T4"],                                 [1, 2]),
("BRG", "Barangaroo",           ["M1"],                                 [1, 2]),   # Metro
("BUW", "Burwood",              ["T2", "T3", "T9"],                     [1, 2, 3, 4, 5, 6]),
# ---- C ------------------------------------------------------------------
("CAB", "Cabramatta",           ["T2", "T3", "T5"],                     [1, 2]),
("CTN", "Campbelltown",         ["T8"],                                 [1, 2, 3, 4]),
("CVE", "Canley Vale",          ["T2", "T5"],                           [1, 2]),
("CIH", "Caringbah",            ["T4"],                                 [1, 2]),
("CLJ", "Carlton",              ["T4"],                                 [1, 2, 3, 4]),
("CRR", "Carramar",             ["T3"],                                 [1, 2]),
("CSL", "Casula",               ["T2", "T5"],                           [1, 2]),
("CSH", "Castle Hill",          ["M1"],                                 [1, 2]),   # Metro
# Central: Sydney Trains uses platforms 12–25; Metro platform 27 is a separate
# underground concourse opened Aug 2024 alongside City & Southwest extension.
("CEN", "Central",              ["T1", "T2", "T3", "T4", "T7", "T8", "T9", "M1"],
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]),
("CWD", "Chatswood",            ["T1", "T9", "M1"],                     [1, 2, 3, 4]),
("CHA", "Cheltenham",           ["T9"],                                 [1, 2, 3]),
("CHH", "Chester Hill",         ["T3"],                                 [1, 2]),
("CRB", "Cherrybrook",          ["M1"],                                 [1, 2]),   # Metro
("CQY", "Circular Quay",        ["T2", "T3", "T8"],                     [1, 2]),
("CRD", "Clarendon",            ["T1", "T5"],                           [1, 2]),
("CYE", "Clyde",                ["T1", "T2"],                           [1, 2, 3, 4, 5]),
("CMO", "Como",                 ["T4"],                                 [1, 2]),
("CDW", "Concord West",         ["T9"],                                 [1, 2, 3, 4]),
("CNL", "Cronulla",             ["T4"],                                 [1, 2]),
# Croydon: Platforms 1 & 2 are disused; active platforms are 3, 4, 5
("CYD", "Croydon",              ["T2", "T3"],                           [1, 2, 3, 4, 5]),
("CWN", "Crows Nest",           ["M1"],                                 [1, 2]),   # Metro
# ---- D ------------------------------------------------------------------
("DST", "Denistone",            ["T9"],                                 [1, 2, 3, 4]),
("DOM", "Domestic Airport",     ["T8"],                                 [1, 2]),
("DOD", "Doonside",             ["T1"],                                 [1, 2, 3, 4]),
# ---- E ------------------------------------------------------------------
("EHS", "East Hills",           ["T8"],                                 [1, 2, 3]),
("ERD", "East Richmond",        ["T1", "T5"],                           [1]),
("EWD", "Eastwood",             ["T9"],                                 [1, 2, 3, 4]),
("ECL", "Edgecliff",            ["T4"],                                 [1, 2]),
("EDP", "Edmondson Park",       ["T2", "T5"],                           [1, 2]),
("EPS", "Emu Plains",           ["T1"],                                 [1, 2]),
("EGD", "Engadine",             ["T4"],                                 [1, 2]),
# Epping: T9 at surface platforms; M1 uses the converted Epping–Chatswood platforms
("EPG", "Epping",               ["T9", "M1"],                           [1, 2, 3, 4]),
("EKV", "Erskineville",         ["T8"],                                 [1, 2, 3, 4]),
# ---- F ------------------------------------------------------------------
("FFL", "Fairfield",            ["T2", "T5"],                           [1, 2]),
("FMG", "Flemington",           ["T2", "T3"],                           [1, 2, 3, 4]),
# ---- G ------------------------------------------------------------------
("GDG", "Gadigal",              ["M1"],                                 [1, 2]),   # Metro (near Town Hall)
("GFD", "Glenfield",            ["T2", "T5", "T8"],                     [1, 2, 3, 4]),
("GDN", "Gordon",               ["T1", "T9"],                           [1, 2, 3]),
("GAV", "Granville",            ["T1", "T2"],                           [1, 2, 3, 4]),
("GQE", "Green Square",         ["T8"],                                 [1, 2]),
("GUD", "Guildford",            ["T2", "T5"],                           [1, 2]),
("GYM", "Gymea",                ["T4"],                                 [1, 2]),
# ---- H ------------------------------------------------------------------
("HPK", "Harris Park",          ["T1", "T2", "T5"],                     [1, 2, 3, 4]),
("HTC", "Heathcote",            ["T4"],                                 [1, 2]),
("HSG", "Hills Showground",     ["M1"],                                 [1, 2]),   # Metro
("HOL", "Holsworthy",           ["T8"],                                 [1, 2]),
("HSH", "Homebush",             ["T2", "T3"],                           [1, 2, 3, 4, 5, 6, 7]),
("HBY", "Hornsby",              ["T1", "T9"],                           [1, 2, 3, 4, 5]),
("HVL", "Hurstville",           ["T4"],                                 [1, 2, 3, 4]),
# ---- I ------------------------------------------------------------------
("IGB", "Ingleburn",            ["T8"],                                 [1, 2]),
("INT", "International Airport",["T8"],                                 [1, 2]),
# ---- J ------------------------------------------------------------------
("JNL", "Jannali",              ["T4"],                                 [1, 2]),
# ---- K ------------------------------------------------------------------
("KVL", "Kellyville",           ["M1"],                                 [1, 2]),   # Metro
("KLA", "Killara",              ["T1", "T9"],                           [1, 2]),
("KSX", "Kings Cross",          ["T4"],                                 [1, 2]),
("KGV", "Kingsgrove",           ["T8"],                                 [1, 2]),
("KWD", "Kingswood",            ["T1"],                                 [1, 2]),
("KEE", "Kirrawee",             ["T4"],                                 [1, 2]),
("KGH", "Kogarah",              ["T4"],                                 [1, 2, 3, 4]),
# ---- L ------------------------------------------------------------------
("LTN", "Leightonfield",        ["T3"],                                 [1, 2]),
("LEP", "Leppington",           ["T2", "T5"],                           [1, 2, 3, 4]),
("LUM", "Leumeah",              ["T8"],                                 [1, 2]),
("LWI", "Lewisham",             ["T2", "T3"],                           [1, 2]),
("LDC", "Lidcombe",             ["T1", "T2", "T3", "T6", "T7"],         [0, 1, 2, 3, 4, 5]),
("LDD", "Lindfield",            ["T1", "T9"],                           [1, 2, 3]),
("LPO", "Liverpool",            ["T2", "T3", "T5"],                     [1, 2, 3, 4]),
("LOF", "Loftus",               ["T4"],                                 [1, 2]),
# ---- M ------------------------------------------------------------------
("MCA", "Macarthur",            ["T8"],                                 [1, 2, 3]),
("MAC", "Macdonaldtown",        ["T2", "T3"],                           [1, 2]),
("MQP", "Macquarie Park",       ["M1"],                                 [1, 2]),   # Metro
("MQF", "Macquarie Fields",     ["T8"],                                 [1, 2]),
("MQU", "Macquarie University", ["M1"],                                 [1, 2]),   # Metro
("MYG", "Marayong",             ["T1", "T5"],                           [1, 2]),
("MPC", "Martin Place",         ["T4", "M1"],                           [1, 2, 3, 4]),
("MCO", "Mascot",               ["T8"],                                 [1, 2]),
("MEB", "Meadowbank",           ["T9"],                                 [1, 2]),
("MLN", "Merrylands",           ["T2", "T5"],                           [1, 2]),
("MPT", "Milsons Point",        ["T1", "T9"],                           [1, 2]),
("MIO", "Minto",                ["T8"],                                 [1, 2]),
("MIJ", "Miranda",              ["T4"],                                 [1, 2]),
("MDE", "Mortdale",             ["T4"],                                 [1, 2]),
("MOC", "Mount Colah",          ["T1"],                                 [1, 2]),
("MTT", "Mount Druitt",         ["T1"],                                 [1, 2, 3, 4]),
("MKI", "Mount Kuring-gai",     ["T1"],                                 [1, 2]),
("MUV", "Mulgrave",             ["T1", "T5"],                           [1, 2]),
("MSM", "Museum",               ["T2", "T3", "T8"],                     [1, 2]),
# ---- N ------------------------------------------------------------------
("NWE", "Narwee",               ["T8"],                                 [1, 2]),
("NTN", "Newtown",              ["T2", "T3"],                           [1, 2]),
("NOR", "Normanhurst",          ["T9"],                                 [1, 2, 3]),
("NST", "North Strathfield",    ["T9"],                                 [1, 2, 3]),
("NRY", "North Ryde",           ["M1"],                                 [1, 2]),   # Metro
("NSY", "North Sydney",         ["T1", "T9"],                           [1, 2, 3, 4]),
("NWT", "Norwest",              ["M1"],                                 [1, 2]),   # Metro
# ---- O ------------------------------------------------------------------
("OAL", "Oatley",               ["T4"],                                 [1, 2]),
("OLP", "Olympic Park",         ["T7"],                                 [1, 2, 3, 4]),
# ---- P ------------------------------------------------------------------
("PDW", "Padstow",              ["T8"],                                 [1, 2]),
("PAN", "Panania",              ["T8"],                                 [1, 2]),
("PAR", "Parramatta",           ["T1", "T2", "T5"],                     [1, 2, 3, 4]),
("PDH", "Pendle Hill",          ["T1", "T5"],                           [1, 2, 3, 4]),
("PNT", "Pennant Hills",        ["T9"],                                 [1, 2, 3]),
("PNR", "Penrith",              ["T1"],                                 [1, 2, 3]),
("PHS", "Penshurst",            ["T4"],                                 [1, 2]),
("PSM", "Petersham",            ["T2", "T3"],                           [1, 2]),
("PYB", "Pymble",               ["T1", "T9"],                                 [1, 2]),
# ---- Q ------------------------------------------------------------------
("QKH", "Quakers Hill",         ["T1", "T5"],                           [1, 2]),
# ---- R ------------------------------------------------------------------
("REF", "Redfern",              ["T1", "T2", "T3", "T4", "T8", "T9"],   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
("RGP", "Regents Park",         ["T3", "T6"],                           [1, 2]),
("RSY", "Revesby",              ["T8"],                                 [1, 2, 3, 4]),
("RDS", "Rhodes",               ["T9"],                                 [1, 2, 3]),
("RCD", "Richmond",             ["T1", "T5"],                           [1, 2]),
("RVS", "Riverstone",           ["T1", "T5"],                           [1, 2]),
("RVD", "Riverwood",            ["T8"],                                 [1, 2]),
("RKL", "Rockdale",             ["T4"],                                 [1, 2, 3, 4, 5]),
("RYH", "Rooty Hill",           ["T1"],                                 [1, 2, 3, 4]),
("RVL", "Roseville",            ["T1", "T9"],                           [1, 2]),
("RSH", "Rouse Hill",           ["M1"],                                 [1, 2]),   # Metro
# ---- S ------------------------------------------------------------------
("SFS", "Schofields",           ["T1", "T5"],                           [1, 2]),
("SFT", "Sefton",               ["T3"],                                 [1, 2]),
("SEV", "Seven Hills",          ["T1", "T5"],                           [1, 2, 3, 4]),
("STJ", "St James",             ["T2", "T3", "T8"],                     [1, 2]),
("SNL", "St Leonards",          ["T1", "T9"],                           [2, 3]),
("STM", "St Marys",             ["T1"],                                 [1, 2, 3, 4]),
("SAP", "St Peters",            ["T8"],                                 [1, 2, 3, 4]),
("SMN", "Stanmore",             ["T2", "T3"],                           [1, 2, 3]),
("STR", "Strathfield",          ["T1", "T2", "T3", "T7", "T9"],         [1, 2, 3, 4, 5, 6, 7, 8]),
("SMH", "Summer Hill",          ["T2", "T3"],                           [1, 2, 3]),
("SLD", "Sutherland",           ["T4"],                                 [1, 2, 3]),
("SDN", "Sydenham",             ["T4", "T8", "M1"],                     [1, 2, 3, 4, 5, 6]),
# ---- T ------------------------------------------------------------------
("TLW", "Tallawong",            ["M1"],                                 [2, 3]),   # Metro
("TME", "Tempe",                ["T4"],                                 [1, 2, 3, 4]),
("THO", "Thornleigh",           ["T9"],                                 [1, 2, 3]),
("TGB", "Toongabbie",           ["T1", "T5"],                           [1, 2, 3, 4]),
("THL", "Town Hall",            ["T1", "T2", "T3", "T4", "T8", "T9"],   [1, 2, 3, 4, 5, 6]),
("TMU", "Turramurra",           ["T1", "T9"],                                 [1, 2]),
("TLL", "Turrella",             ["T8"],                                 [1, 2]),
# ---- V ------------------------------------------------------------------
("VCX", "Victoria Cross",       ["M1"],                                 [1, 2]),   # Metro
("VWD", "Villawood",            ["T3"],                                 [1, 2]),
("VYR", "Vineyard",             ["T1", "T5"],                           [1]),
# ---- W ------------------------------------------------------------------
("WRO", "Wahroonga",            ["T1", "T9"],                                 [1, 2]),
("WTA", "Waitara",              ["T1", "T9"],                                 [1, 2]),
("WWE", "Warrawee",             ["T1", "T9"],                                 [1, 2]),
("WWF", "Warwick Farm",         ["T2", "T3", "T5"],                     [1, 2]),
("WFL", "Waterfall",            ["T4"],                                 [1, 2]),
("WLO", "Waterloo",             ["M1"],                                 [1, 2]),   # Metro
("WVT", "Waverton",             ["T1", "T9"],                           [1, 2]),
("WVL", "Wentworthville",       ["T1", "T5"],                           [1, 2, 3, 4]),
("WRT", "Werrington",           ["T1"],                                 [1, 2]),
("WRY", "West Ryde",            ["T9"],                                 [1, 2, 3]),
("WMD", "Westmead",             ["T1", "T5"],                           [1, 2, 3, 4]),
("WIN", "Windsor",              ["T1", "T5"],                           [1]),
("WCK", "Wolli Creek",          ["T4", "T8"],                           [1, 2, 3, 4]),
("WSC", "Wollstonecraft",       ["T1", "T9"],                           [1, 2]),
("WOE", "Woolooware",           ["T4"],                                 [1, 2]),
("WYN", "Wynyard",              ["T1", "T2", "T3", "T8", "T9"],         [3, 4, 5, 6]),
# ---- Y ------------------------------------------------------------------
("YOA", "Yagoona",              ["T6"],                                 [1, 2]),
("YNR", "Yennora",              ["T2", "T5"],                           [1, 2]),
]

stationsList = ['Allawah', 'Arncliffe', 'Artarmon', 'Ashfield', 'Asquith', 'Auburn', 'Banksia', 'Bankstown', 'Bardwell Park', 'Beecroft', 'Berala', 'Berowra', 'Bella Vista', 'Beverly Hills', 'Bexley North', 'Birrong', 'Blacktown', 'Bondi Junction', 'Barangaroo', 'Burwood', 'Cabramatta', 'Campbelltown', 'Canley Vale', 'Caringbah', 'Carlton', 'Carramar', 'Casula', 'Castle Hill', 'Central', 'Chatswood', 'Cheltenham', 'Chester Hill', 'Cherrybrook', 'Circular Quay', 'Clarendon', 'Clyde', 'Como', 'Concord West', 'Cronulla', 'Croydon', 'Crows Nest', 'Denistone', 'Domestic Airport', 'Doonside', 'East Hills', 'East Richmond', 'Eastwood', 'Edgecliff', 'Edmondson Park', 'Emu Plains', 'Engadine', 'Epping', 'Erskineville', 'Fairfield', 'Flemington', 'Gadigal', 'Glenfield', 'Gordon', 'Granville', 'Green Square', 'Guildford', 'Gymea', 'Harris Park', 'Heathcote', 'Hills Showground', 'Holsworthy', 'Homebush', 'Hornsby', 'Hurstville', 'Ingleburn', 'International Airport', 'Jannali', 'Kellyville', 'Killara', 'Kings Cross', 'Kingsgrove', 'Kingswood', 'Kirrawee', 'Kogarah', 'Leightonfield', 'Leppington', 'Leumeah', 'Lewisham', 'Lidcombe', 'Lindfield', 'Liverpool', 'Loftus', 'Macarthur', 'Macdonaldtown', 'Macquarie Park', 'Macquarie Fields', 'Macquarie University', 'Marayong', 'Martin Place', 'Mascot', 'Meadowbank', 'Merrylands', 'Milsons Point', 'Minto', 'Miranda', 'Mortdale', 'Mount Colah', 'Mount Druitt', 'Mount Kuring-gai', 'Mulgrave', 'Museum', 'Narwee', 'Newtown', 'Normanhurst', 'North Strathfield', 'North Ryde', 'North Sydney', 'Norwest', 'Oatley', 'Olympic Park', 'Padstow', 'Panania', 'Parramatta', 'Pendle Hill', 'Pennant Hills', 'Penrith', 'Penshurst', 'Petersham', 'Pymble', 'Quakers Hill', 'Redfern', 'Regents Park', 'Revesby', 'Rhodes', 'Richmond', 'Riverstone', 'Riverwood', 'Rockdale', 'Rooty Hill', 'Roseville', 'Rouse Hill', 'Schofields', 'Sefton', 'Seven Hills', 'St James', 'St Leonards', 'St Marys', 'St Peters', 'Stanmore', 'Strathfield', 'Summer Hill', 'Sutherland', 'Sydenham', 'Tallawong', 'Tempe', 'Thornleigh', 'Toongabbie', 'Town Hall', 'Turramurra', 'Turrella', 'Victoria Cross', 'Villawood', 'Vineyard', 'Wahroonga', 'Waitara', 'Warrawee', 'Warwick Farm', 'Waterfall', 'Waterloo', 'Waverton', 'Wentworthville', 'Werrington', 'West Ryde', 'Westmead', 'Windsor', 'Wolli Creek', 'Wollstonecraft', 'Woolooware', 'Wynyard', 'Yagoona', 'Yennora']
stationLines = {'Allawah': ['T4'], 'Arncliffe': ['T4'], 'Artarmon': ['T1', 'T9'], 'Ashfield': ['T2', 'T3'], 'Asquith': ['T1'], 'Auburn': ['T1', 'T2'], 'Banksia': ['T4'], 'Bankstown': ['T6'], 'Bardwell Park': ['T8'], 'Beecroft': ['T9'], 'Berala': ['T3', 'T6'], 'Berowra': ['T1'], 'Bella Vista': ['M1'], 'Beverly Hills': ['T8'], 'Bexley North': ['T8'], 'Birrong': ['T6'], 'Blacktown': ['T1', 'T5'], 'Bondi Junction': ['T4'], 'Barangaroo': ['M1'], 'Burwood': ['T2', 'T3', 'T9'], 'Cabramatta': ['T2', 'T3', 'T5'], 'Campbelltown': ['T8'], 'Canley Vale': ['T2', 'T5'], 'Caringbah': ['T4'], 'Carlton': ['T4'], 'Carramar': ['T3'], 'Casula': ['T2', 'T5'], 'Castle Hill': ['M1'], 'Central': ['T1', 'T2', 'T3', 'T4', 'T7', 'T8', 'T9', 'M1'], 'Chatswood': ['T1', 'T9', 'M1'], 'Cheltenham': ['T9'], 'Chester Hill': ['T3'], 'Cherrybrook': ['M1'], 'Circular Quay': ['T2', 'T3', 'T8'], 'Clarendon': ['T1', 'T5'], 'Clyde': ['T1', 'T2'], 'Como': ['T4'], 'Concord West': ['T9'], 'Cronulla': ['T4'], 'Croydon': ['T2', 'T3'], 'Crows Nest': ['M1'], 'Denistone': ['T9'], 'Domestic Airport': ['T8'], 'Doonside': ['T1'], 'East Hills': ['T8'], 'East Richmond': ['T1', 'T5'], 'Eastwood': ['T9'], 'Edgecliff': ['T4'], 'Edmondson Park': ['T2', 'T5'], 'Emu Plains': ['T1'], 'Engadine': ['T4'], 'Epping': ['T9', 'M1'], 'Erskineville': ['T8'], 'Fairfield': ['T2', 'T5'], 'Flemington': ['T2', 'T3'], 'Gadigal': ['M1'], 'Glenfield': ['T2', 'T5', 'T8'], 'Gordon': ['T1', 'T9'], 'Granville': ['T1', 'T2'], 'Green Square': ['T8'], 'Guildford': ['T2', 'T5'], 'Gymea': ['T4'], 'Harris Park': ['T1', 'T2', 'T5'], 'Heathcote': ['T4'], 'Hills Showground': ['M1'], 'Holsworthy': ['T8'], 'Homebush': ['T2', 'T3'], 'Hornsby': ['T1', 'T9'], 'Hurstville': ['T4'], 'Ingleburn': ['T8'], 'International Airport': ['T8'], 'Jannali': ['T4'], 'Kellyville': ['M1'], 'Killara': ['T1', 'T9'], 'Kings Cross': ['T4'], 'Kingsgrove': ['T8'], 'Kingswood': ['T1'], 'Kirrawee': ['T4'], 'Kogarah': ['T4'], 'Leightonfield': ['T3'], 'Leppington': ['T2', 'T5'], 'Leumeah': ['T8'], 'Lewisham': ['T2', 'T3'], 'Lidcombe': ['T1', 'T2', 'T3', 'T6', 'T7'], 'Lindfield': ['T1', 'T9'], 'Liverpool': ['T2', 'T3', 'T5'], 'Loftus': ['T4'], 'Macarthur': ['T8'], 'Macdonaldtown': ['T2', 'T3'], 'Macquarie Park': ['M1'], 'Macquarie Fields': ['T8'], 'Macquarie University': ['M1'], 'Marayong': ['T1', 'T5'], 'Martin Place': ['T4', 'M1'], 'Mascot': ['T8'], 'Meadowbank': ['T9'], 'Merrylands': ['T2', 'T5'], 'Milsons Point': ['T1', 'T9'], 'Minto': ['T8'], 'Miranda': ['T4'], 'Mortdale': ['T4'], 'Mount Colah': ['T1'], 'Mount Druitt': ['T1'], 'Mount Kuring-gai': ['T1'], 'Mulgrave': ['T1', 'T5'], 'Museum': ['T2', 'T3', 'T8'], 'Narwee': ['T8'], 'Newtown': ['T2', 'T3'], 'Normanhurst': ['T9'], 'North Strathfield': ['T9'], 'North Ryde': ['M1'], 'North Sydney': ['T1', 'T9'], 'Norwest': ['M1'], 'Oatley': ['T4'], 'Olympic Park': ['T7'], 'Padstow': ['T8'], 'Panania': ['T8'], 'Parramatta': ['T1', 'T2', 'T5'], 'Pendle Hill': ['T1', 'T5'], 'Pennant Hills': ['T9'], 'Penrith': ['T1'], 'Penshurst': ['T4'], 'Petersham': ['T2', 'T3'], 'Pymble': ['T1', 'T9'], 'Quakers Hill': ['T1', 'T5'], 'Redfern': ['T1', 'T2', 'T3', 'T4', 'T8', 'T9'], 'Regents Park': ['T3', 'T6'], 'Revesby': ['T8'], 'Rhodes': ['T9'], 'Richmond': ['T1', 'T5'], 'Riverstone': ['T1', 'T5'], 'Riverwood': ['T8'], 'Rockdale': ['T4'], 'Rooty Hill': ['T1'], 'Roseville': ['T1', 'T9'], 'Rouse Hill': ['M1'], 'Schofields': ['T1', 'T5'], 'Sefton': ['T3'], 'Seven Hills': ['T1', 'T5'], 'St James': ['T2', 'T3', 'T8'], 'St Leonards': ['T1', 'T9'], 'St Marys': ['T1'], 'St Peters': ['T8'], 'Stanmore': ['T2', 'T3'], 'Strathfield': ['T1', 'T2', 'T3', 'T7', 'T9'], 'Summer Hill': ['T2', 'T3'], 'Sutherland': ['T4'], 'Sydenham': ['T4', 'T8', 'M1'], 'Tallawong': ['M1'], 'Tempe': ['T4'], 'Thornleigh': ['T9'], 'Toongabbie': ['T1', 'T5'], 'Town Hall': ['T1', 'T2', 'T3', 'T4', 'T8', 'T9'], 'Turramurra': ['T1', 'T9'], 'Turrella': ['T8'], 'Victoria Cross': ['M1'], 'Villawood': ['T3'], 'Vineyard': ['T1', 'T5'], 'Wahroonga': ['T1', 'T9'], 'Waitara': ['T1', 'T9'], 'Warrawee': ['T1', 'T9'], 'Warwick Farm': ['T2', 'T3', 'T5'], 'Waterfall': ['T4'], 'Waterloo': ['M1'], 'Waverton': ['T1', 'T9'], 'Wentworthville': ['T1', 'T5'], 'Werrington': ['T1'], 'West Ryde': ['T9'], 'Westmead': ['T1', 'T5'], 'Windsor': ['T1', 'T5'], 'Wolli Creek': ['T4', 'T8'], 'Wollstonecraft': ['T1', 'T9'], 'Woolooware': ['T4'], 'Wynyard': ['T1', 'T2', 'T3', 'T8', 'T9'], 'Yagoona': ['T6'], 'Yennora': ['T2', 'T5']}

def calculateLineSegment(start, end):
    station1Lines = stationLines[start]
    station2Lines = stationLines[end]
    found = False
    segment_lines = []
    for line in station1Lines:
        if line in station2Lines:
            found = True
            segment_lines.append(line)
            
    if not found:
        print(f"Error: No shared line between {start} and {end}")
        return None
    return segment_lines

def addStations():
    conn = sqlite3.connect("TfNSW.db")
    cur = conn.cursor()


    existing = cur.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
    if existing > 0:
        print(f"stations table already has {existing} rows.")
        print("To re-seed with corrected data, run:")
        print(f"  sqlite3 {DB_PATH} 'DELETE FROM stations;'")
        print("Then re-run this script.")
        conn.close()
        return

    rows = [
        (stop_id, name, json.dumps(lines), json.dumps(platforms))
        for stop_id, name, lines, platforms in STATIONS
    ]

    cur.executemany(
        "INSERT INTO stations (stop_id, name, lines, platforms) VALUES (?, ?, ?, ?)",
        rows,
    )

    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
    conn.close()

    print(f"Done — inserted {count} stations into '{DB_PATH}'.")
    assert count == len(STATIONS), f"Mismatch: expected {len(STATIONS)}, got {count}"

