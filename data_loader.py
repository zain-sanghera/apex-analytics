"""
Apex Analytics - Data Loader
Reads and processes the football player CSV dataset.
Team: Goal Diggers (Ibrahim, Zain, Aashir, Sitara, Abdullah)
"""

import csv
import os


# Fields that should be parsed as integers
INT_FIELDS = [
    'age', 'matches_played', 'minutes_played', 'goals', 'assists',
    'shots', 'shots_on_target', 'passes_completed', 'passes_attempted',
    'tackles', 'interceptions', 'clean_sheets', 'yellow_cards',
    'red_cards', 'dribbles_completed', 'aerial_duels_won'
]

# Fields that should be parsed as floats
FLOAT_FIELDS = ['rating']

# All stat fields
STAT_FIELDS = INT_FIELDS + FLOAT_FIELDS


def load_players(filepath=None):
    """
    Load players from CSV file.
    Returns a list of dictionaries, one per player.
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'players.csv')

    players = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            player = {}
            for key, value in row.items():
                key = key.strip()
                value = value.strip()
                if key in INT_FIELDS:
                    try:
                        player[key] = int(value)
                    except ValueError:
                        player[key] = 0
                elif key in FLOAT_FIELDS:
                    try:
                        player[key] = float(value)
                    except ValueError:
                        player[key] = 0.0
                else:
                    player[key] = value
            # Skip players with 0 matches (not in the league)
            if player.get('matches_played', 0) > 0:
                players.append(player)
    return players


def get_player_by_name(players, name):
    """Find a player by name (case-insensitive partial match)"""
    name_lower = name.lower()
    for player in players:
        if name_lower in player.get('name', '').lower():
            return player
    return None


def filter_players(players, position=None, team=None, min_matches=0):
    """Filter players by position, team, and minimum matches"""
    result = players
    if position:
        pos = position.upper()
        result = [p for p in result if p.get('position', '').upper() == pos]
    if team:
        team_lower = team.lower()
        result = [p for p in result if team_lower in p.get('team', '').lower()]
    if min_matches > 0:
        result = [p for p in result if p.get('matches_played', 0) >= min_matches]
    return result


def get_column(players, field):
    """Extract a single column of data from all players"""
    return [p.get(field, 0) for p in players]


def get_teams(players):
    """Get a sorted list of unique team names"""
    teams = set()
    for p in players:
        team = p.get('team', '')
        if team:
            teams.add(team)
    return sorted(teams)


def get_positions(players):
    """Get a sorted list of unique positions"""
    positions = set()
    for p in players:
        pos = p.get('position', '')
        if pos:
            positions.add(pos)
    return sorted(positions)


def get_team_players(players, team_name):
    """Get all players from a specific team"""
    team_lower = team_name.lower()
    return [p for p in players if team_lower in p.get('team', '').lower()]


def sort_players(players, field, descending=True):
    """Sort players by a specific field"""
    return sorted(players, key=lambda p: p.get(field, 0), reverse=descending)


def search_players(players, query):
    """Search players by name (case-insensitive)"""
    if not query:
        return players
    query_lower = query.lower()
    return [p for p in players if query_lower in p.get('name', '').lower()]


def get_top_players(players, field, n=10):
    """Get top N players by a specific field"""
    sorted_list = sort_players(players, field, descending=True)
    return sorted_list[:n]
