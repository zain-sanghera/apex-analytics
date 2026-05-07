"""
Apex Analytics - Statistics & Probability Engine
All formulas implemented from scratch without external libraries.
Team: Goal Diggers (Ibrahim, Zain, Aashir, Sitara, Abdullah)
"""

import math

# ============================================================
# CONSTANTS
# ============================================================
PI = 3.141592653589793
E = 2.718281828459045


# ============================================================
# 1. DESCRIPTIVE STATISTICS
# ============================================================

def mean(data):
    """Calculate arithmetic mean: sum(x) / n"""
    if not data:
        return 0
    return sum(data) / len(data)


def median(data):
    """Calculate median: middle value of sorted data"""
    if not data:
        return 0
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        return sorted_data[mid]


def mode(data):
    """Calculate mode: most frequently occurring value"""
    if not data:
        return 0
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_freq = max(frequency.values())
    modes = [k for k, v in frequency.items() if v == max_freq]
    return modes[0] if len(modes) == 1 else modes


def variance(data, population=True):
    """
    Calculate variance: sum((x - mean)^2) / n
    population=True  -> divide by n   (population variance)
    population=False -> divide by n-1 (sample variance)
    """
    if not data or len(data) < 2:
        return 0
    m = mean(data)
    squared_diffs = [(x - m) ** 2 for x in data]
    divisor = len(data) if population else (len(data) - 1)
    return sum(squared_diffs) / divisor


def std_dev(data, population=True):
    """Calculate standard deviation: sqrt(variance)"""
    return math.sqrt(variance(data, population))


def data_range(data):
    """Calculate range: max - min"""
    if not data:
        return 0
    return max(data) - min(data)


def quartiles(data):
    """Calculate Q1, Q2 (median), Q3"""
    if not data:
        return (0, 0, 0)
    sorted_data = sorted(data)
    n = len(sorted_data)
    q2 = median(sorted_data)
    mid = n // 2
    if n % 2 == 0:
        lower = sorted_data[:mid]
        upper = sorted_data[mid:]
    else:
        lower = sorted_data[:mid]
        upper = sorted_data[mid + 1:]
    q1 = median(lower) if lower else q2
    q3 = median(upper) if upper else q2
    return (q1, q2, q3)


def iqr(data):
    """Interquartile Range: Q3 - Q1"""
    q1, q2, q3 = quartiles(data)
    return q3 - q1


def coefficient_of_variation(data):
    """CV = (std_dev / mean) * 100"""
    m = mean(data)
    if m == 0:
        return 0
    return (std_dev(data) / m) * 100


def skewness(data):
    """
    Pearson's skewness coefficient:
    skew = (3 * (mean - median)) / std_dev
    """
    s = std_dev(data)
    if s == 0:
        return 0
    return (3 * (mean(data) - median(data))) / s


# ============================================================
# 2. Z-SCORE & PERCENTILE
# ============================================================

def z_score(x, data):
    """Z-score: (x - mean) / std_dev"""
    m = mean(data)
    s = std_dev(data)
    if s == 0:
        return 0
    return (x - m) / s


def z_score_direct(x, mu, sigma):
    """Z-score with known mean and std dev"""
    if sigma == 0:
        return 0
    return (x - mu) / sigma


def percentile_rank(x, data):
    """
    Percentile rank: (values_below + 0.5 * values_equal) / total * 100
    """
    if not data:
        return 0
    below = sum(1 for v in data if v < x)
    equal = sum(1 for v in data if v == x)
    return (below + 0.5 * equal) / len(data) * 100


def percentile(data, p):
    """Get the value at the p-th percentile (0-100)"""
    if not data:
        return 0
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = (p / 100) * (n - 1)
    f = int(k)
    c = k - f
    if f + 1 < n:
        return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
    return sorted_data[f]


# ============================================================
# 3. PROBABILITY THEORY
# ============================================================

def classical_probability(favorable, total):
    """P(A) = favorable outcomes / total outcomes"""
    if total == 0:
        return 0
    return favorable / total


def complement_probability(p_a):
    """P(A') = 1 - P(A)"""
    return 1 - p_a


def addition_rule(p_a, p_b, p_a_and_b):
    """P(A ∪ B) = P(A) + P(B) - P(A ∩ B)"""
    return p_a + p_b - p_a_and_b


def addition_rule_mutually_exclusive(p_a, p_b):
    """P(A ∪ B) = P(A) + P(B) when events are mutually exclusive"""
    return p_a + p_b


def multiplication_rule(p_a, p_b_given_a):
    """P(A ∩ B) = P(A) × P(B|A)"""
    return p_a * p_b_given_a


def multiplication_rule_independent(p_a, p_b):
    """P(A ∩ B) = P(A) × P(B) for independent events"""
    return p_a * p_b


