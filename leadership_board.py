# from modules import display_leadership_board_friends, display_leadership_board_global
# import streamlit as sl
# import pandas as pd

# def display_leadership_board(user_id):
#     sl.markdown("## 🏆 Leaderboard")
   
#     sl.markdown("""
#         <style>
#         /* Center the tab bar */
#         .stTabs [data-baseweb="tab-list"] {
#             justify-content: center;
#             gap: 2rem;
#         }

#         /* Force font size on tabs */
#         .stTabs [data-baseweb="tab"] > button {
#             font-size: 2rem !important;
#             padding: 0.75rem 1.5rem;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     tab1, tab2 = sl.tabs(["👥 Friends", "🌎Global"])
#     with tab1:
#         leaderboard_data = [('user1', 500), ('user2', 300), ('You', 250), ('user3', 200), ('user4', 150)]

#         sl.markdown("""
#         <style>
#         .leaderboard-header, .leaderboard-card {
#             background-color: #f0f2f6;
#             border-radius: 12px;
#             padding: 0.75rem 1.5rem;
#             margin: 0.5rem 0;
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#             font-family: 'Segoe UI', sans-serif;
#         }

#         .leaderboard-header {
#             font-weight: 600;
#             background-color: #e4e6eb;
#             border-left: 6px solid #6c757d;
#         }

#         .leaderboard-card.you {
#             background-color: #d1e7dd;
#             font-weight: bold;
#             border-left: 6px solid #0f5132;
#         }

#         .rank {
#             font-size: 1.1rem;
#             width: 40px;
#             font-weight: bold;
#         }

#         .rank.gold { color: #FFD700; }   /* gold */
#         .rank.silver { color: #C0C0C0; } /* silver */
#         .rank.bronze { color: #CD7F32; } /* bronze */
#         .rank.default { color: #333; }   /* black */

#         .name {
#             flex-grow: 1;
#             font-size: 1.05rem;
#             margin-left: 1rem;
#         }

#         .score {
#             font-size: 1.05rem;
#             color: #333;
#             white-space: nowrap;
#         }
#         </style>
#         """, unsafe_allow_html=True)


#         # Header row
#         sl.markdown(f"""
#         <div class="leaderboard-header">
#             <div class="rank"></div>
#             <div class="name">Name</div>
#             <div class="score">Calories Burned🔥</div>
#         </div>
#         """, unsafe_allow_html=True)

#         # Player rows with colored rank numbers
#         for i, (user, score) in enumerate(leaderboard_data, start=1):
#             if i == 1:
#                 rank_class = "gold"
#             elif i == 2:
#                 rank_class = "silver"
#             elif i == 3:
#                 rank_class = "bronze"
#             else:
#                 rank_class = "default"
            
#             card_class = "leaderboard-card you" if user == "You" else "leaderboard-card"
            
#             sl.markdown(f"""
#             <div class="{card_class}">
#                 <div class="rank {rank_class}">{i}</div>
#                 <div class="name">{user}</div>
#                 <div class="score">{score} kcal</div>
#             </div>
#             """, unsafe_allow_html=True)
                
#     with tab2:
#         leaderboard_data = [('user50', 456), ('user2', 150), ('You', 50)]

#         # Convert to DataFrame
#         df = pd.DataFrame(leaderboard_data, columns=["User", "Score"])
#         df.index += 1  # start ranks from 1

#         # Optional: Add a Rank column
#         df.insert(0, "Rank", df.index)

#         # Display leaderboard
#         sl.dataframe(df, use_container_width=True)