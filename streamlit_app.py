import nba_api
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from io import BytesIO
from nba_api.stats.endpoints import shotchartdetail, playercareerstats
from nba_api.stats.static import players, teams
import plotly.express as px
from PIL import Image, UnidentifiedImageError
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from page_3 import live_page
from page2 import page_2

# Function to fetch data from the API
def fetch_data(api_url):
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        data = pd.read_json(data)
        df = pd.DataFrame(data) 
        return df
    else:
        st.error(f"Error fetching data from the API. Status code: {response.status_code}")
        return None

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


def plot_pts(df):
    # Create subplots with two columns
    fig = make_subplots(rows=1, cols=1, subplot_titles=['Top 10 Players by PTS'])

    # Bar plot for 'PTS'
    trace = go.Bar(x=df.sort_values('PTS', ascending=False).iloc[0:10]['Player'],
                   y=df.sort_values('PTS', ascending=False).iloc[0:10]['PTS'],
                   marker=dict(color='blue'))
    
    # Add trace to the subplot
    fig.add_trace(trace)

    # Update layout
    fig.update_layout(title_text='Top 10 Players by PTS', showlegend=False)

    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)

    # Show the plot
    st.plotly_chart(fig)

def plot_ast(df):
    # Create subplots with two columns
    fig = make_subplots(rows=1, cols=1, subplot_titles=['Top 10 Players by AST'])

    # Bar plot for 'AST'
    trace = go.Bar(x=df.sort_values('AST', ascending=False).iloc[0:10]['Player'],
                   y=df.sort_values('AST', ascending=False).iloc[0:10]['AST'],
                   marker=dict(color='green'))

    # Add trace to the subplot
    fig.add_trace(trace)

    # Update layout
    fig.update_layout(title_text='Top 10 Players by AST', showlegend=False)

    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)

    # Show the plot
    st.plotly_chart(fig)

def scatter_plot(df):
    import plotly.express as px
    # Define a color scale mapping for positions
    pos_color_mapping = {
        'C': 'red',
        'SG': 'blue',
        'PF': 'green',
        'SF': 'orange',
        'PG': 'magenta'    
    }

    # Map the 'Pos' column to colors
    df['Color'] = df['Pos'].map(pos_color_mapping)

    # Add a new column for marker size with a constant value (e.g., 5)
    df['Marker_Size'] = 5

    # Filter out players with multiple positions
    df_filtered = df[~df['Pos'].str.contains('-')]

    # Filter the top 15 players for each position
    top_players = df_filtered.groupby('Pos').apply(lambda x: x.nlargest(25, 'PTS')).reset_index(drop=True)

    # Create a scatter plot using Plotly Express
    fig = px.scatter(top_players, x='AST', y='PTS', hover_name="Player", color='Pos', size='Marker_Size', opacity=0.7,
                     title='Scatter Plot of AST vs PTS (Top 25 Players per Position)',
                     labels={'AST': 'Assists', 'PTS': 'Points'},
                     color_discrete_map=pos_color_mapping)

    # Update the legend title
    fig.update_layout(legend_title_text='Position')

    # Adjust the maximum marker size
    fig.update_traces(marker=dict(size=10, sizemode='diameter', sizeref=0.1))

    # Show the interactive plot
    st.plotly_chart(fig)



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
    title = f"Comparing player stats: {player1} and {player2}"

    # Plot 1: Line Polar
    fig1 = px.line_polar(stats_filtered, r='value', theta='variable', line_close=True, color='Player', title=title)
    st.plotly_chart(fig1)

    # Plot 2: Two Line Polars
    fig2_1 = px.line_polar(stats_filtered[stats_filtered['Player'] == player1],
                           r='value', theta='variable', line_close=True, color='Player',
                           title=f"{player1}'s Stats")

    fig2_2 = px.line_polar(stats_filtered[stats_filtered['Player'] == player2],
                           r='value', theta='variable', line_close=True, color='Player',
                           title=f"{player2}'s Stats")

    grid_props = dict(showgrid=True, gridwidth=1, gridcolor='lightgray')

    fig2_1.update_layout(polar=dict(radialaxis=dict(visible=True, **grid_props), angularaxis=dict(**grid_props)))
    fig2_2.update_layout(polar=dict(radialaxis=dict(visible=True, **grid_props), angularaxis=dict(**grid_props)))

    st.plotly_chart(fig2_1)
    st.plotly_chart(fig2_2)

    # Plot 3: Subplots
    fig3 = make_subplots(rows=1, cols=2, subplot_titles=[f"{player1}'s Stats", f"{player2}'s Stats"])

    fig3.add_trace(go.Scatterpolar(
        r=stats_filtered[stats_filtered['Player'] == player1]['value'],
        theta=stats_filtered[stats_filtered['Player'] == player1]['variable'],
        fill='toself',
        name=player1
    ))

    fig3.add_trace(go.Scatterpolar(
        r=stats_filtered[stats_filtered['Player'] == player2]['value'],
        theta=stats_filtered[stats_filtered['Player'] == player2]['variable'],
        fill='toself',
        name=player2
    ))

    fig3.update_layout(title_text=title)
    st.plotly_chart(fig3)


