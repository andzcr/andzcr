import requests
import datetime
from datetime import timedelta
import html
import base64

# --- CONFIGURARE ---
USERNAME = "andzcr"
# Link-ul RAW catre logo-ul tau (folosim raw pentru a lua bitii imaginii)
LOGO_URL = "https://raw.githubusercontent.com/andzcr/andzcr/main/logo.png"

def get_logo_base64():
    """
    Descarca logo-ul si il converteste in Base64 pentru a fi integrat
    direct in SVG. Asta rezolva problema cu imaginea care nu se incarca.
    """
    try:
        r = requests.get(LOGO_URL, timeout=10)
        if r.status_code == 200:
            # Convertim in string base64
            b64_data = base64.b64encode(r.content).decode('utf-8')
            return f"data:image/png;base64,{b64_data}"
    except:
        pass
    return "" # Returnam gol daca nu reusim

def get_data():
    try:
        # 1. Luam ultimul repo
        url = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&direction=desc"
        r = requests.get(url, timeout=10)
        if r.status_code != 200 or not r.json(): return None, None
        repo = r.json()[0]
        
        # 2. Luam ultimul commit SPECIFIC
        last_sha = requests.get(f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits", timeout=10).json()[0]['sha']
        c_url = f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits/{last_sha}"
        c = requests.get(c_url, timeout=10)
        commit = c.json() if c.status_code == 200 else None
        
        return repo, commit
    except:
        return None, None

def create_dashboard(repo, commit):
    if not repo: return

    # --- PREGATIRE DATE ---
    name = html.escape(repo['name'])
    desc = html.escape(repo['description']) if repo['description'] else "No description provided."
    if len(desc) > 55: desc = desc[:52] + "..."
    
    language = html.escape(repo['language']) if repo['language'] else "Dev"
    
    lines_edited = "0"
    action_verb = "Edited" # Default

    if commit:
        msg = commit['commit']['message'].split('\n')[0]
        
        # Logica: daca mesajul contine "removed", schimbam verbul
        if "removed" in msg.lower():
            action_verb = "Removed"
            
        if len(msg) > 40: msg = msg[:38] + "..."
        msg = html.escape(msg)
        
        if 'stats' in commit:
            total_lines = commit['stats']['total']
            lines_edited = f"{total_lines}"
    else:
        msg = "Initial setup"
    
    # Time Logic (UTC+2)
    now_ro = datetime.datetime.utcnow() + timedelta(hours=2)
    last_push_utc = datetime.datetime.strptime(repo['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
    last_push_ro = last_push_utc + timedelta(hours=2)
    
    diff_minutes = (now_ro - last_push_ro).total_seconds() / 60
    
    # --- LOGICA CULORI ---
    if diff_minutes < 45:
        # ACTIVE
        status_text = "ACTIVE"
        status_color = "#ffffff" 
        dot_color = "#58a6ff"    # GitHub Blue (Active)
        border_color = "#ffffff" # White Outline
    else:
        # INACTIVE
        status_text = "OFFLINE"
        status_color = "#ff4d4d" 
        dot_color = "#ff0000"    # Red Dot
        border_color = "#ff0000" # Red Outline

    current_time = now_ro.strftime("%H:%M")
    current_date = now_ro.strftime("%d %b")

    # Obtinem imaginea codata
    logo_href = get_logo_base64()

    # --- SVG GENERATOR ---
    svg = f"""
    <svg width="800" height="260" viewBox="0 0 800 260" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
      <defs>
        <style>
            .font-main {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
            .text-white {{ fill: #ffffff; }}
            .text-dim {{ fill: #8b949e; }}
            .text-status {{ fill: {status_color}; }}
            
            /* ANIMATII BORDER */
            @keyframes flowRight {{
                to {{ stroke-dashoffset: -1600; }}
            }}
            .border-anim-right {{
                fill: none;
                stroke: {border_color};
                stroke-width: 2;
                stroke-linecap: round;
                stroke-dasharray: 400, 1200; 
                stroke-dashoffset: 0;
                animation: flowRight 6s linear infinite;
                filter: drop-shadow(0 0 5px {border_color});
            }}

            @keyframes flowLeft {{
                to {{ stroke-dashoffset: -1000; }}
            }}
            .border-anim-left {{
                fill: none;
                stroke: {border_color};
                stroke-width: 2;
                stroke-linecap: round;
                stroke-dasharray: 250, 750;
                stroke-dashoffset: 0;
                animation: flowLeft 6s linear infinite;
                filter: drop-shadow(0 0 3px {border_color});
            }}
            
            /* Pulse Dot */
            @keyframes pulse {{
                0% {{ opacity: 1; r: 4; }}
                50% {{ opacity: 0.5; r: 6; }}
                100% {{ opacity: 1; r: 4; }}
            }}
            .pulse-dot {{ animation: pulse 2s infinite ease-in-out; }}
            
        </style>
        
        <linearGradient id="bg-grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#161b22;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#0d1117;stop-opacity:1" />
        </linearGradient>
      </defs>

      <g transform="translate(10, 10)">
          <rect x="2" y="2" width="226" height="236" rx="20" fill="url(#bg-grad)" stroke="#30363d" stroke-width="1" />
          <rect x="2" y="2" width="226" height="236" rx="20" class="border-anim-left" />
          
          <text x="115" y="110" text-anchor="middle" class="font-main text-white" font-size="48" font-weight="700">{current_time}</text>
          <text x="115" y="135" text-anchor="middle" class="font-main text-status" font-size="14" font-weight="600">{current_date}</text>
          
          <rect x="65" y="180" width="100" height="24" rx="12" fill="rgba(255,255,255,0.05)" />
          <circle cx="80" cy="192" r="4" fill="{dot_color}" class="pulse-dot" />
          <text x="95" y="196" class="font-main text-white" font-size="10" font-weight="600" letter-spacing="1">{status_text}</text>
      </g>

      <g transform="translate(260, 10)">
          <rect x="2" y="2" width="526" height="236" rx="20" fill="url(#bg-grad)" stroke="#30363d" stroke-width="1" />
          
          <image href="{logo_href}" x="300" y="13" height="210" opacity="0.08" />

          <rect x="2" y="2" width="526" height="236" rx="20" class="border-anim-right" />
          
          <text x="30" y="40" class="font-main text-dim" font-size="11" font-weight="600" letter-spacing="1">CURRENT FOCUS</text>
          
          <text x="500" y="40" text-anchor="end" class="font-main text-dim" font-size="11" font-family="monospace">{action_verb} {lines_edited} lines</text>
          
          <text x="30" y="90" class="font-main text-white" font-size="32" font-weight="800">{name}</text>
          <text x="30" y="120" class="font-main text-dim" font-size="14" width="450">{desc}</text>
          
          <line x1="30" y1="160" x2="500" y2="160" stroke="#30363d" stroke-width="1" />
          
          <g transform="translate(30, 180)">
             <rect width="4" height="30" rx="2" fill="{dot_color}" />
             <text x="12" y="12" class="font-main text-dim" font-size="10">LATEST COMMIT</text>
             <text x="12" y="26" class="font-main text-white" font-size="12" font-family="monospace">"{msg}"</text>
          </g>
          
          <g transform="translate(430, 185)">
             <text x="0" y="15" class="font-main text-status" font-size="12" font-weight="bold" text-anchor="end">{language}</text>
             <circle cx="10" cy="11" r="4" fill="{dot_color}" opacity="0.8" />
          </g>
      </g>
      
    </svg>
    """
    
    with open("dashboard_final.svg", "w", encoding="utf-8") as f:
        f.write(svg)

if __name__ == "__main__":
    r, c = get_data()
    create_dashboard(r, c)
