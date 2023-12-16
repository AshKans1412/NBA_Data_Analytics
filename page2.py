import streamlit as st 
import requests
import difflib
from PIL import Image
from io import BytesIO
import plotly.express as px
import pandas as pd

# Function to find the closest match using difflib
def find_closest_match(user_input, candidate_list):
    matches = difflib.get_close_matches(user_input, candidate_list)
    return matches[0] if matches else None


# Function to get team logo URL from GitHub
def get_team_logo_url(team_abbreviation):
    github_url = f"https://raw.githubusercontent.com/Kaushiknb11/Basketball_Analytics/main/Teams/{team_abbreviation}.png"
    return github_url

team_name_mapping = {
    "ATL": "Atlanta Hawks",
    "BRK": "Brooklyn Nets",
    "BOS": "Boston Celtics",
    "CHO": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHO": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards"
}




st.title("Player Information")


api_player_names = requests.get("https://nba-api-ash-1-fc1674476d71.herokuapp.com/players").json()

# Get player name from the user
user_input = st.text_input("Enter the player name:")

if user_input:
    # Find the closest match in the API player names
    closest_match = find_closest_match(user_input, api_player_names)
    if closest_match:
        # Replace spaces with "%20" for URL encoding
        player_name_encoded = closest_match.replace(" ", "%20")
        # API endpoints
        api_url = f"https://nba-api-ash-1-fc1674476d71.herokuapp.com/players/{player_name_encoded}"
        api_url_2 = f"https://nba-api-ash-1-fc1674476d71.herokuapp.com/get_images/{player_name_encoded}"

        # Making the GET request
        response = requests.get(api_url)
        response_2 = requests.get(api_url_2)
    
        # Checking the status code
        if response.status_code == 200:
            data = response.json()

            # Display player data
            #st.subheader("Player Information")
            st.write(f"Player Name: {data.get('API_Names', 'N/A')}")

            # Display player image
            if response_2.status_code == 200:
                image_url = response_2.json()["image"]
                response_image = requests.get(image_url)
                img = Image.open(BytesIO(response_image.content))
                st.image(img)#, caption=data.get('API_Names', 'N/A'))
            else:
                st.error("Failed to load player image.")

            team_abbreviation = data.get('Tm', None)
            full_team_name = team_name_mapping.get(team_abbreviation, "N/A")
            st.text(f"Currently Plays for: {full_team_name}")
            if team_abbreviation:
                team_logo_url = get_team_logo_url(team_abbreviation)
                st.image(team_logo_url, width=100)



            
            st.text(f"Birthday: {data.get('birthday', 'N/A')}")
            st.text(f"Age: {data.get('Age', 'N/A')}")
            st.text(f"Country: {data.get('country', 'N/A')}")
            st.text(f"Draft Year: {data.get('draft_year', 'N/A')}")
            st.text(f"Height: {data.get('height', 'N/A')}")
            st.text(f"Weight: {data.get('weight', 'N/A')}")
            st.text(f"School: {data.get('school', 'N/A')}")
            st.text(f"Position: {data.get('Pos', 'N/A')}")
            st.text(f"Points per game: {data.get('PTS', 'N/A')}")
            st.text(f"Assists per game: {data.get('AST', 'N/A')}")
            st.text(f"Rebounds per game: {data.get('TRB', 'N/A')}")
            st.text(f"Blocks per game: {data.get('BLK', 'N/A')}")
            st.text(f"Defensive Rebounds per game: {data.get('DRB', 'N/A')}")
            st.text(f"Offensive Rebounds per game: {data.get('ORB', 'N/A')}")
            st.text(f"Total Rebounds per game: {data.get('TRB', 'N/A')}")
            st.text(f"Field Goal Percentage: {data.get('FG%', 'N/A')}")
            st.text(f"Two-Point Percentage: {data.get('2P%', 'N/A')}")
            st.text(f"Three-Point Percentage: {data.get('3P%', 'N/A')}")
            st.text(f"Free Throw Percentage: {data.get('FT%', 'N/A')}")
            st.text(f"Minutes per game: {data.get('MP', 'N/A')}")
            st.text(f"Steals per game: {data.get('STL', 'N/A')}")
            st.text(f"Turnovers per game: {data.get('TOV', 'N/A')}")
            
        else:
            st.error("Failed to fetch player data.")
    else:
        st.warning("No close match found. Please try again.")



    

