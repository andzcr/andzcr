import requests
import datetime
from datetime import timedelta

# CONFIGURARE
USERNAME = "andzcr"
# Link-ul RAW catre logo-ul tau (important: raw, nu blob)
LOGO_URL = "https://raw.githubusercontent.com/andzcr/andzcr.github.io/resources/photos/andz-logo.png"

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
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def create_ultimate_card(repo, commit):
    if not repo: return

    # --- DATA PROCESSING ---
    name = repo['name']
    language = repo['language'] if repo['language'] else "Unknown Language"
    
    if commit:
        msg = commit['commit']['message'].split('\n')[0]
        # Trunchiem inteligent mesajul
        if len(msg) > 50: msg = msg[:48] + "..."
        author_name = commit['commit']['author']['name']
    else:
        msg = "Initial repository setup or no commit history available."
        author_name = USERNAME

    # Time Logic (Romania UTC+2)
    last_push_utc = datetime.datetime.strptime(repo['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
    last_push_ro = last_push_utc + timedelta(hours=2)
    now_ro = datetime.datetime.utcnow() + timedelta(hours=2)
    
    minutes_diff = (now_ro - last_push_ro).total_seconds() / 60
    
    # STATUS LOGIC (45 min window)
    if minutes_diff < 45:
        is_online = True
        status_text = "Active Session"
        # Verde neon Apple
        status_color = "#32d74b" 
        status_sub = "Working now"
        # Animatie de pulsare doar cand e online
        pulse_anim = """<animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite" />
                        <animate attributeName="opacity" values="1;0.6;1" dur="2s" repeatCount="indefinite" />"""
    else:
        is_online = False
        time_str = last_push_ro.strftime("%H:%M")
        status_text = "System Idle"
        # Gri neutru
        status_color = "#86868b"
        status_sub = f"Last seen {time_str}"
        pulse_anim = ""

    last_date_nice = last_push_ro.strftime("%d %B")

    # --- ULTIMATE SVG DESIGN ---
    svg = f"""
    <svg width="500" height="260" viewBox="0 0 500 260" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
      <defs>
        <style>
            .sf {{ font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
            .mono {{ font-family: 'SF Mono', 'Fira Code', Consolas, monospace; letter-spacing: -0.5px; }}
            
            /* Text Colors */
            .t-white {{ fill: #ffffff; }}
            .t-grey-light {{ fill: rgba(235, 235, 245, 0.6); }}
            .t-grey-dark {{ fill: rgba(235, 235, 245, 0.4); }}
            .t-accent {{ fill: #0a84ff; }}
        </style>
        
        <linearGradient id="bg-dark" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#292a2d;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1c1c1e;stop-opacity:1" />
        </linearGradient>
        
        <linearGradient id="glass-rim" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:rgba(255,255,255,0.15);"/>
            <stop offset="100%" style="stop-color:rgba(255,255,255,0.0);"/>
        </linearGradient>

        <filter id="f1" x="-10%" y="-10%" width="120%" height="120%">
            <feOffset result="offOut" in="SourceAlpha" dx="0" dy="6" />
            <feGaussianBlur result="blurOut" in="offOut" stdDeviation="6" />
            <feBlend in="SourceGraphic" in2="blurOut" mode="normal" />
        </filter>
        
        <clipPath id="round-logo"><circle cx="40" cy="40" r="16" /></clipPath>
      </defs>

      <g filter="url(#f1)">
          <rect x="10" y="10" width="480" height="240" rx="24" fill="url(#bg-dark)" stroke="rgba(0,0,0,0.5)" stroke-width="1"/>
          <rect x="11" y="11" width="478" height="238" rx="23" fill="url(#glass-rim)" stroke="rgba(255,255,255,0.1)" stroke-width="1.5"/>
      </g>
      
      <image x="24" y="24" width="32" height="32" xlink:href="{LOGO_URL}" clip-path="url(#round-logo)"/>
      
      <g transform="translate(450, 40)">
          <text x="-15" y="0" text-anchor="end" class="sf t-white" font-size="13" font-weight="600">{status_text}</text>
          <text x="-15" y="14" text-anchor="end" class="sf t-grey-dark" font-size="11">{status_sub}</text>
          <circle cx="5" cy="5" r="5" fill="{status_color}">
              {pulse_anim}
          </circle>
      </g>
      
      <line x1="30" y1="70" x2="470" y2="70" stroke="rgba(255,255,255,0.08)" />


      <g transform="translate(35, 105)">
          <text class="sf t-grey-dark" font-size="11" font-weight="600" letter-spacing="0.8">CURRENT FOCUS</text>
          
          <text y="28" class="sf t-white" font-size="26" font-weight="700" letter-spacing="-0.5">{name}</text>
          
          <g transform="translate(0, 45)">
              <rect width="430" height="42" rx="10" fill="rgba(0,0,0,0.2)" stroke="rgba(255,255,255,0.08)"/>
              <path d="M15,26 C15,26 25,16 25,16 C28.3137,12.6863 28.3137,7.31371 25,4 C21.6863,0.686292 16.3137,0.686292 13,4 C13,4 8.87,8.13 8.87,8.13 C6.96,7.39 4.81,7.79 3.29,9.31 C1.34,11.26 1.34,14.42 3.29,16.37 C3.56,16.64 3.85,16.87 4.15,17.08 L5.29,21.08 L9.46,22.29 C9.66,22.59 9.89,22.88 10.16,23.15 C11.69,24.67 13.91,25.06 15.84,24.29 L15,26 Z M16.41,5.41 C18.75,3.07 22.55,3.07 24.89,5.41 C27.23,7.75 27.23,11.55 24.89,13.89 C24.89,13.89 15.06,23.72 15.06,23.72 C13.45,25.33 10.83,25.33 9.22,23.72 C7.61,22.11 7.61,19.49 9.22,17.88 L14.81,12.29 L12.29,9.77 L6.7,15.36 C5.09,16.97 2.47,16.97 0.86,15.36 C-0.75,13.75 -0.75,11.13 0.86,9.52 C2.47,7.91 5.09,7.91 6.7,9.52 L16.41,5.41 Z" transform="translate(10,9) scale(0.6)" fill="#f34f29"/>
              
              <text x="32" y="25" class="mono t-grey-light" font-size="12">
                <tspan fill="#f34f29">Wait, </tspan>{author_name}: <tspan class="t-white">"{msg}"</tspan>
              </text>
          </g>
      </g>

      <g transform="translate(35, 225)">
          <rect x="0" y="-16" width="auto" height="22" rx="6" fill="rgba(10, 132, 255, 0.15)" stroke="rgba(10, 132, 255, 0.3)"/>
          <rect x="0" y="-16" width="{len(language)*7 + 20}" height="22" rx="6" fill="rgba(10, 132, 255, 0.15)" stroke="rgba(10, 132, 255, 0.3)"/>
          <text x="{len(language)*3.5 + 10}" y="0" class="sf t-accent" font-size="11" font-weight="700" text-anchor="middle">{language}</text>
          
          <text x="160" y="0" class="sf t-grey-dark" font-size="11">Last update: {last_date_nice}</text>
          
          <text x="450" y="0" text-anchor="end" class="sf t-grey-dark" font-size="10" font-weight="600" letter-spacing="1"> andzOS System Bot</text>
      </g>

    </svg>
    """
    
    # Salvam ca 'andz_os_card.svg' pentru noul branding
    with open("andz_os_card.svg", "w", encoding="utf-8") as f:
        f.write(svg)

if __name__ == "__main__":
    r, c = get_data()
    create_ultimate_card(r, c)