def generate_top_performers_plots(df, category):
    # Mapping categories to columns
    category_mapping = {
        'Points': 'PTS',
        'Assists': 'AST',
        'Rebounds': 'TRB',
        'Steals': 'STL',
        'Blocks': 'BLK',
        'FG Percentage': 'FG%',
        '3P Percentage': '3P%',
        'FT Percentage': 'FT%'
    }

    # Check if the selected category is valid
    if category not in category_mapping:
        st.error("Invalid category selected.")
        return

    # Identify top performers in the selected category
    column_name = category_mapping[category]
    top_performers = df[['Player', column_name]].sort_values(by=column_name, ascending=False).head(10)

    sns.set_style("white")
    fig, ax = plt.subplots(figsize=(10, 4))  # Create a figure and a set of subplots

    # Plotting the top performers
    sns.barplot(x=column_name, y='Player', data=top_performers, palette='viridis', ax=ax)
    
    # Centering the title and setting font size
    ax.set_title(f'Top Performers in {category}', loc='center', fontsize=16)

    # Setting x and y labels with specified font sizes
    ax.set_xlabel(category, fontsize=14)
    ax.set_ylabel('Player', fontsize=14)

    # Annotate each bar with the value
    for p in ax.patches:
        ax.annotate(format(p.get_width(), '.1f'),  # Format the number to 1 decimal place
                    (p.get_width(), p.get_y() + p.get_height() / 2),  # Position
                    xytext=(5, 0),  # 5 points horizontal offset
                    textcoords='offset points',  # Offset from the xy value
                    ha='left', va='center')  # Horizontal alignment and vertical alignment

    plt.tight_layout()
    return fig 


