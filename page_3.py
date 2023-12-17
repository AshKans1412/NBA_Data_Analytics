import os
import requests
import difflib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from io import BytesIO
import streamlit as st
import boto3
import json
from datetime import datetime, timezone
import plotly.express as px
from PIL import Image
import matplotlib.pyplot as plt


# Function to calculate countdown or game status
def get_game_status(game_time_utc, game_end_time_et):
    current_time_utc = datetime.now(timezone.utc)
    game_time = datetime.fromisoformat(game_time_utc.replace("Z", "+00:00"))
    game_end_time = datetime.fromisoformat(game_end_time_et.replace("Z", "+00:00"))

    if game_time > current_time_utc:
        # Game has not started yet, calculate countdown
        time_diff = game_time - current_time_utc
        hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"Countdown to Start: {hours}h {minutes}m {seconds}s", "blue"
    elif game_end_time > current_time_utc:
        # Game has started but not ended, indicate ongoing game
        return "Game is ongoing", "red"
    else:
        # Game has ended
        return "Game has ended", "green"



def draw_radial_chart(leader_data, title):
    categories = ['Points', 'Rebounds', 'Assists']
    values = [leader_data['points'], leader_data['rebounds'], leader_data['assists']]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 5]  # Adjust the range based on your data
            )),
        showlegend=False,
        title=title,
        width=300,
        height=300
    )

    return fig

def get_player_image(Name):
# List of all players from the API
    api_player_names = requests.get("https://nba-api-ash-1-fc1674476d71.herokuapp.com/players").json()
    
    # Get player name from the user
    user_input = Name
    
    # Function to find the closest match using difflib
    def find_closest_match(user_input, candidate_list):
        matches = difflib.get_close_matches(user_input, candidate_list)
        if matches:
            return matches[0]
        else:
            return None
    
    # Find the closest match in the API player names
    closest_match = find_closest_match(user_input, api_player_names)
    # Replace spaces with "%20" for URL encoding
    player_name_encoded = closest_match.replace(" ", "%20") if closest_match else None
    
    # API endpoint
    api_url_2 = f"https://nba-api-ash-1-fc1674476d71.herokuapp.com/get_images/{player_name_encoded}"
    response_2 = requests.get(api_url_2)
    image_url = response_2.json()["image"]

    return image_url


def plot_image_from_url(image_url):

    response = requests.get(image_url)
    response.raise_for_status()  # Raise an error for bad status codes

    image = Image.open(BytesIO(response.content))

    # Plotting the image using Matplotlib
    fig, ax = plt.subplots(figsize=(3, 2))    
    ax.imshow(image)
    ax.axis('off')  # Hide the axis
    return fig

    
def get_period_scores(team_data):
    return [period['score'] for period in team_data['periods']]

def draw_line_chart(period_scores, team_name):
    # Create a line chart for the team's performance across periods
    periods = ['Period 1', 'Period 2', 'Period 3', 'Period 4']
    fig = px.line(x=periods, y=period_scores, markers=True, title=f'Performance Across Periods: {team_name}')
    fig.update_layout(xaxis_title="Period", yaxis_title="Score", width = 300, height = 300)
    return fig
    
def draw_pie_chart(wins, losses, team_name):
    # Create a pie chart for wins and losses using Plotly
    labels = ['Wins', 'Losses']
    values = [wins, losses]

    fig = px.pie(names=labels, values=values, title=f'Win/Loss Ratio for {team_name}')
    fig.update_layout(width = 200, height = 300)

    return fig


def read_files_from_s3(bucket_name, folder_path, aws_access_key_id, aws_secret_access_key):
    # Initialize Boto3 S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    # List files in the specified S3 bucket directory
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    files = [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith('.json')]
    return s3, files

def read_files_from_local(local_folder_path):
    # List files in the specified local directory
    files = [f for f in os.listdir(local_folder_path) if f.endswith('.json')]
    return None, files

