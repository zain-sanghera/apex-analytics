/*
  Apex Analytics - app.js
  Team: Goal Diggers (Ibrahim, Zain, Aashir, Sitara, Abdullah)

  Fixes:
  1. Navigation was broken — clicking sidebar items did nothing.
  2. Dashboard data was not loading — API calls were missing.
*/

// ─── Helper: shortcut like jQuery's $() but only for one element ───
function $(selector) {
  return document.querySelector(selector);
}

// ─── NAVIGATION ────────────────────────────────────────────────────
// When a nav item is clicked, hide all pages and show the right one.
function setupNavigation() {
  const navItems = document.querySelectorAll(".nav-item");

  navItems.forEach(function (item) {
    item.addEventListener("click", function () {
      // 1. Remove "active" from all nav items
      navItems.forEach(function (n) {
        n.classList.remove("active");
      });

      // 2. Add "active" to the clicked item
      item.classList.add("active");

      // 3. Hide all page sections
      document.querySelectorAll(".page-section").forEach(function (section) {
        section.classList.remove("active");
      });

      // 4. Show the matching page section
      var pageId = "page-" + item.getAttribute("data-page");
      var target = document.getElementById(pageId);
      if (target) {
        target.classList.add("active");
      }
    });
  });
}

// ─── API HELPERS ───────────────────────────────────────────────────
// Get the API base URL (works locally and in production)
function getApiBaseUrl() {
  // In production, use the current domain
  // In development, use localhost:8000
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  // Production: use current domain with same protocol
  return window.location.protocol + '//' + window.location.host;
}

// Simple fetch wrapper — calls our Python server and returns JSON.
async function apiFetch(endpoint) {
  try {
    var baseUrl = getApiBaseUrl();
    var response = await fetch(baseUrl + endpoint);
    if (!response.ok) {
      console.error("API error:", response.status, endpoint);
      return null;
    }
    return await response.json();
  } catch (err) {
    console.error("Could not reach server:", err);
    return null;
  }
}

// ─── DASHBOARD ─────────────────────────────────────────────────────
async function loadDashboard() {
  // Fetch all players from the API
  var data = await apiFetch("/api/players?sort=goals&order=desc");
  if (!data) return;

  var players = data.players;

  // --- Stat cards ---
  var totalGoals = players.reduce(function (sum, p) {
    return sum + (p.goals || 0);
  }, 0);
  var totalAssists = players.reduce(function (sum, p) {
    return sum + (p.assists || 0);
  }, 0);
  var avgRating =
    players.reduce(function (sum, p) {
      return sum + (p.rating || 0);
    }, 0) / (players.length || 1);

  $("#dash-total-players").textContent = players.length;
  $("#dash-total-goals").textContent = totalGoals;
  $("#dash-total-assists").textContent = totalAssists;
  $("#dash-avg-rating").textContent = avgRating.toFixed(2);

  // --- Top Scorers table ---
  var topScorers = players.slice(0, 10); // already sorted by goals desc
  var scorersBody = $("#dash-top-scorers");
  scorersBody.innerHTML = "";
  topScorers.forEach(function (p, i) {
    var row = document.createElement("tr");
    row.innerHTML =
      "<td>" +
      (i + 1) +
      "</td>" +
      '<td style="cursor:pointer;color:var(--accent-1)" onclick="goToProfile(\'' +
      p.name +
      "')\">" +
      p.name +
      "</td>" +
      "<td>" +
      p.team +
      "</td>" +
      "<td>" +
      p.position +
      "</td>" +
      "<td>" +
      p.goals +
      "</td>" +
      "<td>" +
      p.assists +
      "</td>" +
      "<td>" +
      p.rating +
      "</td>";
    scorersBody.appendChild(row);
  });

  // --- Top Assists table ---
  var byAssists = players.slice().sort(function (a, b) {
    return b.assists - a.assists;
  });
  var topAssists = byAssists.slice(0, 10);
  var assistsBody = $("#dash-top-assists");
  assistsBody.innerHTML = "";
  topAssists.forEach(function (p, i) {
    var row = document.createElement("tr");
    row.innerHTML =
      "<td>" +
      (i + 1) +
      "</td>" +
      '<td style="cursor:pointer;color:var(--accent-1)" onclick="goToProfile(\'' +
      p.name +
      "')\">" +
      p.name +
      "</td>" +
      "<td>" +
      p.team +
      "</td>" +
      "<td>" +
      p.assists +
      "</td>" +
      "<td>" +
      p.goals +
      "</td>" +
      "<td>" +
      p.rating +
      "</td>";
    assistsBody.appendChild(row);
  });

  // --- Bar chart using Canvas ---
  drawBarChart(topScorers);
}

