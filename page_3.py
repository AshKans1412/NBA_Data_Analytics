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


def live_page():
    aws_access_key_id = st.secrets["AWS_Access_key"]
    aws_secret_access_key = st.secrets["Secre_AK"]
    # Initialize Boto3 S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    # Specify your bucket name and folder path
    bucket_name = 'ash-dcsc-project'
    folder_path = 'NBA_Live_Data/Current_Matches/'
    
    # List files in the specified S3 bucket directory
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    files = [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith('.json')]
    
    # Initialize Streamlit app
    st.title('Game Details')
    if st.button('Refresh'):
        st.experimental_rerun()
    # Process each JSON file

    for file_key in files:
        # Read file content
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        match_data = json.loads(obj['Body'].read().decode('utf-8'))
    
        with st.expander(f"Match ID: {match_data['gameId']} - {match_data['gameCode']}", expanded=False):
            game_status, color = get_game_status(match_data['gameTimeUTC'],match_data['gameEt'])
    
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
