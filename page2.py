import streamlit as st
import requests
import difflib
from PIL import Image
from io import BytesIO
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# Function to find the closest match using difflib
def find_closest_match(user_input, candidate_list):
    matches = difflib.get_close_matches(user_input, candidate_list)
    return matches[0] if matches else None


# Function to get team logo URL from GitHub
def get_team_logo_url(team_abbreviation):
    github_url = f"https://raw.githubusercontent.com/Kaushiknb11/Basketball_Analytics/main/Teams/{team_abbreviation}.png"
    return github_url



# Function to fetch data from the API
def fetch_data(api_url):
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        data = pd.read_json(data)
        df = pd.DataFrame(data) 
        return df
    else:
        df = pd.read_csv("./Sample_Data/NBA_2024_per_game.csv")
        #st.error(f"Error fetching data from the API. Status code: {response.status_code}")
        return df

# Function to preprocess data
def preprocess_data(df):
    # Convert 'MP' column to numeric, handling errors by coercing to NaN
    df['MP'] = pd.to_numeric(df['MP'], errors='coerce')

    # Filter rows where 'MP' is greater than 5
    df = df.loc[df['MP'] > 5]

    # Identify players who have been traded
    players = df.Player.value_counts()
    traded_players = players[players > 1].keys()

    # Filter out rows where a player is traded but not marked as 'TOT'
    df = df.loc[(~df.Player.isin(traded_players)) | (df.Player.isin(traded_players) & (df.Tm == 'TOT'))]

    return df


def generate_player_comparison_plots(df, player1, player2):

    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    # Process the stats DataFrame
    stats = df[['Player', 'PTS', 'AST', 'TRB', 'STL', 'BLK']].copy()
    stats['PTS'] = pd.qcut(stats['PTS'], q=5, labels=False) + 1
    stats['AST'] = pd.qcut(stats['AST'], q=5, labels=False) + 1
    stats['TRB'] = pd.qcut(stats['TRB'], q=5, labels=False) + 1
    stats['STL'] = pd.qcut(stats['STL'], q=5, labels=False) + 1
    stats['BLK'] = pd.qcut(stats['BLK'], q=5, labels=False, duplicates='drop') + 1
    stats.loc[stats.BLK > 1, 'BLK'] = stats.loc[stats.BLK > 1, 'BLK'] + 1
    stats = pd.melt(stats, id_vars=['Player'], value_vars=['PTS', 'AST', 'TRB', 'STL', 'BLK'])

    # Select players
    players = [player1, player2]
    stats_filtered = stats.loc[stats['Player'].isin(players)]

    # Generate a title with player names
    title = f"Player Stats"

        # Create a subplot for each player's stats
    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'polar'}, {'type': 'polar'}]])


    # Add player 1's data to the first subplot
    fig.add_trace(
        go.Scatterpolar(
            r=stats_filtered[stats_filtered['Player'] == player1]['value'],
            theta=stats_filtered[stats_filtered['Player'] == player1]['variable'],
            fill='toself',
            name=player1
        ), 
        row=1, col=1
    )

    # Add player 2's data to the second subplot
    fig.add_trace(
        go.Scatterpolar(
            r=stats_filtered[stats_filtered['Player'] == player2]['value'],
            theta=stats_filtered[stats_filtered['Player'] == player2]['variable'],
            fill='toself',
            name=player2
        ), 
        row=1, col=2
    )

    # Update layout for a clean look and display the figure
    #fig.update_layout(title_text="Player Comparison", showlegend=False)
    st.plotly_chart(fig)


    # Plot 1: Line Polar
    #fig1 = px.line_polar(stats_filtered, r='value', theta='variable', line_close=True, title=title)
    #fig1.update_layout(
    #    autosize=False,
    #    width=400,   # Adjust the width to fit your layout
    #    height=400   # Adjust the height as needed
    #)
    #st.plotly_chart(fig1)

    # Plot 2: Two Line Polars
    #fig2_1 = px.line_polar(stats_filtered[stats_filtered['Player'] == player1],
                           #r='value', theta='variable', line_close=True, color='Player',
                           #title=f"{player1}'s Stats")

    #fig2_2 = px.line_polar(stats_filtered[stats_filtered['Player'] == player2],
                           #r='value', theta='variable', line_close=True, color='Player',
                           #title=f"{player2}'s Stats")

    #grid_props = dict(showgrid=True, gridwidth=1, gridcolor='lightgray')

    #fig2_1.update_layout(polar=dict(radialaxis=dict(visible=True, **grid_props), angularaxis=dict(**grid_props)))
    #fig2_2.update_layout(polar=dict(radialaxis=dict(visible=True, **grid_props), angularaxis=dict(**grid_props)))

    #st.plotly_chart(fig2_1)
    #st.plotly_chart(fig2_2)

    # Plot 3: Subplots
    #fig3 = make_subplots(rows=1, cols=2, subplot_titles=[f"{player1}'s Stats", f"{player2}'s Stats"])

    #fig3.add_trace(go.Scatterpolar(
        #r=stats_filtered[stats_filtered['Player'] == player1]['value'],
        #theta=stats_filtered[stats_filtered['Player'] == player1]['variable'],
        #fill='toself',
        #name=player1
    #))

    #fig3.add_trace(go.Scatterpolar(
        #r=stats_filtered[stats_filtered['Player'] == player2]['value'],
        #theta=stats_filtered[stats_filtered['Player'] == player2]['variable'],
        #fill='toself',
        #name=player2
    #))

    #fig3.update_layout(title_text=title)
    #st.plotly_chart(fig3)