// ─── SIMPLE BAR CHART ──────────────────────────────────────────────
function drawBarChart(players) {
  var canvas = document.getElementById("dash-chart");
  if (!canvas) return;
  var ctx = canvas.getContext("2d");

  var width = canvas.offsetWidth || 800;
  var height = canvas.height || 280;
  canvas.width = width;

  ctx.clearRect(0, 0, width, height);

  var maxGoals =
    Math.max.apply(
      null,
      players.map(function (p) {
        return p.goals;
      }),
    ) || 1;
  var barCount = players.length;
  var padding = 50;
  var barGap = 8;
  var barWidth = (width - padding * 2 - barGap * (barCount - 1)) / barCount;

  players.forEach(function (p, i) {
    var barHeight = (p.goals / maxGoals) * (height - 60);
    var x = padding + i * (barWidth + barGap);
    var y = height - 30 - barHeight;

    // Bar colour: teal gradient
    ctx.fillStyle = "#00d4aa";
    ctx.fillRect(x, y, barWidth, barHeight);

    // Goals number on top of bar
    ctx.fillStyle = "#ffffff";
    ctx.font = "11px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(p.goals, x + barWidth / 2, y - 4);

    // Player name below bar (shortened)
    var shortName = p.name.split(" ").pop(); // last name only
    ctx.fillStyle = "#a0aec0";
    ctx.font = "10px sans-serif";
    ctx.fillText(shortName, x + barWidth / 2, height - 10);
  });
}

