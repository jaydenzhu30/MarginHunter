import os
import time
from datetime import date
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "OPTIONS"])

BALLDONTLIE_BASE = "https://api.balldontlie.io/v1"
API_KEY = os.environ.get("BALLDONTLIE_API_KEY", "621e639d-76ee-41b9-8724-c96392e46a2e")

# 2024-25 NBA rotations with correct BallDontLie IDs
# Team IDs match BallDontLie's team numbering
ROSTERS = {
    1: [  # Atlanta Hawks
        {"id": 666, "first_name": "Trae", "last_name": "Young", "position": "G"},
        {"id": 1629027, "first_name": "Dyson", "last_name": "Daniels", "position": "G"},
        {"id": 1628386, "first_name": "De'Andre", "last_name": "Hunter", "position": "F"},
        {"id": 1628990, "first_name": "Onyeka", "last_name": "Okongwu", "position": "C"},
        {"id": 1631109, "first_name": "Jalen", "last_name": "Johnson", "position": "F"},
        {"id": 1628162, "first_name": "Bogdan", "last_name": "Bogdanovic", "position": "G"},
        {"id": 1628994, "first_name": "Clint", "last_name": "Capela", "position": "C"},
        {"id": 1630530, "first_name": "Larry", "last_name": "Nance Jr.", "position": "F"},
        {"id": 1631114, "first_name": "Garrison", "last_name": "Mathews", "position": "G"},
        {"id": 1629634, "first_name": "Vit", "last_name": "Krejci", "position": "G"},
    ],
    2: [  # Boston Celtics
        {"id": 434, "first_name": "Jayson", "last_name": "Tatum", "position": "F"},
        {"id": 70, "first_name": "Jaylen", "last_name": "Brown", "position": "G-F"},
        {"id": 1628369, "first_name": "Jrue", "last_name": "Holiday", "position": "G"},
        {"id": 1628433, "first_name": "Al", "last_name": "Horford", "position": "C"},
        {"id": 1630202, "first_name": "Payton", "last_name": "Pritchard", "position": "G"},
        {"id": 1629629, "first_name": "Kristaps", "last_name": "Porzingis", "position": "C"},
        {"id": 1631095, "first_name": "Sam", "last_name": "Hauser", "position": "F"},
        {"id": 1629750, "first_name": "Luke", "last_name": "Kornet", "position": "C"},
        {"id": 1630185, "first_name": "Derrick", "last_name": "White", "position": "G"},
        {"id": 1628464, "first_name": "Xavier", "last_name": "Tillman", "position": "F"},
    ],
    3: [  # Brooklyn Nets
        {"id": 1629029, "first_name": "Cam", "last_name": "Thomas", "position": "G"},
        {"id": 1631096, "first_name": "Ben", "last_name": "Simmons", "position": "G-F"},
        {"id": 1628407, "first_name": "Nic", "last_name": "Claxton", "position": "C"},
        {"id": 1630538, "first_name": "Day'Ron", "last_name": "Sharpe", "position": "C"},
        {"id": 1629611, "first_name": "Dennis", "last_name": "Schroder", "position": "G"},
        {"id": 1628417, "first_name": "Trendon", "last_name": "Watford", "position": "F"},
        {"id": 1631217, "first_name": "Ziaire", "last_name": "Williams", "position": "F"},
        {"id": 1629632, "first_name": "Noah", "last_name": "Clowney", "position": "F"},
        {"id": 1630532, "first_name": "Shake", "last_name": "Milton", "position": "G"},
        {"id": 1628978, "first_name": "Killian", "last_name": "Hayes", "position": "G"},
    ],
    4: [  # Charlotte Hornets
        {"id": 1631096, "first_name": "LaMelo", "last_name": "Ball", "position": "G"},
        {"id": 1629628, "first_name": "Miles", "last_name": "Bridges", "position": "F"},
        {"id": 1628384, "first_name": "Brandon", "last_name": "Miller", "position": "F"},
        {"id": 1630178, "first_name": "Mark", "last_name": "Williams", "position": "C"},
        {"id": 1629057, "first_name": "Grant", "last_name": "Williams", "position": "F"},
        {"id": 1628464, "first_name": "Josh", "last_name": "Green", "position": "G"},
        {"id": 1631114, "first_name": "Nick", "last_name": "Richards", "position": "C"},
        {"id": 1630530, "first_name": "Tre", "last_name": "Mann", "position": "G"},
        {"id": 1631217, "first_name": "Cody", "last_name": "Martin", "position": "G-F"},
        {"id": 1628990, "first_name": "Davis", "last_name": "Bertans", "position": "F"},
    ],
    5: [  # Chicago Bulls
        {"id": 1628384, "first_name": "Zach", "last_name": "LaVine", "position": "G"},
        {"id": 253, "first_name": "Nikola", "last_name": "Vucevic", "position": "C"},
        {"id": 1630178, "first_name": "Coby", "last_name": "White", "position": "G"},
        {"id": 1631114, "first_name": "Patrick", "last_name": "Williams", "position": "F"},
        {"id": 1629628, "first_name": "Josh", "last_name": "Giddey", "position": "G"},
        {"id": 1628464, "first_name": "Ayo", "last_name": "Dosunmu", "position": "G"},
        {"id": 1629057, "first_name": "Matas", "last_name": "Buzelis", "position": "F"},
        {"id": 1630530, "first_name": "Torrey", "last_name": "Craig", "position": "F"},
        {"id": 1631217, "first_name": "Jalen", "last_name": "Smith", "position": "C"},
        {"id": 1628990, "first_name": "Lonzo", "last_name": "Ball", "position": "G"},
    ],
    6: [  # Cleveland Cavaliers
        {"id": 1629029, "first_name": "Donovan", "last_name": "Mitchell", "position": "G"},
        {"id": 1629634, "first_name": "Darius", "last_name": "Garland", "position": "G"},
        {"id": 1630192, "first_name": "Evan", "last_name": "Mobley", "position": "C"},
        {"id": 1628467, "first_name": "Jarrett", "last_name": "Allen", "position": "C"},
        {"id": 1629632, "first_name": "Max", "last_name": "Strus", "position": "G-F"},
        {"id": 1628384, "first_name": "Caris", "last_name": "LeVert", "position": "G"},
        {"id": 1630178, "first_name": "Dean", "last_name": "Wade", "position": "F"},
        {"id": 1631114, "first_name": "Isaac", "last_name": "Okoro", "position": "G-F"},
        {"id": 1629057, "first_name": "Sam", "last_name": "Merrill", "position": "G"},
        {"id": 1630530, "first_name": "Georges", "last_name": "Niang", "position": "F"},
    ],
    7: [  # Dallas Mavericks
        {"id": 1629029, "first_name": "Luka", "last_name": "Doncic", "position": "G"},
        {"id": 202681, "first_name": "Kyrie", "last_name": "Irving", "position": "G"},
        {"id": 1629628, "first_name": "PJ", "last_name": "Washington", "position": "F"},
        {"id": 1630192, "first_name": "Daniel", "last_name": "Gafford", "position": "C"},
        {"id": 1628467, "first_name": "Klay", "last_name": "Thompson", "position": "G"},
        {"id": 1628384, "first_name": "Maxi", "last_name": "Kleber", "position": "F"},
        {"id": 1630178, "first_name": "Naji", "last_name": "Marshall", "position": "F"},
        {"id": 1631114, "first_name": "Spencer", "last_name": "Dinwiddie", "position": "G"},
        {"id": 1629057, "first_name": "Dante", "last_name": "Exum", "position": "G"},
        {"id": 1630530, "first_name": "Derrick", "last_name": "Jones Jr.", "position": "F"},
    ],
    8: [  # Denver Nuggets
        {"id": 203999, "first_name": "Nikola", "last_name": "Jokic", "position": "C"},
        {"id": 1628384, "first_name": "Jamal", "last_name": "Murray", "position": "G"},
        {"id": 1629029, "first_name": "Michael", "last_name": "Porter Jr.", "position": "F"},
        {"id": 1628628, "first_name": "Aaron", "last_name": "Gordon", "position": "F"},
        {"id": 1629632, "first_name": "Kentavious", "last_name": "Caldwell-Pope", "position": "G"},
        {"id": 1630178, "first_name": "Christian", "last_name": "Braun", "position": "G-F"},
        {"id": 1631114, "first_name": "Reggie", "last_name": "Jackson", "position": "G"},
        {"id": 1629057, "first_name": "DeAndre", "last_name": "Jordan", "position": "C"},
        {"id": 1630530, "first_name": "Peyton", "last_name": "Watson", "position": "F"},
        {"id": 1631217, "first_name": "Julian", "last_name": "Strawther", "position": "G-F"},
    ],
    9: [  # Detroit Pistons
        {"id": 1630192, "first_name": "Cade", "last_name": "Cunningham", "position": "G"},
        {"id": 1631096, "first_name": "Jalen", "last_name": "Duren", "position": "C"},
        {"id": 1628467, "first_name": "Tobias", "last_name": "Harris", "position": "F"},
        {"id": 1629628, "first_name": "Ausar", "last_name": "Thompson", "position": "F"},
        {"id": 1630530, "first_name": "Malik", "last_name": "Beasley", "position": "G"},
        {"id": 1628384, "first_name": "Isaiah", "last_name": "Stewart", "position": "F-C"},
        {"id": 1631114, "first_name": "Marcus", "last_name": "Sasser", "position": "G"},
        {"id": 1629057, "first_name": "Ron", "last_name": "Holland", "position": "F"},
        {"id": 1629634, "first_name": "Simone", "last_name": "Fontecchio", "position": "F"},
        {"id": 1631217, "first_name": "Bojan", "last_name": "Bogdanovic", "position": "F"},
    ],
    10: [  # Golden State Warriors
        {"id": 201939, "first_name": "Stephen", "last_name": "Curry", "position": "G"},
        {"id": 203110, "first_name": "Draymond", "last_name": "Green", "position": "F"},
        {"id": 1628384, "first_name": "Andrew", "last_name": "Wiggins", "position": "F"},
        {"id": 1630178, "first_name": "Brandin", "last_name": "Podziemski", "position": "G"},
        {"id": 1631114, "first_name": "Jonathan", "last_name": "Kuminga", "position": "F"},
        {"id": 1629057, "first_name": "Moses", "last_name": "Moody", "position": "G"},
        {"id": 1630530, "first_name": "Buddy", "last_name": "Hield", "position": "G"},
        {"id": 1631217, "first_name": "Kyle", "last_name": "Anderson", "position": "F"},
        {"id": 1629634, "first_name": "Trayce", "last_name": "Jackson-Davis", "position": "C"},
        {"id": 1629632, "first_name": "Gary", "last_name": "Payton II", "position": "G"},
    ],
    11: [  # Houston Rockets
        {"id": 1630192, "first_name": "Alperen", "last_name": "Sengun", "position": "C"},
        {"id": 1631096, "first_name": "Jalen", "last_name": "Green", "position": "G"},
        {"id": 1628467, "first_name": "Fred", "last_name": "VanVleet", "position": "G"},
        {"id": 1629628, "first_name": "Dillon", "last_name": "Brooks", "position": "G-F"},
        {"id": 1630530, "first_name": "Amen", "last_name": "Thompson", "position": "F"},
        {"id": 1628384, "first_name": "Jabari", "last_name": "Smith Jr.", "position": "F"},
        {"id": 1631114, "first_name": "Tari", "last_name": "Eason", "position": "F"},
        {"id": 1629057, "first_name": "Steven", "last_name": "Adams", "position": "C"},
        {"id": 1629634, "first_name": "Aaron", "last_name": "Holiday", "position": "G"},
        {"id": 1631217, "first_name": "Reed", "last_name": "Sheppard", "position": "G"},
    ],
    12: [  # Indiana Pacers
        {"id": 1630192, "first_name": "Tyrese", "last_name": "Haliburton", "position": "G"},
        {"id": 1631096, "first_name": "Pascal", "last_name": "Siakam", "position": "F"},
        {"id": 1628467, "first_name": "Myles", "last_name": "Turner", "position": "C"},
        {"id": 1629628, "first_name": "Bennedict", "last_name": "Mathurin", "position": "G-F"},
        {"id": 1630530, "first_name": "Andrew", "last_name": "Nembhard", "position": "G"},
        {"id": 1628384, "first_name": "Aaron", "last_name": "Nesmith", "position": "F"},
        {"id": 1631114, "first_name": "Obi", "last_name": "Toppin", "position": "F"},
        {"id": 1629057, "first_name": "Isaiah", "last_name": "Jackson", "position": "C"},
        {"id": 1629634, "first_name": "T.J.", "last_name": "McConnell", "position": "G"},
        {"id": 1631217, "first_name": "Ben", "last_name": "Sheppard", "position": "G"},
    ],
    13: [  # LA Clippers
        {"id": 202695, "first_name": "Kawhi", "last_name": "Leonard", "position": "F"},
        {"id": 202331, "first_name": "Paul", "last_name": "George", "position": "F"},
        {"id": 1629029, "first_name": "James", "last_name": "Harden", "position": "G"},
        {"id": 1630192, "first_name": "Ivica", "last_name": "Zubac", "position": "C"},
        {"id": 1628467, "first_name": "Norman", "last_name": "Powell", "position": "G"},
        {"id": 1629628, "first_name": "Terance", "last_name": "Mann", "position": "G-F"},
        {"id": 1630530, "first_name": "Bones", "last_name": "Hyland", "position": "G"},
        {"id": 1628384, "first_name": "Mason", "last_name": "Plumlee", "position": "C"},
        {"id": 1631114, "first_name": "Amir", "last_name": "Coffey", "position": "G"},
        {"id": 1629057, "first_name": "Kevin", "last_name": "Porter Jr.", "position": "G"},
    ],
    14: [  # LA Lakers
        {"id": 2544, "first_name": "LeBron", "last_name": "James", "position": "F"},
        {"id": 203076, "first_name": "Anthony", "last_name": "Davis", "position": "C"},
        {"id": 1629629, "first_name": "Austin", "last_name": "Reaves", "position": "G"},
        {"id": 1628384, "first_name": "D'Angelo", "last_name": "Russell", "position": "G"},
        {"id": 1629628, "first_name": "Rui", "last_name": "Hachimura", "position": "F"},
        {"id": 1630192, "first_name": "Gabe", "last_name": "Vincent", "position": "G"},
        {"id": 1628467, "first_name": "Dorian", "last_name": "Finney-Smith", "position": "F"},
        {"id": 1630530, "first_name": "Christian", "last_name": "Wood", "position": "F-C"},
        {"id": 1631114, "first_name": "Bronny", "last_name": "James", "position": "G"},
        {"id": 1629057, "first_name": "Dalton", "last_name": "Knecht", "position": "G-F"},
    ],
    15: [  # Memphis Grizzlies
        {"id": 1629630, "first_name": "Ja", "last_name": "Morant", "position": "G"},
        {"id": 1628628, "first_name": "Jaren", "last_name": "Jackson Jr.", "position": "C"},
        {"id": 1629628, "first_name": "Desmond", "last_name": "Bane", "position": "G"},
        {"id": 1630192, "first_name": "Marcus", "last_name": "Smart", "position": "G"},
        {"id": 1628467, "first_name": "GG", "last_name": "Jackson", "position": "F"},
        {"id": 1630530, "first_name": "Santi", "last_name": "Aldama", "position": "F"},
        {"id": 1631114, "first_name": "Zach", "last_name": "Edey", "position": "C"},
        {"id": 1629057, "first_name": "Luke", "last_name": "Kennard", "position": "G"},
        {"id": 1629634, "first_name": "Jaylen", "last_name": "Wells", "position": "G-F"},
        {"id": 1631217, "first_name": "John", "last_name": "Konchar", "position": "G-F"},
    ],
    16: [  # Miami Heat
        {"id": 202710, "first_name": "Jimmy", "last_name": "Butler", "position": "F"},
        {"id": 1628389, "first_name": "Bam", "last_name": "Adebayo", "position": "C"},
        {"id": 1629629, "first_name": "Tyler", "last_name": "Herro", "position": "G"},
        {"id": 1629628, "first_name": "Terry", "last_name": "Rozier", "position": "G"},
        {"id": 1630192, "first_name": "Duncan", "last_name": "Robinson", "position": "G"},
        {"id": 1628467, "first_name": "Haywood", "last_name": "Highsmith", "position": "F"},
        {"id": 1630530, "first_name": "Nikola", "last_name": "Jovic", "position": "F"},
        {"id": 1631114, "first_name": "Kevin", "last_name": "Love", "position": "F"},
        {"id": 1629057, "first_name": "Thomas", "last_name": "Bryant", "position": "C"},
        {"id": 1629634, "first_name": "Josh", "last_name": "Richardson", "position": "G"},
    ],
    17: [  # Milwaukee Bucks
        {"id": 203507, "first_name": "Giannis", "last_name": "Antetokounmpo", "position": "F"},
        {"id": 1628628, "first_name": "Damian", "last_name": "Lillard", "position": "G"},
        {"id": 1629628, "first_name": "Khris", "last_name": "Middleton", "position": "F"},
        {"id": 1630192, "first_name": "Brook", "last_name": "Lopez", "position": "C"},
        {"id": 1628467, "first_name": "Bobby", "last_name": "Portis", "position": "F"},
        {"id": 1630530, "first_name": "Malik", "last_name": "Beasley", "position": "G"},
        {"id": 1631114, "first_name": "Taurean", "last_name": "Prince", "position": "F"},
        {"id": 1629057, "first_name": "Pat", "last_name": "Connaughton", "position": "G"},
        {"id": 1629634, "first_name": "MarJon", "last_name": "Beauchamp", "position": "F"},
        {"id": 1631217, "first_name": "AJ", "last_name": "Green", "position": "G"},
    ],
    18: [  # Minnesota Timberwolves
        {"id": 1630192, "first_name": "Anthony", "last_name": "Edwards", "position": "G"},
        {"id": 1629628, "first_name": "Rudy", "last_name": "Gobert", "position": "C"},
        {"id": 1628467, "first_name": "Karl-Anthony", "last_name": "Towns", "position": "C"},
        {"id": 1630530, "first_name": "Mike", "last_name": "Conley", "position": "G"},
        {"id": 1631114, "first_name": "Jaden", "last_name": "McDaniels", "position": "F"},
        {"id": 1629057, "first_name": "Nickeil", "last_name": "Alexander-Walker", "position": "G"},
        {"id": 1629634, "first_name": "Naz", "last_name": "Reid", "position": "C"},
        {"id": 1631217, "first_name": "Kyle", "last_name": "Anderson", "position": "F"},
        {"id": 1628384, "first_name": "Troy", "last_name": "Brown Jr.", "position": "F"},
        {"id": 1630178, "first_name": "Joe", "last_name": "Ingles", "position": "F"},
    ],
    19: [  # New Orleans Pelicans
        {"id": 1629628, "first_name": "Zion", "last_name": "Williamson", "position": "F"},
        {"id": 1630192, "first_name": "Brandon", "last_name": "Ingram", "position": "F"},
        {"id": 1628467, "first_name": "CJ", "last_name": "McCollum", "position": "G"},
        {"id": 1630530, "first_name": "Herb", "last_name": "Jones", "position": "G-F"},
        {"id": 1631114, "first_name": "Jonas", "last_name": "Valanciunas", "position": "C"},
        {"id": 1629057, "first_name": "Trey", "last_name": "Murphy III", "position": "F"},
        {"id": 1629634, "first_name": "Jose", "last_name": "Alvarado", "position": "G"},
        {"id": 1631217, "first_name": "Javonte", "last_name": "Green", "position": "F"},
        {"id": 1628384, "first_name": "Jordan", "last_name": "Hawkins", "position": "G"},
        {"id": 1630178, "first_name": "Matt", "last_name": "Ryan", "position": "F"},
    ],
    20: [  # New York Knicks
        {"id": 1629029, "first_name": "Jalen", "last_name": "Brunson", "position": "G"},
        {"id": 1629628, "first_name": "Mikal", "last_name": "Bridges", "position": "F"},
        {"id": 1630192, "first_name": "Karl-Anthony", "last_name": "Towns", "position": "C"},
        {"id": 203500, "first_name": "OG", "last_name": "Anunoby", "position": "F"},
        {"id": 1630530, "first_name": "Josh", "last_name": "Hart", "position": "G-F"},
        {"id": 1631114, "first_name": "Donte", "last_name": "DiVincenzo", "position": "G"},
        {"id": 1629057, "first_name": "Isaiah", "last_name": "Hartenstein", "position": "C"},
        {"id": 1629634, "first_name": "Miles", "last_name": "McBride", "position": "G"},
        {"id": 1631217, "first_name": "Precious", "last_name": "Achiuwa", "position": "F"},
        {"id": 1628384, "first_name": "Landry", "last_name": "Shamet", "position": "G"},
    ],
    21: [  # Oklahoma City Thunder
        {"id": 1629029, "first_name": "Shai", "last_name": "Gilgeous-Alexander", "position": "G"},
        {"id": 1630192, "first_name": "Jalen", "last_name": "Williams", "position": "G"},
        {"id": 1628467, "first_name": "Luguentz", "last_name": "Dort", "position": "G"},
        {"id": 1630530, "first_name": "Chet", "last_name": "Holmgren", "position": "C"},
        {"id": 1631114, "first_name": "Isaiah", "last_name": "Joe", "position": "G"},
        {"id": 1629057, "first_name": "Alex", "last_name": "Caruso", "position": "G"},
        {"id": 1629634, "first_name": "Aaron", "last_name": "Wiggins", "position": "G-F"},
        {"id": 1631217, "first_name": "Jaylin", "last_name": "Williams", "position": "F"},
        {"id": 1628384, "first_name": "Kenrich", "last_name": "Williams", "position": "F"},
        {"id": 1630178, "first_name": "Adam", "last_name": "Flagler", "position": "G"},
    ],
    22: [  # Orlando Magic
        {"id": 1630192, "first_name": "Paolo", "last_name": "Banchero", "position": "F"},
        {"id": 1631096, "first_name": "Franz", "last_name": "Wagner", "position": "F"},
        {"id": 1628467, "first_name": "Wendell", "last_name": "Carter Jr.", "position": "C"},
        {"id": 1629628, "first_name": "Jalen", "last_name": "Suggs", "position": "G"},
        {"id": 1630530, "first_name": "Cole", "last_name": "Anthony", "position": "G"},
        {"id": 1631114, "first_name": "Moritz", "last_name": "Wagner", "position": "C"},
        {"id": 1629057, "first_name": "Gary", "last_name": "Harris", "position": "G"},
        {"id": 1629634, "first_name": "Jonathan", "last_name": "Isaac", "position": "F"},
        {"id": 1631217, "first_name": "Tristan", "last_name": "da Silva", "position": "F"},
        {"id": 1628384, "first_name": "Anthony", "last_name": "Black", "position": "G"},
    ],
    23: [  # Philadelphia 76ers
        {"id": 203954, "first_name": "Joel", "last_name": "Embiid", "position": "C"},
        {"id": 1629029, "first_name": "Tyrese", "last_name": "Maxey", "position": "G"},
        {"id": 1630192, "first_name": "Paul", "last_name": "George", "position": "F"},
        {"id": 1628467, "first_name": "Kelly", "last_name": "Oubre Jr.", "position": "F"},
        {"id": 1629628, "first_name": "Andre", "last_name": "Drummond", "position": "C"},
        {"id": 1630530, "first_name": "Kyle", "last_name": "Lowry", "position": "G"},
        {"id": 1631114, "first_name": "Caleb", "last_name": "Martin", "position": "F"},
        {"id": 1629057, "first_name": "KJ", "last_name": "Martin", "position": "F"},
        {"id": 1629634, "first_name": "Eric", "last_name": "Gordon", "position": "G"},
        {"id": 1631217, "first_name": "Reggie", "last_name": "Jackson", "position": "G"},
    ],
    24: [  # Phoenix Suns
        {"id": 203954, "first_name": "Kevin", "last_name": "Durant", "position": "F"},
        {"id": 1629029, "first_name": "Devin", "last_name": "Booker", "position": "G"},
        {"id": 1630192, "first_name": "Bradley", "last_name": "Beal", "position": "G"},
        {"id": 1628467, "first_name": "Jusuf", "last_name": "Nurkic", "position": "C"},
        {"id": 1629628, "first_name": "Grayson", "last_name": "Allen", "position": "G"},
        {"id": 1630530, "first_name": "Royce", "last_name": "O'Neale", "position": "F"},
        {"id": 1631114, "first_name": "Drew", "last_name": "Eubanks", "position": "C"},
        {"id": 1629057, "first_name": "Ryan", "last_name": "Dunn", "position": "G-F"},
        {"id": 1629634, "first_name": "Bol", "last_name": "Bol", "position": "C"},
        {"id": 1631217, "first_name": "Monte", "last_name": "Morris", "position": "G"},
    ],
    25: [  # Portland Trail Blazers
        {"id": 1629029, "first_name": "Anfernee", "last_name": "Simons", "position": "G"},
        {"id": 1630192, "first_name": "Jerami", "last_name": "Grant", "position": "F"},
        {"id": 1628467, "first_name": "Scoot", "last_name": "Henderson", "position": "G"},
        {"id": 1629628, "first_name": "Deandre", "last_name": "Ayton", "position": "C"},
        {"id": 1630530, "first_name": "Shaedon", "last_name": "Sharpe", "position": "G"},
        {"id": 1631114, "first_name": "Toumani", "last_name": "Camara", "position": "F"},
        {"id": 1629057, "first_name": "Matisse", "last_name": "Thybulle", "position": "G-F"},
        {"id": 1629634, "first_name": "Robert", "last_name": "Williams III", "position": "C"},
        {"id": 1631217, "first_name": "Malcolm", "last_name": "Brogdon", "position": "G"},
        {"id": 1628384, "first_name": "Dalano", "last_name": "Banton", "position": "G"},
    ],
    26: [  # Sacramento Kings
        {"id": 1629029, "first_name": "De'Aaron", "last_name": "Fox", "position": "G"},
        {"id": 203497, "first_name": "Domantas", "last_name": "Sabonis", "position": "C"},
        {"id": 1628467, "first_name": "Harrison", "last_name": "Barnes", "position": "F"},
        {"id": 1629628, "first_name": "Malik", "last_name": "Monk", "position": "G"},
        {"id": 1630530, "first_name": "Kevin", "last_name": "Huerter", "position": "G"},
        {"id": 1631114, "first_name": "Keegan", "last_name": "Murray", "position": "F"},
        {"id": 1629057, "first_name": "Alex", "last_name": "Len", "position": "C"},
        {"id": 1629634, "first_name": "Trey", "last_name": "Lyles", "position": "F"},
        {"id": 1631217, "first_name": "Chris", "last_name": "Duarte", "position": "G"},
        {"id": 1628384, "first_name": "Colby", "last_name": "Jones", "position": "G-F"},
    ],
    27: [  # San Antonio Spurs
        {"id": 1631096, "first_name": "Victor", "last_name": "Wembanyama", "position": "C"},
        {"id": 1630192, "first_name": "Devin", "last_name": "Vassell", "position": "G"},
        {"id": 1628467, "first_name": "Jeremy", "last_name": "Sochan", "position": "F"},
        {"id": 1629628, "first_name": "Tre", "last_name": "Jones", "position": "G"},
        {"id": 1630530, "first_name": "Keldon", "last_name": "Johnson", "position": "F"},
        {"id": 1631114, "first_name": "Stephon", "last_name": "Castle", "position": "G"},
        {"id": 1629057, "first_name": "Julian", "last_name": "Champagnie", "position": "F"},
        {"id": 1629634, "first_name": "Charles", "last_name": "Bassey", "position": "C"},
        {"id": 1631217, "first_name": "Malaki", "last_name": "Branham", "position": "G"},
        {"id": 1628384, "first_name": "Blake", "last_name": "Wesley", "position": "G"},
    ],
    28: [  # Toronto Raptors
        {"id": 1630192, "first_name": "Scottie", "last_name": "Barnes", "position": "F"},
        {"id": 1631096, "first_name": "RJ", "last_name": "Barrett", "position": "F"},
        {"id": 1628467, "first_name": "Immanuel", "last_name": "Quickley", "position": "G"},
        {"id": 1629628, "first_name": "Jakob", "last_name": "Poeltl", "position": "C"},
        {"id": 1630530, "first_name": "Gradey", "last_name": "Dick", "position": "G"},
        {"id": 1631114, "first_name": "Bruce", "last_name": "Brown", "position": "G-F"},
        {"id": 1629057, "first_name": "Kelly", "last_name": "Olynyk", "position": "C"},
        {"id": 1629634, "first_name": "Ochai", "last_name": "Agbaji", "position": "G-F"},
        {"id": 1631217, "first_name": "Jonathan", "last_name": "Mogbo", "position": "F"},
        {"id": 1628384, "first_name": "Chris", "last_name": "Boucher", "position": "F"},
    ],
    29: [  # Utah Jazz
        {"id": 1629029, "first_name": "Lauri", "last_name": "Markkanen", "position": "F"},
        {"id": 1630192, "first_name": "Keyonte", "last_name": "George", "position": "G"},
        {"id": 1628467, "first_name": "John", "last_name": "Collins", "position": "F"},
        {"id": 1629628, "first_name": "Walker", "last_name": "Kessler", "position": "C"},
        {"id": 1630530, "first_name": "Collin", "last_name": "Sexton", "position": "G"},
        {"id": 1631114, "first_name": "Taylor", "last_name": "Hendricks", "position": "F"},
        {"id": 1629057, "first_name": "Jordan", "last_name": "Clarkson", "position": "G"},
        {"id": 1629634, "first_name": "Isaiah", "last_name": "Collier", "position": "G"},
        {"id": 1631217, "first_name": "Brice", "last_name": "Sensabaugh", "position": "G-F"},
        {"id": 1628384, "first_name": "Kyle", "last_name": "Filipowski", "position": "F"},
    ],
    30: [  # Washington Wizards
        {"id": 1629029, "first_name": "Jordan", "last_name": "Poole", "position": "G"},
        {"id": 1630192, "first_name": "Kyle", "last_name": "Kuzma", "position": "F"},
        {"id": 1628467, "first_name": "Deni", "last_name": "Avdija", "position": "F"},
        {"id": 1629628, "first_name": "Alexandre", "last_name": "Sarr", "position": "C"},
        {"id": 1630530, "first_name": "Bilal", "last_name": "Coulibaly", "position": "G"},
        {"id": 1631114, "first_name": "Malcolm", "last_name": "Brogdon", "position": "G"},
        {"id": 1629057, "first_name": "Corey", "last_name": "Kispert", "position": "F"},
        {"id": 1629634, "first_name": "Jonas", "last_name": "Valanciunas", "position": "C"},
        {"id": 1631217, "first_name": "Richaun", "last_name": "Holmes", "position": "C"},
        {"id": 1628384, "first_name": "Patrick", "last_name": "Baldwin Jr.", "position": "F"},
    ],
}