def conditional_probability(p_a_and_b, p_b):
    """P(A|B) = P(A ∩ B) / P(B)"""
    if p_b == 0:
        return 0
    return p_a_and_b / p_b


def bayes_theorem(p_b_given_a, p_a, p_b):
    """
    Bayes' Theorem: P(A|B) = P(B|A) × P(A) / P(B)
    """
    if p_b == 0:
        return 0
    return (p_b_given_a * p_a) / p_b


def total_probability(priors, likelihoods):
    """
    Law of Total Probability:
    P(B) = Σ P(B|Ai) × P(Ai)
    priors: list of P(Ai)
    likelihoods: list of P(B|Ai)
    """
    return sum(p * l for p, l in zip(priors, likelihoods))


# ============================================================
# 4. COMBINATORICS (for distributions)
# ============================================================

def factorial(n):
    """n! = n × (n-1) × ... × 1"""
    if n < 0:
        return 0
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def combination(n, k):
    """C(n, k) = n! / (k! × (n-k)!)"""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    # Optimize: use smaller k
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def permutation(n, k):
    """P(n, k) = n! / (n-k)!"""
    if k < 0 or k > n:
        return 0
    result = 1
    for i in range(n, n - k, -1):
        result *= i
    return result


# ============================================================
# 5. PROBABILITY DISTRIBUTIONS
# ============================================================

def binomial_pmf(n, k, p):
    """
    Binomial Distribution PMF:
    P(X=k) = C(n,k) × p^k × (1-p)^(n-k)
    
    n: number of trials
    k: number of successes
    p: probability of success on each trial
    """
    if k < 0 or k > n:
        return 0
    return combination(n, k) * (p ** k) * ((1 - p) ** (n - k))


def binomial_cdf(n, k, p):
    """
    Binomial CDF: P(X <= k) = Σ P(X=i) for i=0 to k
    """
    return sum(binomial_pmf(n, i, p) for i in range(k + 1))


def binomial_mean(n, p):
    """Expected value of binomial: E(X) = n × p"""
    return n * p


def binomial_variance(n, p):
    """Variance of binomial: Var(X) = n × p × (1-p)"""
    return n * p * (1 - p)


def poisson_pmf(lam, k):
    """
    Poisson Distribution PMF:
    P(X=k) = (λ^k × e^(-λ)) / k!
    
    lam (λ): average rate (e.g., goals per match)
    k: number of events
    """
    if k < 0:
        return 0
    return (lam ** k * E ** (-lam)) / factorial(k)


def poisson_cdf(lam, k):
    """
    Poisson CDF: P(X <= k) = Σ P(X=i) for i=0 to k
    """
    return sum(poisson_pmf(lam, i) for i in range(k + 1))


def poisson_mean(lam):
    """Expected value of Poisson: E(X) = λ"""
    return lam


def poisson_variance(lam):
    """Variance of Poisson: Var(X) = λ"""
    return lam


def normal_pdf(x, mu, sigma):
    """
    Normal Distribution PDF:
    f(x) = (1 / (σ√(2π))) × e^(-(x-μ)² / (2σ²))
    """
    if sigma == 0:
        return 0
    coefficient = 1 / (sigma * math.sqrt(2 * PI))
    exponent = -((x - mu) ** 2) / (2 * sigma ** 2)
    return coefficient * (E ** exponent)


def normal_cdf(x, mu, sigma):
    """
    Normal CDF approximation using the error function approximation.
    Uses Abramowitz and Stegun approximation for erf.
    """
    if sigma == 0:
        return 1.0 if x >= mu else 0.0
    z = (x - mu) / (sigma * math.sqrt(2))
    return 0.5 * (1 + _erf_approx(z))


def _erf_approx(x):
    """
    Approximation of error function using Horner form.
    Abramowitz and Stegun formula 7.1.26
    Max error: 1.5 × 10^(-7)
    """
    sign = 1 if x >= 0 else -1
    x = abs(x)
    
    # Constants
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * (E ** (-x * x))
    
    return sign * y


def standard_normal_pdf(z):
    """Standard Normal PDF: μ=0, σ=1"""
    return normal_pdf(z, 0, 1)


def standard_normal_cdf(z):
    """Standard Normal CDF: μ=0, σ=1"""
    return normal_cdf(z, 0, 1)


# ============================================================
# 6. CORRELATION & REGRESSION
# ============================================================

def pearson_correlation(x_data, y_data):
    # Calculate Pearson correlation
    if len(x_data) != len(y_data) or len(x_data) < 2:
        return 0
    
    x_mean = mean(x_data)
    y_mean = mean(y_data)
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data))
    denom_x = sum((x - x_mean) ** 2 for x in x_data)
    denom_y = sum((y - y_mean) ** 2 for y in y_data)
    
    denominator = math.sqrt(denom_x * denom_y)
    
    if denominator == 0:
        return 0
    
    return numerator / denominator