# NbaScraper Class
class NbaScraper:
    """ Class to scrape data from the NBA official website.
    """

    @staticmethod
    def requests_session():
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    @staticmethod
    def get_json_from_name(name: str, is_player=True) -> int:
        """ Get the json of a player or team from his name
        """
        from nba_api.stats.static import players, teams
        if is_player:
            nba_players = players.get_players()
            return [player for player in nba_players 
                    if player['full_name'] == name][0]
        else:
            nba_teams = teams.get_teams()
            return [team for team in nba_teams 
                    if team['full_name'] == name][0]
    
    @staticmethod
    def get_player_career(player_id: int) -> list:
        """ Get the career of a player from his id. """
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        return career.get_data_frames()[0]

    @staticmethod
    def get_shot_data(id: int, team_ids: list, seasons: list) -> list:
        """ Get the shot data of a player from his id and seasons. """
        session = NbaScraper.requests_session()
        df = pd.DataFrame()
        for season in seasons:
            for team in team_ids:
                shot_data = shotchartdetail.ShotChartDetail(
                    team_id=team, player_id=id,
                    context_measure_simple='FGA',
                    season_nullable=season,
                    timeout=10 
                )
                df = pd.concat([df, shot_data.get_data_frames()[0]])
        return df
    
    @staticmethod
    def get_all_ids(only_active=True) -> list:
        """ Get all the ids of the players
        """
        from nba_api.stats.static import players
        nba_players = players.get_players()
        if only_active:
            return [player['id'] for player in nba_players 
                    if player['is_active']]
        return [player['id'] for player in nba_players]
    
    @staticmethod
    def get_player_headshot(id: int) -> str:
            """ Get the headshot of a player from his id
            """
            from nba_api.stats.static import players
            import shutil
            
            url = f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{id}.png'
            output_path = f'../data/nba/transient/headshots/{id}.png'
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(output_path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
    
    @staticmethod                                    
    def get_all_nba_headshots(only_active=False) -> None:
        """ Get the headshots of all the players
        """
        ids = NbaScraper.get_all_ids(only_active=only_active)
        for id in ids:
            NbaScraper.get_player_headshot(id)





class ShotCharts:
        def __init__(self) -> None:
                pass
        
        def create_court(ax: mpl.axes, color="white") -> mpl.axes:
                """ Create a basketball court in a matplotlib axes
                """
                # Short corner 3PT lines
                ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
                ax.plot([220, 220], [0, 140], linewidth=2, color=color)
                # 3PT Arc
                ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))
                # Lane and Key
                ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
                ax.plot([80, 80], [0, 190], linewidth=2, color=color)
                ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
                ax.plot([60, 60], [0, 190], linewidth=2, color=color)
                ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
                ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))
                ax.plot([-250, 250], [0, 0], linewidth=4, color='white')
                # Rim
                ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))
                # Backboard
                ax.plot([-30, 30], [40, 40], linewidth=2, color=color)
                # Remove ticks
                ax.set_xticks([])
                ax.set_yticks([])
                # Set axis limits
                ax.set_xlim(-250, 250)
                ax.set_ylim(0, 470)
                return ax
        
        def add_headshot(fig: plt.figure, id: int) -> plt.figure:
       
            headshot_url = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{id}.png"
            
            try:
                response = requests.get(headshot_url)
                
                # Check if the request was successful and the content type is an image
                if response.status_code == 200 and response.headers['Content-Type'].startswith('image/'):
                    img = Image.open(BytesIO(response.content))
                    ax = fig.add_axes([0.06, 0.01, 0.3, 0.3], anchor='SW')
                    ax.imshow(img)
                    ax.axis('off')
                else:
                    print(f"The response did not contain an image. Status Code: {response.status_code}")
            except UnidentifiedImageError:
                print(f"Cannot identify image file from {headshot_url}. The file may be corrupted or the URL is incorrect.")
            except Exception as e:
                print(f"An error occurred: {e}")

            return fig
                
        #def add_headshot(fig: plt.figure, id: int) -> plt.figure:
                #headshot_path = "https://github.com/ubiratanfilho/HotShot/blob/main/data/nba/raw/headshots/"+ str(id) +".png?raw=true" 
                #im = plt.imread(headshot_path)
                #ax = fig.add_axes([0.06, 0.01, 0.3, 0.3], anchor='SW')
                #ax.imshow(im)
                #ax.axis('off')
                #return fig
        
        def frequency_chart(df: pd.DataFrame, name: str, season=None, extent=(-250, 250, 422.5, -47.5),
                                gridsize=25, cmap="inferno"):
                """ Create a shot chart of a player's shot frequency and accuracy
                """ 
                # create frequency of shots per hexbin zone
                shots_hex = plt.hexbin(
                df.LOC_X, df.LOC_Y + 60,
                extent=extent, cmap=cmap, gridsize=gridsize)
                plt.close()
                shots_hex_array = shots_hex.get_array()
                freq_by_hex = shots_hex_array / sum(shots_hex_array)
                
                # create field goal % per hexbin zone
                makes_df = df[df.SHOT_MADE_FLAG == 1] # filter dataframe for made shots
                makes_hex = plt.hexbin(makes_df.LOC_X, makes_df.LOC_Y + 60, cmap=cmap,
                                gridsize=gridsize, extent=extent) # create hexbins
                plt.close()
                pcts_by_hex = makes_hex.get_array() / shots_hex.get_array()
                pcts_by_hex[np.isnan(pcts_by_hex)] = 0  # convert NAN values to 0
                
                # filter data for zone with at least 5 shots made
                sample_sizes = shots_hex.get_array()
                filter_threshold = 5
                for i in range(len(pcts_by_hex)):
                        if sample_sizes[i] < filter_threshold:
                                pcts_by_hex[i] = 0
                x = [i[0] for i in shots_hex.get_offsets()]
                y = [i[1] for i in shots_hex.get_offsets()]
                z = pcts_by_hex
                sizes = freq_by_hex * 1000
                
                # Create figure and axes
                fig = plt.figure(figsize=(3.6, 3.6), facecolor='black', edgecolor='black', dpi=100)
                ax = fig.add_axes([0, 0, 1, 1], facecolor='black')
                plt.xlim(250, -250)
                plt.ylim(-47.5, 422.5)
                # Plot hexbins
                scatter = ax.scatter(x, y, c=z, cmap=cmap, marker='h', s=sizes)
                # Draw court
                ax = ShotCharts.create_court(ax)
                # Add legends
                max_freq = max(freq_by_hex)
                max_size = max(sizes)
                legend_acc = plt.legend(
                *scatter.legend_elements(num=5, fmt="{x:.0f}%",
                                        func=lambda x: x * 100),
                loc=[0.85,0.785], title='Shot %', fontsize=6)
                legend_freq = plt.legend(
                *scatter.legend_elements(
                        'sizes', num=5, alpha=0.8, fmt="{x:.1f}%"
                        , func=lambda s: s / max_size * max_freq * 100
                ),
                loc=[0.68,0.785], title='Freq %', fontsize=6)
                plt.gca().add_artist(legend_acc)
                # Add title
                plt.text(-250, 450, f"{name}", fontsize=21, color='white',
                        fontname='Arial')
                plt.text(-250, 420, "Frequency and FG%", fontsize=12, color='white',
                        fontname='Arial')
                season = f"{season[0][:4]}-{season[-1][-2:]}"
                plt.text(-250, -20, season, fontsize=8, color='white')
                #plt.text(110, -20, '@hotshot_nba', fontsize=8, color='white')
                
                # add headshot
                fig = ShotCharts.add_headshot(fig, df.PLAYER_ID.iloc[0])

                return fig
        
        def volume_chart(df: pd.DataFrame, name: str, season=None, 
                        RA=True,
                        extent=(-250, 250, 422.5, -47.5),
                        gridsize=25, cmap="plasma"):
                fig = plt.figure(figsize=(3.6, 3.6), facecolor='black', edgecolor='black', dpi=100)
                ax = fig.add_axes([0, 0, 1, 1], facecolor='black')

                # Plot hexbin of shots
                if RA == True:
                        x = df.LOC_X
                        y = df.LOC_Y + 60
                        # Annotate player name and season
                        plt.text(-250, 440, f"{name}", fontsize=21, color='white',
                                fontname='Arial')
                        plt.text(-250, 410, "Shot Volume", fontsize=12, color='white',
                                fontname='Arial')
                        season = f"{season[0][:4]}-{season[-1][-2:]}"
                        plt.text(-250, -20, season, fontsize=8, color='white')
                        #plt.text(110, -20, '@hotshot_nba', fontsize=8, color='white')
                else:
                        cond = ~((-45 < df.LOC_X) & (df.LOC_X < 45) & (-40 < df.LOC_Y) & (df.LOC_Y < 45))
                        x = df.LOC_X[cond]
                        y = df.LOC_Y[cond] + 60
                        # Annotate player name and season
                        plt.text(-250, 440, f"{name}", fontsize=21, color='white',
                                fontname='Arial')
                        plt.text(-250, 410, "Shot Volume", fontsize=12, color='white',
                                fontname='Arial')
                        plt.text(-250, 385, "(w/o restricted area)", fontsize=10, color='red')
                        season = f"{season[0][:4]}-{season[-1][-2:]}"
                        plt.text(-250, -20, season, fontsize=8, color='white')
                        #plt.text(110, -20, '@hotshot_nba', fontsize=8, color='white')
                        
                hexbin = ax.hexbin(x, y, cmap=cmap,
                        bins="log", gridsize=25, mincnt=2, extent=(-250, 250, 422.5, -47.5))

                # Draw court
                ax = ShotCharts.create_court(ax, 'white')

                # add colorbar
                #im = plt.imread("https://github.com/ubiratanfilho/HotShot/blob/main/images/Colorbar%20Shotcharts.png?raw=true")
                #newax = fig.add_axes([0.56, 0.6, 0.45, 0.4], anchor='NE', zorder=1)
                #newax.xaxis.set_visible(False)
                #newax.yaxis.set_visible(False)
                #newax.imshow(im)
                url = "https://github.com/ubiratanfilho/HotShot/blob/main/images/Colorbar%20Shotcharts.png?raw=true"
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                colorbar_data = np.array(img)
                
                
                # add colorbar
                newax = fig.add_axes([0.56, 0.6, 0.45, 0.4], anchor='NE', zorder=1)
                newax.xaxis.set_visible(False)
                newax.yaxis.set_visible(False)
                newax.imshow(colorbar_data)
                
                
                # add headshot
                fig = ShotCharts.add_headshot(fig, df.PLAYER_ID.iloc[0])

                return fig
        
        def makes_misses_chart(df: pd.DataFrame, name: str, season=None):
                # Create figure and axes
                fig = plt.figure(figsize=(3.6, 3.6), facecolor='black', edgecolor='black', dpi=100)
                ax = fig.add_axes([0, 0, 1, 1], facecolor='black')

                plt.text(-250, 450, f"{name}", fontsize=21, color='white',
                        fontname='Arial')
                plt.text(-250, 425, "Misses", fontsize=12, color='red',
                        fontname='Arial')
                plt.text(-170, 425, "&", fontsize=12, color='white',
                        fontname='Arial')
                plt.text(-150, 425, "Buckets", fontsize=12, color='green',
                        fontname='Arial')
                season = f"{season[0][:4]}-{season[-1][-2:]}"
                plt.text(-250, -20, season, fontsize=8, color='white')
                #plt.text(110, -20, '@hotshot_nba', fontsize=8, color='white')

                ax = ShotCharts.create_court(ax, 'white')
                sc = ax.scatter(df.LOC_X, df.LOC_Y + 60, c=df.SHOT_MADE_FLAG, cmap='RdYlGn', s=12)
                
                # add headshot
                fig = ShotCharts.add_headshot(fig, df.PLAYER_ID.iloc[0])

                return fig





