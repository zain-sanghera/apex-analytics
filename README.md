# ⚽ Apex Analytics - Football Performance Analyzer

**Premier League 2024-25 Season Analysis with Statistical Predictions**

By **Team Goal Diggers**: Ibrahim · Zain · Aashir · Sitara · Abdullah

---

## 🎯 Features

- **📊 Dashboard** - League overview, top scorers, team stats
- **📋 Player Profile** - Detailed individual player analysis
- **⚔️ Compare** - Head-to-head player comparison with Bayesian probability
- **🔮 Predict** - Goal predictions using Poisson & Binomial distributions
- **📈 Rankings** - Sort players by any stat
- **📉 Correlations** - Statistical relationships between player stats

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript (Chart.js for visualizations)
- **Backend:** Python 3 (built-in libraries only)
- **Data:** CSV dataset with 500+ Premier League players
- **Statistics:** From-scratch implementations of Poisson, Binomial, Bayesian, Z-scores, etc.

---

## 🚀 Quick Start

### Local Development
```bash
# 1. Navigate to project
cd backupProject

# 2. Start Python server
python server.py

# 3. Open browser
# http://localhost:8000
```

### Deploy to Production
See [DEPLOY.md](DEPLOY.md) for free hosting options:
- **Render.com** (recommended)
- Railway.app
- Replit

---

## 📁 Project Structure

```
backupProject/
├── index.html              # Main app UI
├── server.py               # Python REST API & static server
├── data_loader.py          # CSV data loading & filtering
├── stats_engine.py         # Statistical calculations
├── requirements.txt        # Python dependencies (none!)
├── data/
│   └── players.csv         # 500+ player statistics
├── css/
│   └── style.css           # UI styling
├── js/
│   └── app.js              # Frontend logic & API calls
└── DEPLOY.md               # Deployment instructions
```

---

## 📊 API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/api/players` | Get all players (sortable, filterable) |
| `/api/player?name=X` | Get single player with analysis |
| `/api/compare?player1=X&player2=Y` | Compare two players |
| `/api/predict?name=X&matches=5` | Predict goals in next N matches |
| `/api/team?name=X` | Get team overview |
| `/api/rankings?field=goals` | Get top 10 by stat |
| `/api/distribution?field=goals` | Statistical distribution data |
| `/api/correlation?x=shots&y=goals` | Correlation between two fields |

---

## 🧮 Statistical Methods Used

- **Poisson Distribution** - Goal predictions
- **Binomial Distribution** - Probability scoring
- **Bayesian Inference** - Performance predictions
- **Z-Scores** - League normalization
- **Pearson Correlation** - Statistical relationships
- **Linear Regression** - Trend analysis
- **Percentile Ranking** - Performance tiers

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Python HTTP servers & REST APIs
- ✅ CORS & cross-origin requests
- ✅ Statistical analysis from scratch
- ✅ CSV data processing
- ✅ Production-ready code
- ✅ Responsive web design
- ✅ Free deployment strategies

---

## 📝 License

Open source - feel free to use and modify!

---

## 🙋 Support

Questions? Check the logs:
```bash
# Backend logs
python server.py

# Browser console
F12 → Console tab
```

**Happy analyzing!** ⚽