def page_2():
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
    
    # Streamlit app title
    st.title("Player Stats & Comparison")
    
    # Dropdown for selecting the feature
    feature = st.selectbox(
        "Select a Feature",
        ["Player Search and Stats", "Player Comparison"]
    )
    
    # Fetch and preprocess NBA data
    api_url = 'https://nba-api-ash-1-fc1674476d71.herokuapp.com/dataset'
    nba_data = fetch_data(api_url)
    preprocessed_data = preprocess_data(nba_data)
    
    # Function to display player information and generate comparison plots
    def display_player_info_and_compare(player_name, preprocessed_data, other_player_name=None):
        # Display player information
        display_player_info(player_name)
    
        # If the other player's name is also provided, generate comparison plots
        if other_player_name:
            generate_player_comparison_plots(preprocessed_data, player_name, other_player_name)
    
    # Function to display player information (same as before)
    def display_player_info(player_name):
        # API Call to fetch player data
        response = requests.get(f"https://nba-api-ash-1-fc1674476d71.herokuapp.com/players/{player_name}")
        response_image = requests.get(f"https://nba-api-ash-1-fc1674476d71.herokuapp.com/get_images/{player_name}")
    
        if response.status_code == 200:
            data = response.json()
            st.write(f"Player Name: {data.get('API_Names', 'N/A')}")
    
            # Display player image
            if response_image.status_code == 200:
                image_url = response_image.json()["image"]
                img = Image.open(BytesIO(requests.get(image_url).content))
                st.image(img)
            else:
                st.error("Failed to load player image.")
    
            # Display other player information
            st.text(f"Currently Plays for: {team_name_mapping.get(data.get('Tm', 'N/A'), 'N/A')}")
            team_abbreviation = data.get('Tm', None)
            full_team_name = team_name_mapping.get(team_abbreviation, "N/A")
            #st.text(f"Currently Plays for: {full_team_name}")
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
            # ... [Add other player details here] ...
    
        else:
            st.error("Failed to fetch player data.")
    
    # Fetch all player names from the API
    
    #api_player_names = requests.get("https://nba-api-ash-1-fc1674476d71.herokuapp.com/players").json()

    nba_data = pd.read_csv("./Sample_Data/NBA_2024_per_game.csv")
    players = nba_data['Player'].unique().tolist()
    api_player_names = jsonify(players)
    
    # Display based on the selected feature
    if feature == "Player Search and Stats":
        # Single player search and stats display
        player_input = st.text_input("Enter the player name:")
        if player_input:
            player_name = find_closest_match(player_input, api_player_names)
            if player_name:
                display_player_info(player_name.replace(" ", "%20"))
            else:
                st.warning("Player not found. Please try again.")
    elif feature == "Player Comparison":
        # Player comparison display
        col1, col2 = st.columns(2)
        with col1:
            player1_input = st.text_input("Enter the name of the first player:")
        with col2:
            player2_input = st.text_input("Enter the name of the second player:")
    
        if player1_input and player2_input:
            player1 = find_closest_match(player1_input, api_player_names)
            player2 = find_closest_match(player2_input, api_player_names)
    
            if player1 and player2:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(player1)
                    display_player_info(player1.replace(" ", "%20"))
    
                with col2:
                    st.subheader(player2)
                    display_player_info(player2.replace(" ", "%20"))
    
                #st.header("Player Comparison")
                generate_player_comparison_plots(preprocessed_data, player1, player2)
            else:
                st.warning("One or both players not found. Please try again.")
        