def nba_stats_page():
    st.title("SHOT Charts Analysis")

    player_name = st.text_input("Enter the player's name:", '')
    st.write("Here are some Players names: 'LeBron James', 'Luka Doncic'..")

    if player_name:
        player_info = NbaScraper.get_json_from_name(player_name)
        if player_info:
            player_id = player_info['id']
            # Assume the format of the season identifier is 'Year-Year'
            current_season = '2022-23'  # Set the season you're interested in
            career = NbaScraper.get_player_career(player_id)
            
            # Filter the career DataFrame for the current season
            career = career[career['SEASON_ID'] == current_season]
            
            if career.empty:
                st.write(f"No data available for {player_name} for the 2022-2023 season.")
                return
            
            team_ids = list(set(career['TEAM_ID']))
            shot_data = NbaScraper.get_shot_data(player_id, team_ids, [current_season])

            if not shot_data.empty:
                st.write(f"Shot chart for {player_name} for the 2022-2023 season")
                chart1 = ShotCharts.volume_chart(shot_data, player_name, [current_season])
                st.pyplot(chart1.figure)

                chart2 = ShotCharts.volume_chart(shot_data, player_name, [current_season], RA=False)
                st.pyplot(chart2.figure)

                chart3 = ShotCharts.frequency_chart(shot_data, player_name, [current_season])
                st.pyplot(chart3.figure)

                chart4 = ShotCharts.makes_misses_chart(shot_data, player_name, [current_season])
                st.pyplot(chart4.figure)
            else:
                st.write("No shot data available for the selected player for the 2022-2023 season.")
        else:
            st.write(f"Player '{player_name}' not found.")