def covariance(x_data, y_data):
    """
    Covariance: cov(X,Y) = Σ(xi - x̄)(yi - ȳ) / n
    """
    if len(x_data) != len(y_data) or not x_data:
        return 0
    x_mean = mean(x_data)
    y_mean = mean(y_data)
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data)) / len(x_data)


def linear_regression(x_data, y_data):
    # Calculate linear regression
    if len(x_data) != len(y_data) or len(x_data) < 2:
        return (0, 0, 0)
    
    x_mean = mean(x_data)
    y_mean = mean(y_data)
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data))
    denominator = sum((x - x_mean) ** 2 for x in x_data)
    
    if denominator == 0:
        return (0, y_mean, 0)
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    # R-squared
    r = pearson_correlation(x_data, y_data)
    r_squared = r ** 2
    
    return (slope, intercept, r_squared)


def predict_linear(x, slope, intercept):
    """Predict y value using linear regression model"""
    return slope * x + intercept


# ============================================================
# 7. FOOTBALL-SPECIFIC ANALYTICS
# ============================================================

def goal_scoring_rate(goals, matches):
    """Goals per match"""
    if matches == 0:
        return 0
    return goals / matches


def shot_accuracy(shots_on_target, total_shots):
    """Shot accuracy percentage"""
    if total_shots == 0:
        return 0
    return (shots_on_target / total_shots) * 100


def shot_conversion_rate(goals, total_shots):
    """Goal conversion rate from shots"""
    if total_shots == 0:
        return 0
    return (goals / total_shots) * 100


def pass_accuracy(passes_completed, passes_attempted):
    """Pass completion rate"""
    if passes_attempted == 0:
        return 0
    return (passes_completed / passes_attempted) * 100


def goal_contribution(goals, assists, matches):
    """Goal contributions (G+A) per match"""
    if matches == 0:
        return 0
    return (goals + assists) / matches


def minutes_per_goal(minutes, goals):
    """Average minutes between goals"""
    if goals == 0:
        return float('inf')
    return minutes / goals


def minutes_per_goal_contribution(minutes, goals, assists):
    """Average minutes between goal contributions"""
    total = goals + assists
    if total == 0:
        return float('inf')
    return minutes / total


def defensive_actions_per_match(tackles, interceptions, matches):
    """Defensive actions per match"""
    if matches == 0:
        return 0
    return (tackles + interceptions) / matches


def discipline_score(yellow_cards, red_cards, matches):
    """Cards per match (lower is better)"""
    if matches == 0:
        return 0
    return (yellow_cards + red_cards * 3) / matches


# ============================================================
# 8. PREDICTION ENGINE
# ============================================================

def predict_goals_poisson(current_goals, matches_played, future_matches):
    """
    Predict probability of scoring k goals in future matches
    using Poisson distribution.
    
    Returns: dict of {goals: probability} for k=0 to 10
    """
    if matches_played == 0:
        return {k: 0 for k in range(11)}
    
    rate = current_goals / matches_played  # goals per match
    lam = rate * future_matches  # expected goals in future matches
    
    predictions = {}
    for k in range(11):
        predictions[k] = round(poisson_pmf(lam, k) * 100, 2)
    
    return predictions


def predict_performance_bayesian(prior_rating, observed_ratings):
    """
    Bayesian update for player performance rating.
    
    Uses conjugate prior (normal-normal) for simplicity:
    posterior_mean = (prior_precision * prior_mean + n * sample_precision * sample_mean) 
                     / (prior_precision + n * sample_precision)
    
    Returns: (posterior_mean, posterior_std)
    """
    if not observed_ratings:
        return (prior_rating, 1.0)
    
    # Prior parameters
    prior_mean = prior_rating
    prior_precision = 1.0  # 1/variance
    
    # Observed data
    n = len(observed_ratings)
    sample_mean = mean(observed_ratings)
    sample_var = variance(observed_ratings) if n > 1 else 1.0
    sample_precision = 1.0 / max(sample_var, 0.01)
    
    # Posterior parameters
    posterior_precision = prior_precision + n * sample_precision
    posterior_mean = (prior_precision * prior_mean + n * sample_precision * sample_mean) / posterior_precision
    posterior_std = math.sqrt(1.0 / posterior_precision)
    
    return (round(posterior_mean, 2), round(posterior_std, 2))


def predict_binomial_success(successes, trials, future_trials, target_successes):
    """
    Predict probability of achieving target_successes in future_trials
    using binomial distribution.
    
    p estimated from historical data.
    """
    if trials == 0:
        return 0
    p = successes / trials
    return round(binomial_pmf(future_trials, target_successes, p) * 100, 2)


