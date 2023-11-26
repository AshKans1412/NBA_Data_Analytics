import pandas as pd
import streamlit as st
import requests
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

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

    # Setting up the aesthetics for the plots
    sns.set_style("whitegrid")
    plt.figure(figsize=(16, 12))

    # Plotting the top performers
    plt.subplot(3, 3, 1)
    sns.barplot(x=column_name, y='Player', data=top_performers, palette='viridis')
    plt.title(f'Top {category}')

    plt.suptitle(f'Top Performers in {category}', fontsize=20)
    plt.tight_layout()

    # Return the Matplotlib figure
    return plt.gcf()




def main():
    st.title("NBA Data Analysis App")

    # JSONPlaceholder API URL for NBA data
    api_url = 'https://ash-nba-api-ea2ef5de0ea1.herokuapp.com/dataset' 

    # Fetch data from the API and directly convert to DataFrame
    nba_data = fetch_data(api_url)
    
    # Initialize preprocessed_data
    preprocessed_data = preprocess_data(nba_data)

    # Sidebar options
    display_df = st.sidebar.selectbox("Display DataFrame", ["Select an option", "Orginal_dataframe", "pre_processed_data"], index=0, key='display_df')
    st.empty()

    # Display dataframes or plots based on user selection
    if display_df == "Orginal_dataframe":
        st.empty()  # Clear previous content
        st.write("## Original DataFrame")
        st.write(nba_data)
    elif display_df == "pre_processed_data":
        st.empty()  # Clear previous content
        st.write("## Preprocessed DataFrame")
        st.write(preprocessed_data)

    st.sidebar.header("Top Performers Categories")
    selected_category = st.sidebar.selectbox("Select a category:", ["Points", "Assists", "Rebounds", "Steals", "Blocks", "FG Percentage", "3P Percentage", "FT Percentage"])
    
    # Button to generate and display the plot
    generate_plot_button = st.sidebar.button("Generate Top Performers Plot")

    if generate_plot_button:
        st.sidebar.empty()  # Clear previous content
        
        # Generate the plot
        top_performers_plot = generate_top_performers_plots(nba_data, selected_category)
        
        # Display the plot using st.pyplot
        st.pyplot(top_performers_plot)

    option = st.sidebar.selectbox("Plots:", ["Select an option", "Points", "Assists", "Scatter Plot"], index=0)
    st.empty()

    # Display the selected information
    if option == "Points":
        st.empty()  # Clear previous content
        st.subheader(f"Top 10 Players by Points:")
        plot_pts(preprocessed_data)
    elif option == "Assists":
        st.empty()  # Clear previous content
        st.subheader(f"Top 10 Players by Assists:")
        plot_ast(preprocessed_data)
    elif option == "Scatter Plot":
        st.empty()  # Clear previous content
        st.subheader("Scatter Plot of AST vs PTS:")
        scatter_plot(preprocessed_data)

    
    player1 = st.sidebar.selectbox("Select the first player:", preprocessed_data['Player'].unique())
    player2 = st.sidebar.selectbox("Select the second player:", preprocessed_data['Player'].unique())

    display_chart = st.sidebar.button("Compare Player Stats")
    st.empty() 

    if display_chart:
        st.sidebar.empty()  # Clear previous content
        generate_player_comparison_plots(preprocessed_data, player1, player2)


if __name__ == "__main__":
    main()





