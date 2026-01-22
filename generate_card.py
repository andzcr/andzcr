import requests
import datetime
from datetime import timedelta
import html

# --- CONFIGURARE ---
USERNAME = "andzcr"

def get_data():
    try:
        # 1. Repo info
        url = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&direction=desc"
        r = requests.get(url, timeout=10)
        if r.status_code != 200 or not r.json(): return None, None
        repo = r.json()[0]
        
        # 2. Commit info
        c_url = f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits"
        c = requests.get(c_url, timeout=10)
        commit = c.json()[0] if c.status_code == 200 and c.json() else None
        return repo, commit
    except:
        return None, None

def create_flow_dashboard(repo, commit):
    if not repo: return

    # --- DATA PROCESSING ---
    name = html.escape(repo['name'])
    desc = html.escape(repo['description']) if repo['description'] else "No description provided."
    if len(desc) > 55: desc = desc[:52] + "..."
    
    language = html.escape(repo['language']) if repo['language'] else "Dev"
    
    if commit:
        msg = commit['commit']['message'].split('\n')[0]
        if len(msg) > 40: msg = msg[:38] + "..."
        msg = html.escape(msg)
        sha = commit['sha'][:7]
    else:
        msg = "Initial setup"
        sha = "INIT"

    # Time Logic (UTC+2 for RO)
    now_ro = datetime.datetime.utcnow() + timedelta(hours=2)
    last_push_utc = datetime.datetime.strptime(repo['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
    last_push_ro = last_push_utc + timedelta(hours=2)
    
    diff_minutes = (now_ro - last_push_ro).total_seconds() / 60
    
    # STATUS LOGIC
    if diff_minutes < 45:
        status_text = "ACTIVE"
        status_color = "#00ff88" # Neon Green
        pulse_animation = "pulse-green"
        border_gradient = "grad-online"
        status_sub = "Systems Online"
    else:
        status_text = "IDLE"
        status_color = "#bd00ff" # Neon Purple
        pulse_animation = "pulse-purple"
        border_gradient = "grad-offline"
        status_sub = f"Last seen {last_push_ro.strftime('%H:%M')}"

    current_time = now_ro.strftime("%H:%M")
    current_date = now_ro.strftime("%d %b")

    # SVG CONTENT
    svg = f"""
    <svg width="800" height="260" viewBox="0 0 800 260" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <style>
            .font-main {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
            .text-white {{ fill: #ffffff; }}
            .text-dim {{ fill: #8b949e; }}
            .text-accent {{ fill: {status_color}; }}
            
            /* ANIMATII */
            
            /* 1. Snake Border Animation */
            @keyframes flow {{
                to {{ stroke-dashoffset: 0; }}
            }}
            .snake-border {{
                fill: none;
                stroke-width: 2;
                stroke-linecap: round;
                stroke-dasharray: 200, 1000; /* Lungimea liniei vs spatiu gol */
                stroke-dashoffset: 1200;
                animation: flow 4s linear infinite;
            }}
            
            /* 2. Pulse Dot */
            @keyframes pulse {{
                0% {{ opacity: 1; r: 4; }}
                50% {{ opacity: 0.5; r: 7; }}
                100% {{ opacity: 1; r: 4; }}
            }}
            .pulse-dot {{ animation: pulse 2s infinite ease-in-out; }}
            
            /* 3. Text Fade In */
            @keyframes fadein {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            .fade {{ animation: fadein 1s ease-out forwards; }}
        </style>
        
        <linearGradient id="grad-online" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00ff88;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#0099ff;stop-opacity:1" />
        </linearGradient>
        
        <linearGradient id="grad-offline" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#bd00ff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ff0055;stop-opacity:1" />
        </linearGradient>

        <linearGradient id="bg-grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#161b22;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#0d1117;stop-opacity:1" />
        </linearGradient>
        
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
             <feGaussianBlur stdDeviation="3" result="blur"/>
             <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
      </defs>

      <g transform="translate(10, 10)">
          <rect x="2" y="2" width="226" height="236" rx="20" fill="url(#bg-grad)" stroke="#30363d" stroke-width="1" />
          
          <rect x="2" y="2" width="226" height="236" rx="20" stroke="url(#{border_gradient})" class="snake-border" filter="url(#glow)" />
          
          <text x="115" y="110" text-anchor="middle" class="font-main text-white" font-size="48" font-weight="700">{current_time}</text>
          <text x="115" y="135" text-anchor="middle" class="font-main text-accent" font-size="14" font-weight="600">{current_date}</text>
          
          <rect x="65" y="180" width="100" height="24" rx="12" fill="rgba(255,255,255,0.05)" />
          <circle cx="80" cy="192" r="4" fill="{status_color}" class="pulse-dot" />
          <text x="95" y="196" class="font-main text-white" font-size="10" font-weight="600" letter-spacing="1">{status_text}</text>
      </g>

      <g transform="translate(260, 10)">
          <rect x="2" y="2" width="526" height="236" rx="20" fill="url(#bg-grad)" stroke="#30363d" stroke-width="1" />
          
          <rect x="2" y="2" width="526" height="236" rx="20" stroke="url(#{border_gradient})" class="snake-border" style="animation-duration: 6s;" filter="url(#glow)" />
          
          <text x="30" y="40" class="font-main text-dim" font-size="11" font-weight="600" letter-spacing="1">CURRENT FOCUS</text>
          <text x="500" y="40" text-anchor="end" class="font-main text-dim" font-size="11" font-family="monospace">SHA: {sha}</text>
          
          <text x="30" y="90" class="font-main text-white fade" font-size="32" font-weight="800">{name}</text>
          
          <text x="30" y="120" class="font-main text-dim fade" font-size="14" width="450">{desc}</text>
          
          <line x1="30" y1="160" x2="500" y2="160" stroke="#30363d" stroke-width="1" />
          
          <g transform="translate(30, 180)">
             <rect width="6" height="30" rx="2" fill="{status_color}" />
             <text x="15" y="12" class="font-main text-dim" font-size="10">LATEST COMMIT</text>
             <text x="15" y="26" class="font-main text-white" font-size="12" font-family="monospace">"{msg}"</text>
          </g>
          
          <g transform="translate(430, 185)">
             <text x="0" y="15" class="font-main text-accent" font-size="12" font-weight="bold" text-anchor="end">{language}</text>
             <circle cx="10" cy="11" r="4" fill="{status_color}" opacity="0.8" />
          </g>
      </g>
      
    </svg>
    """
    
    with open("dashboard_final.svg", "w", encoding="utf-8") as f:
        f.write(svg)

if __name__ == "__main__":
    r, c = get_data()
    create_flow_dashboard(r, c)