def predict_season_goals(current_goals, matches_played, total_matches=38):
    # Predict end-of-season goals
    if matches_played == 0:
        return 0
    rate = current_goals / matches_played
    return round(rate * total_matches, 1)


def player_composite_score(player_data):
    """
    Calculate a weighted composite performance score (0-100).
    
    Weights by position:
    FWD: Goals(30%), Assists(15%), Shot Accuracy(15%), Rating(20%), G+A per match(20%)
    MID: Goals(15%), Assists(20%), Pass Accuracy(20%), Rating(20%), Tackles(10%), Dribbles(15%)
    DEF: Clean Sheets(25%), Tackles(20%), Interceptions(15%), Pass Accuracy(15%), Rating(25%)
    GK:  Clean Sheets(40%), Rating(35%), Pass Accuracy(25%)
    """
    pos = player_data.get('position', 'FWD')
    matches = player_data.get('matches_played', 1) or 1
    
    # Normalize values to 0-1 scale (approximate league maximums)
    goals_norm = min(player_data.get('goals', 0) / 30, 1)
    assists_norm = min(player_data.get('assists', 0) / 15, 1)
    rating_norm = min(player_data.get('rating', 0) / 10, 1)
    
    shots_ot = player_data.get('shots_on_target', 0)
    shots = player_data.get('shots', 1) or 1
    shot_acc_norm = shots_ot / shots
    
    passes_c = player_data.get('passes_completed', 0)
    passes_a = player_data.get('passes_attempted', 1) or 1
    pass_acc_norm = passes_c / passes_a
    
    tackles_norm = min(player_data.get('tackles', 0) / 70, 1)
    interceptions_norm = min(player_data.get('interceptions', 0) / 30, 1)
    clean_sheets_norm = min(player_data.get('clean_sheets', 0) / 20, 1)
    dribbles_norm = min(player_data.get('dribbles_completed', 0) / 60, 1)
    
    ga_per_match = (player_data.get('goals', 0) + player_data.get('assists', 0)) / matches
    ga_norm = min(ga_per_match / 1.5, 1)
    
    if pos == 'FWD':
        score = (goals_norm * 0.30 + assists_norm * 0.15 + shot_acc_norm * 0.15 +
                 rating_norm * 0.20 + ga_norm * 0.20)
    elif pos == 'MID':
        score = (goals_norm * 0.15 + assists_norm * 0.20 + pass_acc_norm * 0.20 +
                 rating_norm * 0.20 + tackles_norm * 0.10 + dribbles_norm * 0.15)
    elif pos == 'DEF':
        score = (clean_sheets_norm * 0.25 + tackles_norm * 0.20 + interceptions_norm * 0.15 +
                 pass_acc_norm * 0.15 + rating_norm * 0.25)
    elif pos == 'GK':
        score = (clean_sheets_norm * 0.40 + rating_norm * 0.35 + pass_acc_norm * 0.25)
    else:
        score = rating_norm
    
    return round(score * 100, 1)


def generate_distribution_data(data, dist_type='normal', bins=50):
    """
    Generate distribution curve data points for visualization.
    
    Returns list of (x, y) tuples.
    """
    if not data:
        return []
    
    m = mean(data)
    s = std_dev(data)
    
    if s == 0:
        s = 1
    
    if dist_type == 'normal':
        x_min = m - 4 * s
        x_max = m + 4 * s
        step = (x_max - x_min) / bins
        points = []
        x = x_min
        while x <= x_max:
            y = normal_pdf(x, m, s)
            points.append((round(x, 3), round(y, 6)))
            x += step
        return points
    
    elif dist_type == 'poisson':
        lam = m
        points = []
        for k in range(int(m + 4 * math.sqrt(max(m, 1))) + 1):
            y = poisson_pmf(lam, k)
            points.append((k, round(y, 6)))
        return points
    
    return []


# ============================================================
# 9. SUMMARY STATISTICS GENERATOR
# ============================================================

def full_summary(data):
    """Generate a complete statistical summary of a dataset"""
    if not data:
        return {}
    
    q1, q2, q3 = quartiles(data)
    
    return {
        'count': len(data),
        'mean': round(mean(data), 3),
        'median': round(median(data), 3),
        'mode': mode(data),
        'variance': round(variance(data), 3),
        'std_dev': round(std_dev(data), 3),
        'range': round(data_range(data), 3),
        'min': min(data),
        'max': max(data),
        'q1': round(q1, 3),
        'q2': round(q2, 3),
        'q3': round(q3, 3),
        'iqr': round(iqr(data), 3),
        'cv': round(coefficient_of_variation(data), 3),
        'skewness': round(skewness(data), 3),
    }