// ─── PLAYERS TABLE DATA (from players.csv) ─────────────────────────
// All players: only name, team, position shown in the table.
var ALL_PLAYERS = [
  { name: "Erling Haaland", team: "Manchester City", position: "FWD" },
  { name: "Mohamed Salah", team: "Liverpool", position: "FWD" },
  { name: "Alexander Isak", team: "Newcastle United", position: "FWD" },
  { name: "Cole Palmer", team: "Chelsea", position: "MID" },
  { name: "Bukayo Saka", team: "Arsenal", position: "FWD" },
  { name: "Son Heung-min", team: "Tottenham", position: "FWD" },
  { name: "Ollie Watkins", team: "Aston Villa", position: "FWD" },
  { name: "Bryan Mbeumo", team: "Brentford", position: "FWD" },
  { name: "Dominic Solanke", team: "Tottenham", position: "FWD" },
  { name: "Nicolas Jackson", team: "Chelsea", position: "FWD" },
  { name: "Chris Wood", team: "Nottingham Forest", position: "FWD" },
  { name: "Matheus Cunha", team: "Wolverhampton", position: "FWD" },
  { name: "Jean-Philippe Mateta", team: "Crystal Palace", position: "FWD" },
  { name: "Yoane Wissa", team: "Brentford", position: "FWD" },
  { name: "Jarrod Bowen", team: "West Ham", position: "FWD" },
  { name: "Danny Welbeck", team: "Brighton", position: "FWD" },
  { name: "Kai Havertz", team: "Arsenal", position: "FWD" },
  { name: "Marcus Rashford", team: "Manchester United", position: "FWD" },
  { name: "Phil Foden", team: "Manchester City", position: "MID" },
  { name: "Bruno Fernandes", team: "Manchester United", position: "MID" },
  { name: "Martin Odegaard", team: "Arsenal", position: "MID" },
  { name: "Kevin De Bruyne", team: "Manchester City", position: "MID" },
  { name: "James Maddison", team: "Tottenham", position: "MID" },
  { name: "Eberechi Eze", team: "Crystal Palace", position: "MID" },
  { name: "Morgan Rogers", team: "Aston Villa", position: "MID" },
  { name: "Declan Rice", team: "Arsenal", position: "MID" },
  { name: "Moises Caicedo", team: "Chelsea", position: "MID" },
  { name: "Sandro Tonali", team: "Newcastle United", position: "MID" },
  { name: "Rodrigo Bentancur", team: "Tottenham", position: "MID" },
  { name: "Douglas Luiz", team: "Aston Villa", position: "MID" },
  { name: "Alexis Mac Allister", team: "Liverpool", position: "MID" },
  { name: "Ryan Gravenberch", team: "Liverpool", position: "MID" },
  { name: "Bernardo Silva", team: "Manchester City", position: "MID" },
  { name: "Noni Madueke", team: "Chelsea", position: "MID" },
  { name: "Pedro Neto", team: "Chelsea", position: "MID" },
  { name: "Anthony Gordon", team: "Newcastle United", position: "FWD" },
  { name: "Virgil van Dijk", team: "Liverpool", position: "DEF" },
  { name: "William Saliba", team: "Arsenal", position: "DEF" },
  { name: "Gabriel Magalhaes", team: "Arsenal", position: "DEF" },
  { name: "Josko Gvardiol", team: "Manchester City", position: "DEF" },
  { name: "Ruben Dias", team: "Manchester City", position: "DEF" },
  { name: "Lisandro Martinez", team: "Manchester United", position: "DEF" },
  { name: "Lewis Hall", team: "Newcastle United", position: "DEF" },
  { name: "Marc Cucurella", team: "Chelsea", position: "DEF" },
  { name: "Antonee Robinson", team: "Fulham", position: "DEF" },
  { name: "Pedro Porro", team: "Tottenham", position: "DEF" },
  { name: "Trent Alexander-Arnold", team: "Liverpool", position: "DEF" },
  { name: "Andrew Robertson", team: "Liverpool", position: "DEF" },
  { name: "Ben White", team: "Arsenal", position: "DEF" },
  { name: "Destiny Udogie", team: "Tottenham", position: "DEF" },
  { name: "Levi Colwill", team: "Chelsea", position: "DEF" },
  { name: "Ezri Konsa", team: "Aston Villa", position: "DEF" },
  { name: "Alisson Becker", team: "Liverpool", position: "GK" },
  { name: "Ederson", team: "Manchester City", position: "GK" },
  { name: "David Raya", team: "Arsenal", position: "GK" },
  { name: "Robert Sanchez", team: "Chelsea", position: "GK" },
  { name: "Andre Onana", team: "Manchester United", position: "GK" },
  { name: "Nick Pope", team: "Newcastle United", position: "GK" },
  { name: "Bernd Leno", team: "Fulham", position: "GK" },
  { name: "Alphonse Areola", team: "West Ham", position: "GK" },
  { name: "Mark Flekken", team: "Brentford", position: "GK" },
  { name: "Diogo Jota", team: "Liverpool", position: "FWD" },
  { name: "Luis Diaz", team: "Liverpool", position: "FWD" },
  { name: "Gabriel Jesus", team: "Arsenal", position: "FWD" },
  { name: "Brennan Johnson", team: "Tottenham", position: "FWD" },
  { name: "Callum Wilson", team: "Newcastle United", position: "FWD" },
  { name: "Leandro Trossard", team: "Arsenal", position: "FWD" },
  { name: "Hwang Hee-chan", team: "Wolverhampton", position: "FWD" },
  { name: "Evan Ferguson", team: "Brighton", position: "FWD" },
  { name: "Joao Pedro", team: "Brighton", position: "FWD" },
  { name: "Rodrigo Muniz", team: "Fulham", position: "FWD" },
  { name: "Raul Jimenez", team: "Fulham", position: "FWD" },
  { name: "Callum Hudson-Odoi", team: "Nottingham Forest", position: "FWD" },
  { name: "Morgan Gibbs-White", team: "Nottingham Forest", position: "MID" },
  { name: "Dwight McNeil", team: "Everton", position: "MID" },
  { name: "James Ward-Prowse", team: "West Ham", position: "MID" },
  { name: "Ilkay Gundogan", team: "Manchester City", position: "MID" },
  { name: "Amadou Onana", team: "Aston Villa", position: "MID" },
  { name: "Yves Bissouma", team: "Tottenham", position: "MID" },
  { name: "Lucas Paqueta", team: "West Ham", position: "MID" },
  { name: "Emile Smith Rowe", team: "Fulham", position: "MID" },
  { name: "Kaoru Mitoma", team: "Brighton", position: "MID" },
  { name: "Pervis Estupinan", team: "Brighton", position: "DEF" },
  { name: "Ola Aina", team: "Nottingham Forest", position: "DEF" },
  { name: "Murillo", team: "Nottingham Forest", position: "DEF" },
];

// Position badge colours matching the site's teal/dark palette
var POSITION_COLORS = {
  FWD: { bg: "#c0392b22", color: "#e74c3c" },
  MID: { bg: "#2980b922", color: "#3498db" },
  DEF: { bg: "#27ae6022", color: "#2ecc71" },
  GK: { bg: "#8e44ad22", color: "#9b59b6" },
};

