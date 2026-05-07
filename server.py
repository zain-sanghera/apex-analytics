"""
Apex Analytics - Python HTTP Server & REST API
Team: Goal Diggers (Ibrahim, Zain, Aashir, Sitara, Abdullah)
"""

import http.server
import json
import os
import urllib.parse

from data_loader import (
    load_players, get_player_by_name, filter_players, get_column,
    get_teams, get_positions, get_team_players, sort_players,
    search_players, get_top_players
)
import stats_engine as se

# Support both local and production environments
PORT = int(os.environ.get('PORT', 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYERS = load_players()

CONTENT_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.csv': 'text/csv',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.ico': 'image/x-icon',
    '.svg': 'image/svg+xml',
}


def json_response(handler, data, status=200):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode('utf-8'))


def compute_player_analysis(player):
    """Compute full statistical analysis for a single player"""
    matches = player.get('matches_played', 1) or 1
    goals = player.get('goals', 0)
    assists = player.get('assists', 0)
    shots = player.get('shots', 0)
    shots_ot = player.get('shots_on_target', 0)
    passes_c = player.get('passes_completed', 0)
    passes_a = player.get('passes_attempted', 0)
    minutes = player.get('minutes_played', 0)
    tackles = player.get('tackles', 0)
    interceptions = player.get('interceptions', 0)

    # Per-match rates
    goals_per_match = se.goal_scoring_rate(goals, matches)
    ga_per_match = se.goal_contribution(goals, assists, matches)

    # Accuracy metrics
    shot_acc = se.shot_accuracy(shots_ot, shots)
    conversion = se.shot_conversion_rate(goals, shots)
    pass_acc = se.pass_accuracy(passes_c, passes_a)

    # Minutes efficiency
    mins_per_goal = se.minutes_per_goal(minutes, goals)
    mins_per_gc = se.minutes_per_goal_contribution(minutes, goals, assists)

    # Defensive
    def_actions = se.defensive_actions_per_match(tackles, interceptions, matches)
    discipline = se.discipline_score(
        player.get('yellow_cards', 0), player.get('red_cards', 0), matches
    )

    # Composite score
    composite = se.player_composite_score(player)

    # Z-scores vs league
    all_goals = get_column(PLAYERS, 'goals')
    all_assists = get_column(PLAYERS, 'assists')
    all_ratings = get_column(PLAYERS, 'rating')

    z_goals = round(se.z_score(goals, all_goals), 2)
    z_assists = round(se.z_score(assists, all_assists), 2)
    z_rating = round(se.z_score(player.get('rating', 0), all_ratings), 2)

    # Percentile ranks
    pct_goals = round(se.percentile_rank(goals, all_goals), 1)
    pct_assists = round(se.percentile_rank(assists, all_assists), 1)
    pct_rating = round(se.percentile_rank(player.get('rating', 0), all_ratings), 1)

    # Poisson prediction: goals in next 5 matches
    poisson_pred = se.predict_goals_poisson(goals, matches, 5)

    # Season projection
    season_proj = se.predict_season_goals(goals, matches, 38)

    # Binomial: P(scoring in a single match)
    p_score = goals / matches if matches > 0 else 0
    binom_at_least_one = round((1 - se.binomial_pmf(1, 0, p_score)) * 100, 2)

    return {
        'goals_per_match': round(goals_per_match, 3),
        'ga_per_match': round(ga_per_match, 3),
        'shot_accuracy': round(shot_acc, 1),
        'conversion_rate': round(conversion, 1),
        'pass_accuracy': round(pass_acc, 1),
        'minutes_per_goal': round(mins_per_goal, 1) if mins_per_goal != float('inf') else None,
        'minutes_per_gc': round(mins_per_gc, 1) if mins_per_gc != float('inf') else None,
        'defensive_actions_per_match': round(def_actions, 2),
        'discipline_score': round(discipline, 3),
        'composite_score': composite,
        'z_score_goals': z_goals,
        'z_score_assists': z_assists,
        'z_score_rating': z_rating,
        'percentile_goals': pct_goals,
        'percentile_assists': pct_assists,
        'percentile_rating': pct_rating,
        'poisson_next5': poisson_pred,
        'season_projection_goals': season_proj,
        'prob_scoring_next_match': binom_at_least_one,
    }


class ApexHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[Apex] {args[0]}")

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = dict(urllib.parse.parse_qsl(parsed.query))

        # API Routes
        if path == '/api/players':
            self.handle_players(params)
        elif path == '/api/player':
            self.handle_player(params)
        elif path == '/api/compare':
            self.handle_compare(params)
        elif path == '/api/predict':
            self.handle_predict(params)
        elif path == '/api/distribution':
            self.handle_distribution(params)
        elif path == '/api/team':
            self.handle_team(params)
        elif path == '/api/rankings':
            self.handle_rankings(params)
        elif path == '/api/correlation':
            self.handle_correlation(params)
        elif path == '/api/summary':
            self.handle_summary(params)
        elif path == '/api/meta':
            self.handle_meta()
        else:
            self.serve_static(path)

    def handle_players(self, params):
        position = params.get('position', '')
        team = params.get('team', '')
        search = params.get('search', '')
        sort_by = params.get('sort', 'rating')
        order = params.get('order', 'desc')
        min_matches = int(params.get('min_matches', '0'))

        result = filter_players(PLAYERS, position or None, team or None, min_matches)
        if search:
            result = search_players(result, search)
        result = sort_players(result, sort_by, descending=(order == 'desc'))

        # Add composite score
        for p in result:
            p['composite_score'] = se.player_composite_score(p)

        json_response(self, {'players': result, 'count': len(result)})

    def handle_player(self, params):
        name = params.get('name', '')
        if not name:
            json_response(self, {'error': 'Name parameter required'}, 400)
            return
        player = get_player_by_name(PLAYERS, name)
        if not player:
            json_response(self, {'error': 'Player not found'}, 404)
            return

        analysis = compute_player_analysis(player)
        json_response(self, {'player': player, 'analysis': analysis})

    def handle_compare(self, params):
        name1 = params.get('player1', '')
        name2 = params.get('player2', '')
        p1 = get_player_by_name(PLAYERS, name1)
        p2 = get_player_by_name(PLAYERS, name2)
        if not p1 or not p2:
            json_response(self, {'error': 'Both players must be found'}, 404)
            return

        a1 = compute_player_analysis(p1)
        a2 = compute_player_analysis(p2)

        # Bayesian comparison
        prior = 7.0
        ratings1 = [p1.get('rating', 7.0)] * max(p1.get('matches_played', 1), 1)
        ratings2 = [p2.get('rating', 7.0)] * max(p2.get('matches_played', 1), 1)
        bayes1 = se.predict_performance_bayesian(prior, ratings1)
        bayes2 = se.predict_performance_bayesian(prior, ratings2)

        # Probability p1 is better (using normal approximation)
        diff_mean = bayes1[0] - bayes2[0]
        diff_std = (bayes1[1]**2 + bayes2[1]**2)**0.5 or 0.01
        prob_p1_better = round(se.normal_cdf(0, -diff_mean, diff_std) * 100, 1)

        json_response(self, {
            'player1': p1, 'analysis1': a1,
            'player2': p2, 'analysis2': a2,
            'bayesian1': {'mean': bayes1[0], 'std': bayes1[1]},
            'bayesian2': {'mean': bayes2[0], 'std': bayes2[1]},
            'prob_player1_better': prob_p1_better,
            'prob_player2_better': round(100 - prob_p1_better, 1),
        })

    def handle_predict(self, params):
        name = params.get('name', '')
        future = int(params.get('matches', '5'))
        player = get_player_by_name(PLAYERS, name)
        if not player:
            json_response(self, {'error': 'Player not found'}, 404)
            return

        matches = player.get('matches_played', 1) or 1
        goals = player.get('goals', 0)
        assists = player.get('assists', 0)
        shots = player.get('shots', 0)

        # Poisson predictions for goals
        poisson_goals = se.predict_goals_poisson(goals, matches, future)

        # Poisson predictions for assists
        poisson_assists = se.predict_goals_poisson(assists, matches, future)

        season_goals = se.predict_season_goals(goals, matches, 38)
        season_assists = se.predict_season_goals(assists, matches, 38)

        # Binomial: probability of scoring in each of the next N matches
        p_score = goals / matches
        prob_score_all = round(se.binomial_pmf(future, future, p_score) * 100, 2)
        prob_score_none = round(se.binomial_pmf(future, 0, p_score) * 100, 2)
        prob_score_at_least_one = round((1 - se.binomial_pmf(future, 0, p_score)) * 100, 2)

        # Expected goals and confidence interval
        exp_goals = round(goals / matches * future, 2)
        std_goals = round((goals / matches * future * (1 - goals / matches if goals / matches < 1 else 0.1)) ** 0.5, 2)

        json_response(self, {
            'player': player,
            'future_matches': future,
            'poisson_goals': poisson_goals,
            'poisson_assists': poisson_assists,
            'season_projection': {
                'goals': season_goals,
                'assists': season_assists,
            },
            'binomial': {
                'prob_score_all_matches': prob_score_all,
                'prob_score_no_match': prob_score_none,
                'prob_score_at_least_one': prob_score_at_least_one,
            },
            'expected_goals': exp_goals,
            'std_goals': std_goals,
        })

    def handle_distribution(self, params):
        field = params.get('field', 'goals')
        dist_type = params.get('type', 'normal')
        position = params.get('position', '')

        filtered = filter_players(PLAYERS, position or None)
        data = [p.get(field, 0) for p in filtered if p.get(field, 0) is not None]

        if not data:
            json_response(self, {'error': 'No data'}, 404)
            return

        summary = se.full_summary(data)
        curve = se.generate_distribution_data(data, dist_type)

        json_response(self, {
            'field': field,
            'distribution': dist_type,
            'summary': summary,
            'curve': curve,
            'raw_data': data,
        })

    def handle_team(self, params):
        team_name = params.get('name', '')
        if not team_name:
            teams = get_teams(PLAYERS)
            team_stats = []
            for t in teams:
                tp = get_team_players(PLAYERS, t)
                team_stats.append({
                    'name': t,
                    'player_count': len(tp),
                    'total_goals': sum(p.get('goals', 0) for p in tp),
                    'total_assists': sum(p.get('assists', 0) for p in tp),
                    'avg_rating': round(se.mean([p.get('rating', 0) for p in tp]), 2),
                    'avg_age': round(se.mean([p.get('age', 0) for p in tp]), 1),
                })
            json_response(self, {'teams': team_stats})
            return

        tp = get_team_players(PLAYERS, team_name)
        if not tp:
            json_response(self, {'error': 'Team not found'}, 404)
            return

        goals_data = get_column(tp, 'goals')
        assists_data = get_column(tp, 'assists')
        ratings_data = get_column(tp, 'rating')

        for p in tp:
            p['composite_score'] = se.player_composite_score(p)

        json_response(self, {
            'team': team_name,
            'players': tp,
            'stats': {
                'goals': se.full_summary(goals_data),
                'assists': se.full_summary(assists_data),
                'ratings': se.full_summary(ratings_data),
                'total_goals': sum(goals_data),
                'total_assists': sum(assists_data),
            }
        })

    def handle_rankings(self, params):
        field = params.get('field', 'goals')
        position = params.get('position', '')
        n = int(params.get('limit', '10'))
        filtered = filter_players(PLAYERS, position or None)
        top = get_top_players(filtered, field, n)
        for p in top:
            p['composite_score'] = se.player_composite_score(p)
        json_response(self, {'field': field, 'rankings': top})

    def handle_correlation(self, params):
        field1 = params.get('x', 'shots')
        field2 = params.get('y', 'goals')
        position = params.get('position', '')
        filtered = filter_players(PLAYERS, position or None)
        x = [p.get(field1, 0) for p in filtered]
        y = [p.get(field2, 0) for p in filtered]

        r = se.pearson_correlation(x, y)
        slope, intercept, r_sq = se.linear_regression(x, y)

        points = [{'x': xi, 'y': yi, 'name': p.get('name', '')}
                  for xi, yi, p in zip(x, y, filtered)]

        json_response(self, {
            'x_field': field1,
            'y_field': field2,
            'correlation': round(r, 4),
            'r_squared': round(r_sq, 4),
            'regression': {'slope': round(slope, 4), 'intercept': round(intercept, 4)},
            'points': points,
        })

    def handle_summary(self, params):
        field = params.get('field', 'goals')
        position = params.get('position', '')
        filtered = filter_players(PLAYERS, position or None)
        data = [p.get(field, 0) for p in filtered]
        summary = se.full_summary(data)
        json_response(self, {'field': field, 'summary': summary})

    def handle_meta(self):
        json_response(self, {
            'project': 'Apex Analytics',
            'team': 'Goal Diggers',
            'members': ['Ibrahim', 'Zain', 'Aashir', 'Sitara', 'Abdullah'],
            'total_players': len(PLAYERS),
            'teams': get_teams(PLAYERS),
            'positions': get_positions(PLAYERS),
            'fields': [
                'goals', 'assists', 'shots', 'shots_on_target',
                'passes_completed', 'passes_attempted', 'tackles',
                'interceptions', 'clean_sheets', 'yellow_cards',
                'red_cards', 'dribbles_completed', 'aerial_duels_won',
                'rating', 'age', 'matches_played', 'minutes_played'
            ],
        })

    def serve_static(self, path):
        if path == '/':
            path = '/index.html'

        filepath = os.path.join(BASE_DIR, path.lstrip('/'))
        if not os.path.isfile(filepath):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            return

        ext = os.path.splitext(filepath)[1]
        content_type = CONTENT_TYPES.get(ext, 'application/octet-stream')

        with open(filepath, 'rb') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run():
    server = http.server.HTTPServer(('0.0.0.0', PORT), ApexHandler)
    print(f"""
    ╔══════════════════════════════════════════╗
    ║         APEX ANALYTICS SERVER            ║
    ║     Football Performance Analyzer        ║
    ║                                          ║
    ║  Team: Goal Diggers                      ║
    ║  Members: Ibrahim, Zain, Aashir,         ║
    ║           Sitara, Abdullah               ║
    ║                                          ║
    ║  Server running on port {PORT}              ║
    ║  Environment: {'Production' if PORT != 8000 else 'Local'}     ║
    ╚══════════════════════════════════════════╝
    """)
    server.serve_forever()


if __name__ == '__main__':
    run()