def live_page(source='local'):
    if source == 'aws':
        aws_access_key_id = st.secrets["AWS_Access_key"]
        aws_secret_access_key = st.secrets["Secre_AK"]
        bucket_name = 'ash-dcsc-project'
        folder_path = 'NBA_Live_Data/Current_Matches/'
        s3, files = read_files_from_s3(bucket_name, folder_path, aws_access_key_id, aws_secret_access_key)
    elif source == 'local':
        local_folder_path = 'Sample_Data'
        s3, files = read_files_from_local(local_folder_path)
    else:
        st.error("Invalid source specified. Please choose 'aws' or 'local'.")
        return
    # Initialize Streamlit app
    st.title('Game Details')
    if st.button('Refresh'):
        st.experimental_rerun()

    for file_key in files:
        # Read file content
        if source == 'aws':
            obj = s3.get_object(Bucket=bucket_name, Key=file_key)
            match_data = json.loads(obj['Body'].read().decode('utf-8'))
        else:
            with open(os.path.join(local_folder_path, file_key), 'r') as file:
                match_data = json.load(file)
        
        game_status, color = get_game_status(match_data['gameTimeUTC'], match_data['gameEt'])
        home_team = match_data['homeTeam']
        away_team = match_data['awayTeam']

        # Modify expander title to include game status
        expander_title = f"{home_team['teamName']} vs {away_team['teamName']}"
        with st.expander(expander_title, expanded=False):    
            
            
            game_status, color = get_game_status(match_data['gameTimeUTC'], match_data['gameEt'])
    
            # Use markdown with custom styling for countdown or status message
            st.write(f"<p style='color: {color};'>{game_status}</p>", unsafe_allow_html=True)
    
            col1, col2 = st.columns([2,2])
    
            with col1:
                
                team_abbreviation = home_team["teamTricode"]
                github_url = f"https://raw.githubusercontent.com/Kaushiknb11/Basketball_Analytics/main/Teams/{team_abbreviation}.png"


                home_team_wins = home_team['wins']
                home_team_losses = home_team['losses']

                col1_1, col1_2 = st.columns(2)
                
                with col1_1:

                    
                    image_fig = plot_image_from_url(github_url)
                    st.pyplot(image_fig) 
                    st.plotly_chart(draw_pie_chart(home_team_wins, home_team_losses, home_team['teamName']))
                    Home_Leader = match_data["gameLeaders"]["homeLeaders"]["name"]
                    #st.write(Home_Leader)
                    
                    image_url = get_player_image(Home_Leader)
                    image_fig = plot_image_from_url(image_url)

                    # Display the plot in Streamlit
                    st.pyplot(image_fig)


                with col1_2:

                
                    st.header("Home Team")
                    st.write(f"Team Name: {match_data['homeTeam']['teamName']}")
                    st.write(f"Score: {match_data['homeTeam']['score']}")
                    
                    st.text("")
                    st.text("")
                    
                    # Draw line charts
                    home_team_scores = get_period_scores(home_team)
                    st.plotly_chart(draw_line_chart(home_team_scores, home_team['teamName']))
                    home_leader = match_data["gameLeaders"]["homeLeaders"]
                    home_chart = draw_radial_chart(home_leader, f"Home Leader: {home_leader['name']}")
                    st.plotly_chart(home_chart)




        
            with col2:
                team_abbreviation = away_team["teamTricode"]
                github_url = f"https://raw.githubusercontent.com/Kaushiknb11/Basketball_Analytics/main/Teams/{team_abbreviation}.png"
                away_team_wins = away_team['wins']
                away_team_losses = away_team['losses']
                col2_1, col2_2 = st.columns(2)
                
                with col2_1:
                    
                    image_fig = plot_image_from_url(github_url)
                    st.pyplot(image_fig) 
                    st.plotly_chart(draw_pie_chart(away_team_wins, away_team_losses, away_team['teamName']))
                    Away_Leader = match_data["gameLeaders"]["awayLeaders"]["name"]
                    #st.write(Away_Leader)
                    
                    image_url = get_player_image(Away_Leader)
                    image_fig = plot_image_from_url(image_url)

                    # Display the plot in Streamlit
                    st.pyplot(image_fig)

                with col2_2:
                    st.header("Away Team")
                    st.write(f"Team Name: {match_data['awayTeam']['teamName']}")
                    st.write(f"Score: {match_data['awayTeam']['score']}")
                    st.write()
                    # Draw line charts
                    away_team_scores = get_period_scores(away_team)
                    st.plotly_chart(draw_line_chart(away_team_scores, away_team['teamName']))
                    
                    away_leader = match_data["gameLeaders"]["awayLeaders"]

                    away_chart = draw_radial_chart(away_leader, f"Away Leader: {away_leader['name']}")
                    st.plotly_chart(away_chart)

    
                

    
            st.markdown("---")  # Separator line
