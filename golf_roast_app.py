import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

# Page config
st.set_page_config(
    page_title="PHX Open 25: Golf Roast Dashboard",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for golf theme and snark
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #2E8B57;
    text-align: center;
    font-weight: bold;
    margin-bottom: 2rem;
}
.subheader {
    color: #228B22;
    font-size: 1.5rem;
    margin-bottom: 1rem;
}
.roast-box {
    background-color: #fff5f5;
    padding: 1rem;
    border-radius: 10px;
    border: 2px solid #ff6b6b;
    border-left: 5px solid #ff6b6b;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    color: #333333;
}
.roast-box h3 {
    color: #ff6b6b;
    margin-bottom: 0.5rem;
}
.roast-box p {
    color: #333333;
    margin: 0.5rem 0;
}
.stat-box {
    background-color: #f0f8f0;
    padding: 0.8rem;
    border-radius: 10px;
    margin: 0.3rem 0;
    border: 1px solid #d0d0d0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    color: #333333;
    display: flex;
    align-items: center;
}
.player-name {
    color: #228B22;
    font-weight: bold;
    font-size: 1.1rem;
    min-width: 120px;
    margin-right: 1rem;
    text-align: left;
}
.stats-container {
    display: flex;
    gap: 1.5rem;
    flex: 1;
}
.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 60px;
}
.stat-label {
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 0.2rem;
}
.stat-value {
    font-weight: bold;
    font-size: 1rem;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# Golf data
golf_data = [
    {"date": "Sat, May 17 at 12:40 PM", "person": "Dan Marcus", "score": "43/47", "comment": ""},
    {"date": "Sat, May 17 at 2:07 PM", "person": "Josh Meliker", "score": "63/57", "comment": "#MostImproved #ShavingStrokes #ChasingGreatness"},
    {"date": "Sun, May 18 at 11:26 AM", "person": "Mark Blakey", "score": "56/50", "comment": "#showingnoimprovemnt"},
    {"date": "Sun, May 18 at 6:33 PM", "person": "Dan Marcus", "score": "48/46", "comment": "#MightSnapAClub"},
    {"date": "Sat, Jun 21 at 10:41 AM", "person": "Dan Marcus", "score": "48/41", "comment": "#momentum"},
    {"date": "Sun, Jun 29 at 10:51 AM", "person": "Dan Marcus", "score": "45/44", "comment": "#momentum?"},
    {"date": "Sun, Jun 29 at 10:51 AM", "person": "Josh Meliker", "score": "57/59", "comment": "#consistency?"},
    {"date": "Sun, Jun 29 at 2:10 PM", "person": "Brett Lazar", "score": "43/40", "comment": "#progress"},
    {"date": "Thu, Jul 3 at 1:55 PM", "person": "Josh Meliker", "score": "58/61", "comment": "#gettingworse"},
    {"date": "Fri, Jul 4 at 1:16 PM", "person": "Mark Blakey", "score": "51/53", "comment": "#regression #goingtokillmyself"},
    {"date": "Sat, Jul 5 at 5:55 PM", "person": "Dan Marcus", "score": "43/47", "comment": "#sepukku"},
    {"date": "Sat, Jul 5 at 5:55 PM", "person": "Brett Lazar", "score": "37/37", "comment": "#PR"},
    {"date": "Sun, Jul 6 at 1:28 PM", "person": "Mark Blakey", "score": "48/45", "comment": "#momentum #futurepro"},
    {"date": "Sat, Jul 12 at 1:29 PM", "person": "Mark Blakey", "score": "49/49", "comment": "#consistency"},
    {"date": "Sun, Jul 13 at 8:14 AM", "person": "Josh Meliker", "score": "53", "comment": "#Just9Today #HonestlyBetterThanUsual #9HolesOnly"},
    {"date": "Sat, Jul 19 at 12:37 PM", "person": "Dan Marcus", "score": "47/41", "comment": "#MadeAWish #ItCameTrue #BandonTuneUp"},
    {"date": "Sat, Jul 26 at 12:14 PM", "person": "Mark Blakey", "score": "53/51", "comment": "#improvement #remedialputting"},
    {"date": "Sat, Jul 26 at 4:15 PM", "person": "Dan Marcus", "score": "43/44", "comment": "#happy"},
    {"date": "Sat, Jul 26 at 6:31 PM", "person": "Brett Lazar", "score": "37/41", "comment": "#gamesfeelinggood"},
    {"date": "Sun, Jul 27 at 1:17 PM", "person": "Josh Meliker", "score": "55/55", "comment": "#consistency #completemeltdownon18"},
    {"date": "Sat, Aug 2 at 10:44 AM", "person": "Dan Marcus", "score": "41/39", "comment": "#HeatingUp #FeedMeBandon"},
    {"date": "Sun, Aug 3 at 11:40 AM", "person": "Mark Blakey", "score": "49/51", "comment": "#completecollapse"},
    {"date": "Sun, Aug 3 at 5:50 PM", "person": "Dan Marcus", "score": "45/43", "comment": "#ReversionToTheMean"},
    {"date": "Fri, Aug 8 at 10:15 PM", "person": "Dan Marcus", "score": "42/50", "comment": "#ButParWas34/38 #30mphwind #SheepRanch"},
    {"date": "Saturday 11:05 PM", "person": "Dan Marcus", "score": "38/48", "comment": "#fuck"},
    {"date": "Saturday 11:05 PM", "person": "Dan Marcus", "score": "41/48", "comment": "#clearlynostamina"},
    {"date": "Sunday 12:30 PM", "person": "Josh Meliker", "score": "55/58", "comment": "#someonefuckingkillme"},
    {"date": "Monday 1:37 PM", "person": "Dan Marcus", "score": "36/48", "comment": "#HappyThenSad"},
    {"date": "Monday 9:23 PM", "person": "Dan Marcus", "score": "41/44", "comment": "#iamtired"},
    {"date": "Tuesday 7:08 PM", "person": "Dan Marcus", "score": "41/46", "comment": "#fin"},
    {"date": "Today 10:41 AM", "person": "Dan Marcus", "score": "45/43", "comment": "#ICannotBelieveIPlayedGolfToday"},
    {"date": "Today 3:01 PM", "person": "Brett Lazar", "score": "40/39", "comment": "#hotasballsinFL"}
]

def parse_date(date_str):
    """Parse various date formats from the data"""
    try:
        # Handle "Today" cases
        if "Today" in date_str:
            return datetime.now().date()
        
        # Handle standard format like "Sat, May 17 at 12:40 PM"
        date_part = date_str.split(" at ")[0]
        if "," in date_part:
            date_part = date_part.split(", ")[1]
        
        # Add year 2025 if not present
        if "2025" not in date_part:
            date_part += " 2025"
            
        return pd.to_datetime(date_part, errors='coerce').date()
    except:
        return pd.to_datetime("2025-08-01").date()

def parse_score(score_str):
    """Parse front/back scores and calculate totals"""
    if "/" in score_str:
        front, back = score_str.split("/")
        return int(front), int(back), int(front) + int(back), False  # False = not 9-hole
    else:
        # 9-hole round
        return int(score_str), None, int(score_str), True  # True = is 9-hole

def calculate_dan_curse_factor(person, front, back):
    """Calculate Dan's back 9 curse severity"""
    if person != "Dan Marcus" or back is None:
        return 0
    
    diff = back - front
    if diff > 5:
        return 3  # Severe curse
    elif diff > 2:
        return 2  # Moderate curse
    elif diff > 0:
        return 1  # Mild curse
    else:
        return 0  # No curse (miracle!)

# Main app
st.markdown('<h1 class="main-header">⛳ PHX Open 25: Rise of the Phoenix (and Fall of Dan\'s Back 9)</h1>', unsafe_allow_html=True)

# Process data
df_list = []
for entry in golf_data:
    date = parse_date(entry['date'])
    front, back, total, is_nine_hole = parse_score(entry['score'])
    curse_factor = calculate_dan_curse_factor(entry['person'], front, back)
    
    # Mark 9-hole rounds clearly
    score_display = f"{entry['score']} (9-hole)" if is_nine_hole else entry['score']
    
    df_list.append({
        'date': date,
        'person': entry['person'],
        'front_9': front,
        'back_9': back,
        'total_score': total,
        'comment': entry['comment'],
        'original_date': entry['date'],
        'curse_factor': curse_factor,
        'is_nine_hole': is_nine_hole,
        'hover_text': f"{entry['person']}<br>Score: {score_display}<br>Date: {entry['date']}<br>{entry['comment']}"
    })

df = pd.DataFrame(df_list)
df = df.sort_values('date')

# Sidebar filters
st.sidebar.markdown('<h2 class="subheader">🎯 Filter Options</h2>', unsafe_allow_html=True)
selected_players = st.sidebar.multiselect(
    "Select Players",
    options=df['person'].unique(),
    default=df['person'].unique()
)

# Filter data
filtered_df = df[df['person'].isin(selected_players)]

# Main dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h2 class="subheader">📈 Score Timeline</h2>', unsafe_allow_html=True)
    
    # Create interactive timeline
    fig = go.Figure()
    
    colors = {
        'Dan Marcus': '#FF4444',  # Bright red for Dan's struggles
        'Josh Meliker': '#00CED1',  # Dark turquoise
        'Brett Lazar': '#1E90FF',  # Dodger blue
        'Mark Blakey': '#32CD32'   # Lime green
    }
    
    for person in filtered_df['person'].unique():
        person_data = filtered_df[filtered_df['person'] == person]
        
        # Separate 18-hole and 9-hole rounds
        eighteen_hole = person_data[person_data['is_nine_hole'] == False]
        nine_hole = person_data[person_data['is_nine_hole'] == True]
        
        # Plot 18-hole rounds as regular line
        if not eighteen_hole.empty:
            fig.add_trace(go.Scatter(
                x=eighteen_hole['date'],
                y=eighteen_hole['total_score'],
                mode='lines+markers',
                name=f"{person} (18-hole)",
                line=dict(color=colors.get(person, '#333333'), width=4),
                marker=dict(
                    size=10, 
                    symbol='circle',
                    color=colors.get(person, '#333333'),
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>%{text}</b><extra></extra>',
                text=eighteen_hole['hover_text'],
                connectgaps=True
            ))
        
        # Plot 9-hole rounds as diamonds
        if not nine_hole.empty:
            fig.add_trace(go.Scatter(
                x=nine_hole['date'],
                y=nine_hole['total_score'],
                mode='markers',
                name=f"{person} (9-hole)",
                marker=dict(
                    size=12, 
                    symbol='diamond',
                    color=colors.get(person, '#333333'),
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>%{text}</b><extra></extra>',
                text=nine_hole['hover_text']
            ))
    
    fig.update_layout(
        title="Golf Scores Over Time (Lower is Better, Obviously)",
        xaxis_title="Date",
        yaxis_title="Total Score",
        hovermode='closest',
        height=500,
        showlegend=True,
        yaxis=dict(autorange='reversed')  # Lower scores at top
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Leaderboard right under the chart
    st.markdown('<h2 class="subheader">🏆 Leaderboard</h2>', unsafe_allow_html=True)
    
    if len(selected_players) > 0:
        # Calculate stats for each player and sort by best average
        player_stats = []
        for player in selected_players:
            player_data = filtered_df[filtered_df['person'] == player]
            eighteen_hole_data = player_data[player_data['is_nine_hole'] == False]
            
            if not eighteen_hole_data.empty:
                avg_18 = eighteen_hole_data['total_score'].mean()
                best_18 = eighteen_hole_data['total_score'].min()
                worst_18 = eighteen_hole_data['total_score'].max()
                rounds_18 = len(eighteen_hole_data)
                front_avg = eighteen_hole_data['front_9'].mean()
                back_avg = eighteen_hole_data['back_9'].mean()
                player_stats.append((player, avg_18, best_18, worst_18, rounds_18, front_avg, back_avg))
            else:
                player_stats.append((player, 999, 0, 0, 0, 0, 0))  # Put players with no rounds at the end
        
        # Sort by average score (best first)
        player_stats.sort(key=lambda x: x[1])
        
        for player, avg_18, best_18, worst_18, rounds_18, front_avg, back_avg in player_stats:
            if avg_18 == 999:  # No 18-hole rounds
                st.markdown(f"""
                <div class="stat-box">
                    <div class="player-name">{player}</div>
                    <div class="stats-container">
                        <span style="color: #666; font-style: italic;">No 18-hole rounds</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="player-name">{player}</div>
                    <div class="stats-container">
                        <div class="stat-item">
                            <div class="stat-label">Average</div>
                            <div class="stat-value">{avg_18:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Front 9</div>
                            <div class="stat-value">{front_avg:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Back 9</div>
                            <div class="stat-value">{back_avg:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Best</div>
                            <div class="stat-value">{best_18}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Worst</div>
                            <div class="stat-value">{worst_18}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Rounds</div>
                            <div class="stat-value">{rounds_18}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Please select at least one player to view statistics.")

with col2:
    st.markdown('<h2 class="subheader">🔥 Roast Corner</h2>', unsafe_allow_html=True)
    
    # Dan vs Brett: Quality vs Quantity Analysis
    dan_data = df[(df['person'] == 'Dan Marcus') & (df['is_nine_hole'] == False)]
    brett_data = df[(df['person'] == 'Brett Lazar') & (df['is_nine_hole'] == False)]
    
    if not dan_data.empty and not brett_data.empty:
        dan_avg = dan_data['total_score'].mean()
        brett_avg = brett_data['total_score'].mean()
        dan_rounds = len(dan_data)
        brett_rounds = len(brett_data)
        rounds_ratio = dan_rounds / brett_rounds if brett_rounds > 0 else 0
        score_diff = dan_avg - brett_avg
        
        st.markdown(f"""
        <div class="roast-box">
        <h3>🎯 Dan vs Brett: Practice Makes... Worse?</h3>
        <p><strong>Dan's Rounds:</strong> {dan_rounds}</p>
        <p><strong>Brett's Rounds:</strong> {brett_rounds}</p>
        <p><strong>Dan plays {rounds_ratio:.1f}x more golf</strong></p>
        <hr>
        <p><strong>Dan's Average:</strong> {dan_avg:.1f}</p>
        <p><strong>Brett's Average:</strong> {brett_avg:.1f}</p>
        <p><strong>Dan is {score_diff:.1f} strokes WORSE</strong></p>
        <p><em>All that practice for nothing! 🤡</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Worst Rounds Hall of Shame (18-hole only)
    eighteen_hole_df = df[df['is_nine_hole'] == False]
    worst_rounds = eighteen_hole_df.nlargest(3, 'total_score')
    st.markdown("""
    <div class="roast-box">
    <h3>🏆 Hall of Shame (Worst 18-Hole Rounds)</h3>
    """, unsafe_allow_html=True)
    
    for _, round_data in worst_rounds.iterrows():
        st.markdown(f"""
        <p><strong>{round_data['person']}</strong>: {round_data['total_score']} 
        <br><em>{round_data['comment']}</em></p>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Best Rounds (18-hole only)
    best_rounds = eighteen_hole_df.nsmallest(3, 'total_score')
    st.markdown("""
    <div class="roast-box" style="background-color: #f0fff0; border-color: #32cd32;">
    <h3>🌟 Best 18-Hole Rounds</h3>
    """, unsafe_allow_html=True)
    
    for _, round_data in best_rounds.iterrows():
        st.markdown(f"""
        <p><strong>{round_data['person']}</strong>: {round_data['total_score']} 
        <br><em>{round_data['comment']}</em></p>
        """, unsafe_allow_html=True)
    
    # Show 9-hole rounds separately
    nine_hole_df = df[df['is_nine_hole'] == True]
    if not nine_hole_df.empty:
        st.markdown("""
        <hr style="margin: 1rem 0;">
        <h4>9-Hole Rounds:</h4>
        """, unsafe_allow_html=True)
        
        for _, round_data in nine_hole_df.iterrows():
            st.markdown(f"""
            <p><strong>{round_data['person']}</strong>: {round_data['total_score']} (9-hole)
            <br><em>{round_data['comment']}</em></p>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

