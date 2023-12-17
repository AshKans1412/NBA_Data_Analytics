import os
import streamlit as st
import boto3
import json
from datetime import datetime, timezone

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

        home_team = match_data['homeTeam']
        away_team = match_data['awayTeam']
        expander_title = f"{match_data['homeTeam']['teamName'].upper()} ({match_data['homeTeam']['teamCity'].lower()}) vs {match_data['awayTeam']['teamName'].upper()} ({match_data['awayTeam']['teamCity'].lower()}")
        with st.expander(expander_title, expanded=False):    
            
            
            game_status, color = get_game_status(match_data['gameTimeUTC'], match_data['gameEt'])
    
            # Use markdown with custom styling for countdown or status message
            st.write(f"<p style='color: {color};'>{game_status}</p>", unsafe_allow_html=True)
    
            col1, col2 = st.columns(2)
    
            with col1:
                st.header("Home Team")
                st.write(f"Team Name: {match_data['homeTeam']['teamName']}")
                st.write(f"Score: {match_data['homeTeam']['score']}")
    
            with col2:
                st.header("Away Team")
                st.write(f"Team Name: {match_data['awayTeam']['teamName']}")
                st.write(f"Score: {match_data['awayTeam']['score']}")
    
            st.markdown("---")  # Separator line