def home_page():
    st.title(" Visualizations ")
    api_url = 'https://nba-api-ash-1-fc1674476d71.herokuapp.com/dataset' 
    nba_data = fetch_data(api_url)
    preprocessed_data = preprocess_data(nba_data)
    # Display buttons for showing original and preprocessed dataframes
    st.write("## Explore the Data")
    if st.button('Show Original DataFrame'):
        st.write("### Original DataFrame")
        st.dataframe(nba_data)  # This will automatically adjust the height

    st.markdown("---")

    #if st.button('Show Preprocessed DataFrame'):
        #st.write("### Preprocessed DataFrame")
        #st.dataframe(preprocessed_data) 

    # Section for Top Performers with dynamically generated buttons
    st.write("## Top Performers in Different Categories")
    st.write("Choose any one category to find out the top performers")
    selected_category = st.selectbox("Select a Category:", ["Points", "Assists", "Rebounds", "Steals", "Blocks"])#, "FG Percentage", "3P Percentage", "FT Percentage"])

    if st.button("Show Top Performers"):
        top_performers_plot = generate_top_performers_plots(nba_data, selected_category)
        st.pyplot(top_performers_plot)#, use_container_width=True)

    st.markdown("---")


    # Section for Scatter Plot of Players
    st.write("## Scatter Plot Analysis")
    st.write("Top NBA Players as Per Different Positions:")
    scatter_plot(preprocessed_data)

    # Player Comparison Section
    #st.write("## Compare Players Performances")
    #col1, col2 = st.columns(2)
    #with col1:
        #player1 = st.selectbox("Select the first player:", preprocessed_data['Player'].unique(), key='player1')
    #with col2:
        #player2 = st.selectbox("Select the second player:", preprocessed_data['Player'].unique(), key='player2')

    #if st.button("Run Player Comparison"):
        #generate_player_comparison_plots(preprocessed_data, player1, player2)

    # Footer with disclaimer
    st.markdown("---")
    