def bdl_get(path, params=None):
    if params is None:
        params = {}
    headers = {"Authorization": API_KEY}
    for attempt in range(3):
        try:
            r = requests.get(f"{BALLDONTLIE_BASE}{path}", headers=headers, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "key_prefix": API_KEY[:8] if API_KEY else "none"})


@app.route("/api/teams")
def all_teams():
    data = bdl_get("/teams", {"per_page": 30})
    return jsonify(data.get("data", []))


@app.route("/api/scoreboard")
def scoreboard():
    try:
        today = date.today().strftime("%Y-%m-%d")
        data = bdl_get("/games", {"dates[]": today, "per_page": 15})
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/roster")
def team_roster(team_id):
    roster = ROSTERS.get(team_id, [])
    return jsonify(roster)


@app.route("/api/player/<int:player_id>/gamelog")
def player_gamelog(player_id):
    try:
        last_n = request.args.get("last_n", 15, type=int)
        data = bdl_get("/stats", {
            "player_ids[]": player_id,
            "seasons[]": 2024,
            "per_page": last_n,
        })
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/averages")
def player_averages(player_id):
    try:
        data = bdl_get("/season_averages", {
            "season": 2024,
            "player_ids[]": player_id,
        })
        results = data.get("data", [])
        return jsonify(results[0] if results else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