// ─── BUILD PLAYERS TABLE IN PROFILE PAGE ───────────────────────────
// Called once on page load. Renders all players in a scrollable table.
function buildProfilePlayersTable() {
  var profileSection = document.getElementById("page-profile");
  if (!profileSection) return;

  // Don't add the table twice
  if (document.getElementById("profile-players-table-wrap")) return;

  // Create the wrapper div (scrollable, max height)
  var wrap = document.createElement("div");
  wrap.id = "profile-players-table-wrap";
  wrap.style.cssText =
    "margin-top: 24px;" +
    "border-radius: 12px;" +
    "overflow: hidden;" +
    "border: 1px solid var(--border, #2d3748);";

  // Scrollable inner container
  var scrollBox = document.createElement("div");
  scrollBox.style.cssText = "max-height: 340px;" + "overflow-y: auto;";

  // Table
  var table = document.createElement("table");
  table.style.cssText = "width:100%; border-collapse: collapse;";

  // Sticky header so column titles stay visible while scrolling
  var thead = document.createElement("thead");
  thead.style.cssText = "position: sticky; top: 0; z-index: 2;";
  thead.innerHTML =
    "<tr>" +
    '<th style="text-align:left; padding: 12px 16px;">#</th>' +
    '<th style="text-align:left; padding: 12px 16px;">Player</th>' +
    '<th style="text-align:left; padding: 12px 16px;">Team</th>' +
    '<th style="text-align:left; padding: 12px 16px;">Position</th>' +
    "</tr>";

  var tbody = document.createElement("tbody");

  ALL_PLAYERS.forEach(function (player, index) {
    var row = document.createElement("tr");
    var posStyle = POSITION_COLORS[player.position] || {
      bg: "#ffffff11",
      color: "#aaa",
    };

    // Hover highlight effect
    row.style.cssText = "cursor: pointer; transition: background 0.15s;";
    row.addEventListener("mouseenter", function () {
      row.style.background = "rgba(0, 212, 170, 0.08)";
    });
    row.addEventListener("mouseleave", function () {
      row.style.background = "";
    });

    // Clicking a row: show analysis above, scroll table into view stays put
    row.addEventListener("click", function () {
      // Highlight selected row
      document
        .querySelectorAll("#profile-players-table-wrap tr")
        .forEach(function (r) {
          r.style.background = "";
        });
      row.style.background = "rgba(0, 212, 170, 0.15)";

      // Trigger analysis
      viewPlayer(player.name);

      // Scroll the analysis panel into view smoothly
      var profileContent = document.getElementById("profile-content");
      if (profileContent) {
        profileContent.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });

    row.innerHTML =
      '<td style="padding: 10px 16px; color: var(--text-muted, #a0aec0); font-size: 13px;">' +
      (index + 1) +
      "</td>" +
      '<td style="padding: 10px 16px; font-weight: 500;">' +
      player.name +
      "</td>" +
      '<td style="padding: 10px 16px; color: var(--text-muted, #a0aec0);">' +
      player.team +
      "</td>" +
      '<td style="padding: 10px 16px;">' +
      '<span style="' +
      "background:" +
      posStyle.bg +
      ";" +
      "color:" +
      posStyle.color +
      ";" +
      "padding: 2px 10px;" +
      "border-radius: 999px;" +
      "font-size: 12px;" +
      "font-weight: 600;" +
      "letter-spacing: 0.04em;" +
      '">' +
      player.position +
      "</span>" +
      "</td>";

    tbody.appendChild(row);
  });

  table.appendChild(thead);
  table.appendChild(tbody);
  scrollBox.appendChild(table);
  wrap.appendChild(scrollBox);

  // Insert table AFTER the profile-content div (analysis shows above, table below)
  var profileContent = document.getElementById("profile-content");
  if (profileContent && profileContent.parentNode) {
    profileContent.parentNode.insertBefore(wrap, profileContent.nextSibling);
  }
}

// ─── PLAYER PROFILE ────────────────────────────────────────────────
// Navigate to profile page and show a player
function goToProfile(name) {
  // Activate the profile nav item
  document.querySelectorAll(".nav-item").forEach(function (n) {
    n.classList.remove("active");
  });
  document.querySelector('[data-page="profile"]').classList.add("active");

  // Show the profile page
  document.querySelectorAll(".page-section").forEach(function (s) {
    s.classList.remove("active");
  });
  $("#page-profile").classList.add("active");

  // Load the player
  viewPlayer(name);
}

async function viewPlayer(name) {
  if (!name || !name.trim()) return;
  $("#profile-search").value = name;

  var container = $("#profile-content");
  container.innerHTML = '<p style="color:var(--text-muted)">Loading...</p>';

  var data = await apiFetch("/api/player?name=" + encodeURIComponent(name));
  if (!data || data.error) {
    container.innerHTML =
      '<p style="color:#fc8181">Player not found. Try a different name.</p>';
    return;
  }

  var p = data.player;
  var a = data.analysis;

  // Z-score gauge bar: visual bar showing where player sits vs league average
  // Range is clamped to [-3, +3] standard deviations
  function zGaugeHTML(label, zVal) {
    var clamped = Math.max(-3, Math.min(3, zVal));
    var pct = ((clamped + 3) / 6) * 100;
    var color = zVal >= 0 ? "#00d4aa" : "#fc8181";
    var sign = zVal >= 0 ? "+" : "";
    return (
      '<div style="margin-bottom:14px;">' +
      '<div style="display:flex;justify-content:space-between;margin-bottom:4px;">' +
      '<span style="font-size:13px;color:var(--text-muted,#a0aec0);">' +
      label +
      "</span>" +
      '<span style="font-size:13px;font-weight:700;color:' +
      color +
      ';">' +
      sign +
      zVal +
      "</span>" +
      "</div>" +
      '<div style="position:relative;height:8px;background:rgba(255,255,255,0.08);border-radius:4px;">' +
      '<div style="position:absolute;left:50%;top:-2px;width:2px;height:12px;background:rgba(255,255,255,0.25);border-radius:1px;"></div>' +
      '<div style="position:absolute;height:8px;border-radius:4px;background:' +
      color +
      ";" +
      (zVal >= 0
        ? "left:50%;width:" + (pct - 50) + "%;"
        : "left:" + pct + "%;width:" + (50 - pct) + "%;") +
      '"></div>' +
      "</div>" +
      '<div style="display:flex;justify-content:space-between;margin-top:2px;">' +
      '<span style="font-size:10px;color:rgba(255,255,255,0.2);">-3s</span>' +
      '<span style="font-size:10px;color:rgba(255,255,255,0.2);">avg</span>' +
      '<span style="font-size:10px;color:rgba(255,255,255,0.2);">+3s</span>' +
      "</div>" +
      "</div>"
    );
  }

  container.innerHTML =
    // Section 1: Core stats
    '<div class="chart-container">' +
    '<div class="chart-title">👤 ' +
    p.name +
    " — " +
    p.team +
    " (" +
    p.position +
    ")</div>" +
    '<div class="stat-grid">' +
    statCard("Goals", p.goals) +
    statCard("Assists", p.assists) +
    statCard("Rating", p.rating) +
    statCard("Matches", p.matches_played) +
    statCard("Goals/Match", a.goals_per_match) +
    statCard("Shot Acc %", a.shot_accuracy) +
    statCard("Pass Acc %", a.pass_accuracy) +
    statCard("Composite Score", a.composite_score) +
    "</div>" +
    '<div class="stat-grid" style="margin-top:16px;">' +
    statCard("Season Goal Proj.", a.season_projection_goals) +
    statCard(
      "Mins per Goal",
      a.minutes_per_goal !== null ? a.minutes_per_goal : "---",
    ) +
    statCard("Def Actions/Match", a.defensive_actions_per_match) +
    statCard("Discipline Score", a.discipline_score) +
    "</div>" +
    "</div>" +
    // Section 2: Z-scores with visual gauge bars
    '<div class="chart-container" style="margin-top:20px;">' +
    '<div class="chart-title">📐 Z-Scores vs League Average</div>' +
    '<p style="font-size:12px;color:var(--text-muted,#a0aec0);margin-bottom:16px;">' +
    "How many standard deviations above or below the league average this player is. " +
    "Centre line = league average. Green = above average, Red = below average." +
    "</p>" +
    zGaugeHTML("Goals Z-Score", a.z_score_goals) +
    zGaugeHTML("Assists Z-Score", a.z_score_assists) +
    zGaugeHTML("Rating Z-Score", a.z_score_rating) +
    '<div class="stat-grid" style="margin-top:16px;">' +
    statCard("Goals Percentile", a.percentile_goals + "%") +
    statCard("Assists Percentile", a.percentile_assists + "%") +
    statCard("Rating Percentile", a.percentile_rating + "%") +
    "</div>" +
    "</div>";
}

// ─── COMPARE ───────────────────────────────────────────────────────
async function doCompare() {
  var name1 = $("#compare-p1").value.trim();
  var name2 = $("#compare-p2").value.trim();
  if (!name1 || !name2) {
    $("#compare-result").innerHTML =
      '<p style="color:#fc8181">Please enter both player names.</p>';
    return;
  }

  $("#compare-result").innerHTML =
    '<p style="color:var(--text-muted)">Loading...</p>';

  var data = await apiFetch(
    "/api/compare?player1=" +
      encodeURIComponent(name1) +
      "&player2=" +
      encodeURIComponent(name2),
  );
  if (!data || data.error) {
    $("#compare-result").innerHTML =
      '<p style="color:#fc8181">One or both players not found.</p>';
    return;
  }

  var p1 = data.player1,
    a1 = data.analysis1;
  var p2 = data.player2,
    a2 = data.analysis2;

  // Build a simple side-by-side comparison table
  var fields = [
    ["Goals", "goals"],
    ["Assists", "assists"],
    ["Rating", "rating"],
    ["Matches", "matches_played"],
  ];

  var rows = fields
    .map(function (f) {
      var label = f[0],
        key = f[1];
      var v1 = p1[key],
        v2 = p2[key];
      var better1 = v1 > v2 ? "color:#00d4aa" : "";
      var better2 = v2 > v1 ? "color:#00d4aa" : "";
      return (
        "<tr>" +
        '<td style="' +
        better1 +
        '">' +
        v1 +
        "</td>" +
        '<td style="text-align:center;color:var(--text-muted)">' +
        label +
        "</td>" +
        '<td style="' +
        better2 +
        '">' +
        v2 +
        "</td>" +
        "</tr>"
      );
    })
    .join("");

  var analysisFields = [
    ["Goals/Match", "goals_per_match"],
    ["Shot Acc %", "shot_accuracy"],
    ["Pass Acc %", "pass_accuracy"],
    ["Composite Score", "composite_score"],
  ];

  var aRows = analysisFields
    .map(function (f) {
      var label = f[0],
        key = f[1];
      var v1 = a1[key],
        v2 = a2[key];
      var better1 = v1 > v2 ? "color:#00d4aa" : "";
      var better2 = v2 > v1 ? "color:#00d4aa" : "";
      return (
        "<tr>" +
        '<td style="' +
        better1 +
        '">' +
        v1 +
        "</td>" +
        '<td style="text-align:center;color:var(--text-muted)">' +
        label +
        "</td>" +
        '<td style="' +
        better2 +
        '">' +
        v2 +
        "</td>" +
        "</tr>"
      );
    })
    .join("");

  $("#compare-result").innerHTML =
    '<div class="chart-container">' +
    '<div class="chart-title">⚔️ ' +
    p1.name +
    " vs " +
    p2.name +
    "</div>" +
    "<table>" +
    "<thead><tr><th>" +
    p1.name +
    "</th><th>Stat</th><th>" +
    p2.name +
    "</th></tr></thead>" +
    "<tbody>" +
    rows +
    aRows +
    "</tbody>" +
    "</table>" +
    '<p style="margin-top:16px;color:var(--text-muted);font-size:13px">🟢 Green = better value</p>' +
    "</div>";
}

// ─── PREDICT ───────────────────────────────────────────────────────
async function doPredict() {
  var name = $("#predict-player").value.trim();
  var matches = $("#predict-matches").value;
  if (!name) {
    $("#predict-result").innerHTML =
      '<p style="color:#fc8181">Please enter a player name.</p>';
    return;
  }

  $("#predict-result").innerHTML =
    '<p style="color:var(--text-muted)">Loading...</p>';

  // Fetch prediction data AND normal distribution data for goals in parallel
  var predData = await apiFetch(
    "/api/predict?name=" + encodeURIComponent(name) + "&matches=" + matches,
  );
  var distData = await apiFetch("/api/distribution?field=goals&type=normal");
  var poisData = await apiFetch("/api/distribution?field=goals&type=poisson");

  if (!predData || predData.error) {
    $("#predict-result").innerHTML =
      '<p style="color:#fc8181">Player not found.</p>';
    return;
  }

  var p = predData.player;
  var b = predData.binomial;

  // Render the stat cards + two canvas placeholders first
  $("#predict-result").innerHTML =
    '<div class="chart-container">' +
    '<div class="chart-title">🔮 ' +
    p.name +
    " — Next " +
    predData.future_matches +
    " Matches</div>" +
    '<div class="stat-grid">' +
    statCard("Expected Goals", predData.expected_goals) +
    statCard("Season Goal Projection", predData.season_projection.goals) +
    statCard("Season Assist Projection", predData.season_projection.assists) +
    statCard("P(Score At Least Once) %", b.prob_score_at_least_one) +
    statCard("P(Score Every Match) %", b.prob_score_all_matches) +
    statCard("P(Score None) %", b.prob_score_no_match) +
    "</div>" +
    "</div>" +
    // Normal Distribution chart
    '<div class="chart-container" style="margin-top:20px;">' +
    '<div class="chart-title">📈 Normal Distribution — League Goals</div>' +
    '<p style="font-size:12px;color:var(--text-muted,#a0aec0);margin-bottom:12px;">' +
    "The bell curve shows how goals are spread across all league players. " +
    "The teal line marks where <strong>" +
    p.name +
    "</strong> sits." +
    "</p>" +
    '<canvas id="dist-normal-canvas" height="200" style="width:100%;"></canvas>' +
    "</div>" +
    // Poisson Distribution chart
    '<div class="chart-container" style="margin-top:20px;">' +
    '<div class="chart-title">🎲 Poisson Distribution — Predicted Goals Next ' +
    predData.future_matches +
    " Matches</div>" +
    '<p style="font-size:12px;color:var(--text-muted,#a0aec0);margin-bottom:12px;">' +
    "Probability of scoring exactly k goals in the next " +
    predData.future_matches +
    " matches, " +
    "based on " +
    p.name +
    "'s current scoring rate." +
    "</p>" +
    '<canvas id="dist-poisson-canvas" height="200" style="width:100%;"></canvas>' +
    "</div>";

  // Draw both charts after the DOM has updated
  setTimeout(function () {
    if (distData && distData.curve) {
      drawNormalCurve(
        "dist-normal-canvas",
        distData.curve,
        p.goals,
        distData.summary,
      );
    }
    if (predData.poisson_goals) {
      drawPoissonBars("dist-poisson-canvas", predData.poisson_goals);
    }
  }, 50);
}

// ── Draw Normal distribution curve on a canvas ─────────────────────
// curve: array of [x, y] pairs from the API
// playerGoals: the player's actual goals value (to draw the marker line)
// summary: { mean, std_dev } from the API
function drawNormalCurve(canvasId, curve, playerGoals, summary) {
  var canvas = document.getElementById(canvasId);
  if (!canvas) return;
  var ctx = canvas.getContext("2d");
  var W = canvas.offsetWidth || 700;
  var H = canvas.height || 200;
  canvas.width = W;

  var PAD_L = 40,
    PAD_R = 20,
    PAD_T = 20,
    PAD_B = 35;
  var plotW = W - PAD_L - PAD_R;
  var plotH = H - PAD_T - PAD_B;

  ctx.clearRect(0, 0, W, H);

  // Find data range
  var xMin = curve[0][0],
    xMax = curve[curve.length - 1][0];
  var yMax = Math.max.apply(
    null,
    curve.map(function (pt) {
      return pt[1];
    }),
  );

  function toCanvasX(x) {
    return PAD_L + ((x - xMin) / (xMax - xMin)) * plotW;
  }
  function toCanvasY(y) {
    return PAD_T + plotH - (y / yMax) * plotH;
  }

  // Draw filled area under curve
  ctx.beginPath();
  ctx.moveTo(toCanvasX(xMin), PAD_T + plotH);
  curve.forEach(function (pt) {
    ctx.lineTo(toCanvasX(pt[0]), toCanvasY(pt[1]));
  });
  ctx.lineTo(toCanvasX(xMax), PAD_T + plotH);
  ctx.closePath();
  ctx.fillStyle = "rgba(0, 212, 170, 0.12)";
  ctx.fill();

  // Draw curve line
  ctx.beginPath();
  curve.forEach(function (pt, i) {
    if (i === 0) ctx.moveTo(toCanvasX(pt[0]), toCanvasY(pt[1]));
    else ctx.lineTo(toCanvasX(pt[0]), toCanvasY(pt[1]));
  });
  ctx.strokeStyle = "#00d4aa";
  ctx.lineWidth = 2;
  ctx.stroke();

  // Draw mean line
  if (summary && summary.mean !== undefined) {
    var mx = toCanvasX(summary.mean);
    ctx.beginPath();
    ctx.moveTo(mx, PAD_T);
    ctx.lineTo(mx, PAD_T + plotH);
    ctx.strokeStyle = "rgba(255,255,255,0.2)";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "rgba(255,255,255,0.3)";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("avg", mx, PAD_T + plotH + 14);
  }

  // Draw player marker line (teal, solid)
  if (playerGoals >= xMin && playerGoals <= xMax) {
    var px = toCanvasX(playerGoals);
    ctx.beginPath();
    ctx.moveTo(px, PAD_T);
    ctx.lineTo(px, PAD_T + plotH);
    ctx.strokeStyle = "#00d4aa";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = "#00d4aa";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("player", px, PAD_T - 6);
  }

  // X-axis labels
  ctx.fillStyle = "rgba(255,255,255,0.3)";
  ctx.font = "10px sans-serif";
  ctx.textAlign = "center";
  [xMin, (xMin + xMax) / 2, xMax].forEach(function (v) {
    ctx.fillText(Math.round(v), toCanvasX(v), PAD_T + plotH + 26);
  });

  // Axis label
  ctx.fillStyle = "rgba(255,255,255,0.2)";
  ctx.fillText("Goals", PAD_L + plotW / 2, H - 2);
}

// ── Draw Poisson PMF bar chart on a canvas ─────────────────────────
// poissonGoals: object { "0": prob%, "1": prob%, ... } from API
function drawPoissonBars(canvasId, poissonGoals) {
  var canvas = document.getElementById(canvasId);
  if (!canvas) return;
  var ctx = canvas.getContext("2d");
  var W = canvas.offsetWidth || 700;
  var H = canvas.height || 200;
  canvas.width = W;

  var PAD_L = 40,
    PAD_R = 20,
    PAD_T = 20,
    PAD_B = 35;
  var plotW = W - PAD_L - PAD_R;
  var plotH = H - PAD_T - PAD_B;

  ctx.clearRect(0, 0, W, H);

  // Convert object to sorted array, drop trailing zero-probability entries
  var keys = Object.keys(poissonGoals)
    .map(Number)
    .sort(function (a, b) {
      return a - b;
    });
  // Keep only entries up to where probability drops to near 0
  while (keys.length > 1 && poissonGoals[keys[keys.length - 1]] < 0.1) {
    keys.pop();
  }

  var values = keys.map(function (k) {
    return poissonGoals[k];
  });
  var yMax = Math.max.apply(null, values) || 1;
  var barCount = keys.length;
  var barGap = 6;
  var barWidth = (plotW - barGap * (barCount - 1)) / barCount;

  keys.forEach(function (k, i) {
    var val = poissonGoals[k];
    var barH = (val / yMax) * plotH;
    var x = PAD_L + i * (barWidth + barGap);
    var y = PAD_T + plotH - barH;

    // Bar fill
    ctx.fillStyle = "#00d4aa";
    ctx.globalAlpha = 0.75;
    ctx.fillRect(x, y, barWidth, barH);
    ctx.globalAlpha = 1;

    // Probability % on top of bar (only if tall enough)
    if (barH > 16) {
      ctx.fillStyle = "#ffffff";
      ctx.font = "9px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(val.toFixed(1) + "%", x + barWidth / 2, y - 3);
    }

    // k value label below bar
    ctx.fillStyle = "rgba(255,255,255,0.35)";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(k, x + barWidth / 2, PAD_T + plotH + 14);
  });

  // Axis labels
  ctx.fillStyle = "rgba(255,255,255,0.2)";
  ctx.font = "10px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("Goals scored (k)", PAD_L + plotW / 2, H - 2);
}

// ─── UTILITY: stat card HTML ───────────────────────────────────────
function statCard(label, value) {
  return (
    '<div class="card">' +
    '<div class="card-title">' +
    label +
    "</div>" +
    '<div class="card-value">' +
    (value !== null && value !== undefined ? value : "—") +
    "</div>" +
    "</div>"
  );
}

// ─── INIT: run everything when the page loads ──────────────────────
document.addEventListener("DOMContentLoaded", function () {
  setupNavigation(); // Fix: wire up sidebar clicks
  loadDashboard(); // Fix: load data into the dashboard
  buildProfilePlayersTable(); // Add players table to Profile tab
});