def main():
    page = st.sidebar.radio("Navigate", ['Home','Visualizations', 'Player Stats & Comparision', 'Live Score'])
    # Setup the sidebar
    with st.sidebar: 
        st.image('https://raw.githubusercontent.com/Kaushiknb11/Basketball_Analytics/main/hoopshub.png')
        st.title('HoopsHub: NBA Insights Platform')
        st.markdown("""Developed by:  
    - Sashank Gangadharabhotla  
    - Kaushik Narasimha Bukkapatnam  
    - Mohammed Junaid Shaik  
    - Sriram Reddy Arabelli""")

    # Content based on page selection
    if page =='Home':
        st.title("Welcome to the World of NBA Analytics")
        st.write(
        """
        Explore in-depth player statistics, shot charts, and comparison analysis across the current NBA Players.
        """
        )
        st.image('https://static01.nyt.com/images/2017/07/12/sports/12SUMMERLEAGUE-web1/12SUMMERLEAGUE-web1-videoSixteenByNineJumbo1600.jpg', use_column_width=True) 
        
    elif page == 'Visualizations':
        home_page()
        nba_stats_page()
    elif page == 'Player Stats & Comparision':
        page_2()
        #st.write('Player Stats & Comparision')  # Calling the NBA stats page function
    elif page == 'Live Score':
        st.write("Live Score")
        live_page()

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
