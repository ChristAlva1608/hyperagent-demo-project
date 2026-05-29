import streamlit as st

def inject_theme():
    """Injects the complete adaptive premium healthcare design system.
    
    Architecture:
    - CSS custom properties defined in :root (light mode defaults)
    - @media (prefers-color-scheme: dark) overrides tokens for OS dark mode (Safari/macOS)
    - [data-theme="dark"] targets Streamlit's own internal dark mode toggle
    - Both mechanisms are covered so the UI adapts in ALL dark mode scenarios
    """
    
    st.markdown(
        """
        <style>
        /* ============================================================
           FONTS
        ============================================================ */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');
        @import url('https://fonts.googleapis.com/icon?family=Material+Icons&display=block');

        /* ============================================================
           DESIGN TOKENS — LIGHT MODE (defaults)
        ============================================================ */
        :root {
            --bg-app:           #f0f4f8;
            --bg-surface:       #ffffff;
            --bg-surface-alt:   #f8fafc;

            --blue-950:         #0a1628;
            --blue-900:         #0f172a;
            --blue-800:         #1e3a5f;
            --blue-700:         #1d4ed8;
            --blue-600:         #2563eb;
            --blue-500:         #3b82f6;
            --blue-400:         #60a5fa;
            --blue-300:         #93c5fd;
            --blue-200:         #bfdbfe;
            --blue-100:         #dbeafe;
            --blue-50:          #eff6ff;

            --text-primary:     #0f172a;
            --text-secondary:   #475569;
            --text-muted:       #94a3b8;
            --text-inverse:     #ffffff;
            --text-accent:      #2563eb;

            --border-default:   #e2e8f0;
            --border-blue:      #bfdbfe;
            --border-focus:     #3b82f6;

            --success-bg:       #f0fdf4;
            --success-border:   #bbf7d0;
            --success-text:     #166534;
            --success-subtext:  #14532d;
            --error-bg:         #fef2f2;
            --error-border:     #fca5a5;
            --error-text:       #991b1b;
            --error-subtext:    #7f1d1d;
            --warning-bg:       #fffbeb;
            --warning-border:   #fde68a;
            --warning-text:     #92400e;

            --shadow-sm:        0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
            --shadow-md:        0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
            --shadow-lg:        0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.05);
            --shadow-blue:      0 4px 14px rgba(37,99,235,0.2);

            --header-bg:        linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);

            /* Badge helpers (hardcoded — always visible on their backgrounds) */
            --badge-green-text:   #14532d;
            --badge-green-bg:     #dcfce7;
            --badge-orange-text:  #92400e;
            --badge-orange-bg:    #fef3c7;
            --badge-red-text:     #991b1b;
            --badge-red-bg:       #fee2e2;
            --badge-blue-text:    #1e40af;
            --badge-blue-bg:      #dbeafe;
            --badge-gray-text:    #374151;
            --badge-gray-bg:      #f3f4f6;
        }

        /* ============================================================
           DARK MODE — OS level (Safari macOS prefers-color-scheme)
        ============================================================ */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-app:           #0d1117;
                --bg-surface:       #161b27;
                --bg-surface-alt:   #1a2035;

                --blue-700:         #2563eb;
                --blue-600:         #3b82f6;
                --blue-500:         #60a5fa;
                --blue-400:         #93c5fd;
                --blue-300:         #bfdbfe;
                --blue-200:         #dbeafe;
                --blue-100:         rgba(219,234,254,0.15);
                --blue-50:          rgba(239,246,255,0.07);

                --text-primary:     #e2e8f0;
                --text-secondary:   #94a3b8;
                --text-muted:       #64748b;
                --text-inverse:     #0f172a;
                --text-accent:      #60a5fa;

                --border-default:   rgba(255,255,255,0.09);
                --border-blue:      rgba(96,165,250,0.25);
                --border-focus:     #60a5fa;

                --success-bg:       rgba(20,83,45,0.25);
                --success-border:   rgba(34,197,94,0.35);
                --success-text:     #86efac;
                --success-subtext:  #bbf7d0;
                --error-bg:         rgba(127,29,29,0.25);
                --error-border:     rgba(239,68,68,0.35);
                --error-text:       #fca5a5;
                --error-subtext:    #fee2e2;
                --warning-bg:       rgba(120,53,15,0.25);
                --warning-border:   rgba(251,191,36,0.35);
                --warning-text:     #fcd34d;

                --shadow-sm:        0 1px 3px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.25);
                --shadow-md:        0 4px 6px -1px rgba(0,0,0,0.45), 0 2px 4px -1px rgba(0,0,0,0.3);
                --shadow-lg:        0 10px 15px -3px rgba(0,0,0,0.55), 0 4px 6px -2px rgba(0,0,0,0.35);
                --shadow-blue:      0 4px 14px rgba(96,165,250,0.25);

                --header-bg:        linear-gradient(135deg, #060c1a 0%, #0f1f3d 100%);

                --badge-green-text:   #86efac;
                --badge-green-bg:     rgba(20,83,45,0.35);
                --badge-orange-text:  #fcd34d;
                --badge-orange-bg:    rgba(120,53,15,0.35);
                --badge-red-text:     #fca5a5;
                --badge-red-bg:       rgba(127,29,29,0.35);
                --badge-blue-text:    #93c5fd;
                --badge-blue-bg:      rgba(30,64,175,0.35);
                --badge-gray-text:    #cbd5e1;
                --badge-gray-bg:      rgba(71,85,105,0.35);
            }
        }

        /* ============================================================
           DARK MODE — Streamlit internal (hamburger menu toggle)
           Streamlit sets data-theme="dark" on the HTML element
        ============================================================ */
        [data-theme="dark"],
        .stApp[data-theme="dark"],
        html[data-theme="dark"] {
            --bg-app:           #0d1117;
            --bg-surface:       #161b27;
            --bg-surface-alt:   #1a2035;

            --blue-700:         #2563eb;
            --blue-600:         #3b82f6;
            --blue-500:         #60a5fa;
            --blue-400:         #93c5fd;
            --blue-300:         #bfdbfe;
            --blue-200:         #dbeafe;
            --blue-100:         rgba(219,234,254,0.15);
            --blue-50:          rgba(239,246,255,0.07);

            --text-primary:     #e2e8f0;
            --text-secondary:   #94a3b8;
            --text-muted:       #64748b;
            --text-inverse:     #0f172a;
            --text-accent:      #60a5fa;

            --border-default:   rgba(255,255,255,0.09);
            --border-blue:      rgba(96,165,250,0.25);
            --border-focus:     #60a5fa;

            --success-bg:       rgba(20,83,45,0.25);
            --success-border:   rgba(34,197,94,0.35);
            --success-text:     #86efac;
            --success-subtext:  #bbf7d0;
            --error-bg:         rgba(127,29,29,0.25);
            --error-border:     rgba(239,68,68,0.35);
            --error-text:       #fca5a5;
            --error-subtext:    #fee2e2;
            --warning-bg:       rgba(120,53,15,0.25);
            --warning-border:   rgba(251,191,36,0.35);
            --warning-text:     #fcd34d;

            --shadow-sm:        0 1px 3px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.25);
            --shadow-md:        0 4px 6px -1px rgba(0,0,0,0.45), 0 2px 4px -1px rgba(0,0,0,0.3);
            --shadow-lg:        0 10px 15px -3px rgba(0,0,0,0.55), 0 4px 6px -2px rgba(0,0,0,0.35);
            --shadow-blue:      0 4px 14px rgba(96,165,250,0.25);

            --header-bg:        linear-gradient(135deg, #060c1a 0%, #0f1f3d 100%);

            --badge-green-text:   #86efac;
            --badge-green-bg:     rgba(20,83,45,0.35);
            --badge-orange-text:  #fcd34d;
            --badge-orange-bg:    rgba(120,53,15,0.35);
            --badge-red-text:     #fca5a5;
            --badge-red-bg:       rgba(127,29,29,0.35);
            --badge-blue-text:    #93c5fd;
            --badge-blue-bg:      rgba(30,64,175,0.35);
            --badge-gray-text:    #cbd5e1;
            --badge-gray-bg:      rgba(71,85,105,0.35);
        }

        /* ============================================================
           BASE APPLICATION
        ============================================================ */
        .stApp {
            background-color: var(--bg-app) !important;
        }

        /* ============================================================
           TYPOGRAPHY (safe: exclude icon/button spans)
        ============================================================ */
        html, body, p, li, label, h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text-primary);
        }

        .stMarkdown, .stText, [data-testid="stMarkdownContainer"] {
            color: var(--text-primary) !important;
        }

        /* ============================================================
           MATERIAL ICONS — preserve font-family
        ============================================================ */
        .material-icons,
        .material-icons-outlined,
        .material-symbols-outlined,
        .material-symbols-rounded,
        .material-symbols-sharp,
        [data-testid="stIcon"],
        [data-testid="stChatMessageAvatarAssistant"] span,
        [data-testid="stChatMessageAvatarUser"] span {
            font-family: 'Material Icons', 'Material Icons Outlined', 'Material Symbols Outlined' !important;
            font-weight: normal !important;
            font-style: normal !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            direction: ltr !important;
            -webkit-font-smoothing: antialiased !important;
        }

        /* ============================================================
           HOSPITAL HEADER — always dark navy gradient
        ============================================================ */
        .hospital-header {
            background: var(--header-bg) !important;
            padding: 22px 32px;
            border-radius: 14px;
            margin-bottom: 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.35);
            border: 1px solid rgba(255,255,255,0.06);
            position: relative;
            overflow: hidden;
        }

        .hospital-header::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(90deg, rgba(37,99,235,0.08) 0%, transparent 60%);
            pointer-events: none;
        }

        /* Force header internals to always be white (dark bg) */
        .hospital-header *,
        .hospital-header h1,
        .hospital-header p {
            color: #ffffff !important;
        }

        .hospital-header h1 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            font-size: 26px !important;
            letter-spacing: -0.3px !important;
            margin: 0 !important;
        }

        .hospital-header p {
            margin: 6px 0 0 0 !important;
            font-size: 14px !important;
            color: rgba(148,197,253,0.9) !important;
            font-weight: 400 !important;
        }

        .header-badge {
            font-size: 13px;
            font-weight: 600;
            color: #38bdf8 !important;
            background: rgba(56,189,248,0.12);
            padding: 8px 18px;
            border-radius: 30px;
            border: 1px solid rgba(56,189,248,0.25);
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* ============================================================
           CARDS
        ============================================================ */
        .hospital-card {
            background: var(--bg-surface) !important;
            border: 1px solid var(--border-default) !important;
            border-radius: 14px !important;
            padding: 24px !important;
            box-shadow: var(--shadow-md) !important;
            transition: transform 0.25s cubic-bezier(0.4,0,0.2,1),
                        box-shadow 0.25s ease,
                        border-color 0.25s ease !important;
            margin-bottom: 20px;
        }

        .hospital-card:hover {
            transform: translateY(-3px) !important;
            box-shadow: var(--shadow-lg) !important;
            border-color: var(--border-blue) !important;
        }

        /* Stat cards */
        .stat-card-blue {
            background: var(--blue-50) !important;
            border: 1px solid var(--blue-200) !important;
            border-radius: 14px !important;
            padding: 22px !important;
            box-shadow: var(--shadow-sm) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            position: relative;
            overflow: hidden;
        }

        .stat-card-blue::after {
            content: '';
            position: absolute;
            top: 0; right: 0;
            width: 60px; height: 60px;
            background: var(--blue-200);
            border-radius: 50%;
            transform: translate(20px, -20px);
            opacity: 0.35;
        }

        .stat-card-blue:hover {
            transform: translateY(-3px) scale(1.01) !important;
            box-shadow: var(--shadow-blue) !important;
            border-color: var(--blue-400) !important;
        }

        .stat-card-blue .stat-label {
            font-size: 11px;
            font-weight: 700;
            color: var(--text-accent);
            letter-spacing: 0.8px;
            text-transform: uppercase;
        }

        .stat-card-blue .stat-value {
            font-size: 34px;
            font-weight: 800;
            color: var(--text-primary);
            margin-top: 6px;
            font-family: 'Outfit', sans-serif;
            letter-spacing: -1px;
        }

        .stat-card-blue .stat-delta {
            font-size: 12px;
            margin-top: 4px;
            font-weight: 500;
            color: var(--text-secondary);
        }

        /* ============================================================
           BADGE STYLES — use CSS vars so they adapt to dark/light
        ============================================================ */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
            line-height: 1.5;
        }

        .badge-green  { color: var(--badge-green-text);  background: var(--badge-green-bg); }
        .badge-orange { color: var(--badge-orange-text); background: var(--badge-orange-bg); }
        .badge-red    { color: var(--badge-red-text);    background: var(--badge-red-bg); }
        .badge-blue   { color: var(--badge-blue-text);   background: var(--badge-blue-bg); }
        .badge-gray   { color: var(--badge-gray-text);   background: var(--badge-gray-bg); }

        /* ============================================================
           TYPOGRAPHY CLASSES
        ============================================================ */
        .clinical-title {
            color: var(--text-primary) !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            font-size: 24px !important;
            letter-spacing: -0.3px !important;
            margin-bottom: 4px !important;
        }

        .clinical-subtitle {
            color: var(--text-secondary) !important;
            font-size: 14px !important;
            font-weight: 400 !important;
            margin-bottom: 24px !important;
            line-height: 1.5 !important;
        }

        /* ============================================================
           SIDEBAR — always dark navy
        ============================================================ */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
        }

        [data-testid="stSidebar"] * {
            color: rgba(255,255,255,0.85) !important;
        }

        [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div,
        [data-testid="stSidebar"] input {
            background-color: rgba(255,255,255,0.07) !important;
            border-color: rgba(255,255,255,0.12) !important;
            color: #e2e8f0 !important;
        }

        /* ============================================================
           TABS
        ============================================================ */
        [data-testid="stTabs"] [role="tablist"] {
            border-bottom: 2px solid var(--border-default) !important;
        }

        [data-testid="stTabs"] [role="tab"] {
            font-weight: 500 !important;
            font-size: 14px !important;
            color: var(--text-secondary) !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 8px 16px !important;
            transition: color 0.2s ease, background 0.2s ease !important;
        }

        [data-testid="stTabs"] [role="tab"]:hover {
            color: var(--text-accent) !important;
            background: var(--blue-50) !important;
        }

        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            color: var(--blue-600) !important;
            border-bottom: 2px solid var(--blue-600) !important;
            font-weight: 600 !important;
        }

        /* ============================================================
           BUTTONS
        ============================================================ */
        [data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, var(--blue-600) 0%, var(--blue-700) 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
        }

        [data-testid="stBaseButton-primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(37,99,235,0.4) !important;
        }

        [data-testid="stBaseButton-secondary"] {
            background-color: var(--bg-surface) !important;
            color: var(--text-accent) !important;
            border: 1.5px solid var(--border-blue) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stBaseButton-secondary"]:hover {
            background-color: var(--blue-50) !important;
            border-color: var(--blue-500) !important;
            transform: translateY(-1px) !important;
        }

        /* File uploader */
        [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
            padding: 8px 18px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            width: auto !important;
            height: auto !important;
            box-shadow: none !important;
        }

        [data-testid="stFileUploader"] button[aria-label="Remove file"],
        [data-testid="stFileUploader"] button:has(svg) {
            background-color: transparent !important;
            border: none !important;
            color: #ef4444 !important;
            box-shadow: none !important;
            padding: 4px !important;
            width: auto !important;
            height: auto !important;
            min-height: 0 !important;
        }

        /* Popover FAB cleanup */
        [data-testid="stPopover"] > button span:nth-child(2),
        [data-testid="stPopover"] > button [data-testid="stIcon"],
        [data-testid="stPopover"] > summary [data-testid="stIcon"],
        [data-testid="stPopover"] > details > summary [data-testid="stIcon"],
        [data-testid="stPopover"] > button svg,
        [data-testid="stPopover"] > summary svg,
        [data-testid="stPopover"] > details > summary svg {
            display: none !important;
        }

        /* ============================================================
           INPUTS
        ============================================================ */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background-color: var(--bg-surface) !important;
            border: 1.5px solid var(--border-default) !important;
            border-radius: 8px !important;
            padding: 10px 14px !important;
            font-size: 14px !important;
            color: var(--text-primary) !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--border-focus) !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
            outline: none !important;
        }

        div[data-testid="stSelectbox"] > div > div {
            background-color: var(--bg-surface) !important;
            border: 1.5px solid var(--border-default) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }

        /* ============================================================
           DIVIDERS & EXPANDERS
        ============================================================ */
        hr, [data-testid="stDivider"] {
            border-color: var(--border-default) !important;
            opacity: 1 !important;
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--border-default) !important;
            border-radius: 10px !important;
            background-color: var(--bg-surface) !important;
        }

        /* ============================================================
           CLINICAL DATA TABLES
        ============================================================ */
        .clinical-table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
            text-align: left;
            border-radius: 12px;
            overflow: hidden;
        }

        .clinical-table th {
            background-color: var(--blue-50);
            color: var(--text-accent);
            font-weight: 700;
            font-size: 11.5px;
            letter-spacing: 0.7px;
            text-transform: uppercase;
            padding: 13px 16px;
            border-bottom: 2px solid var(--blue-200);
        }

        .clinical-table td {
            padding: 13px 16px;
            border-bottom: 1px solid var(--border-default);
            color: var(--text-primary);
            font-size: 13.5px;
        }

        .clinical-table tr:hover td {
            background-color: var(--blue-50);
        }

        .clinical-table tr:last-child td {
            border-bottom: none;
        }

        /* ============================================================
           DOCTOR PROFILE CARD
        ============================================================ */
        .doc-profile-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-default);
            border-radius: 14px;
            padding: 20px;
            display: flex;
            gap: 16px;
            align-items: center;
            box-shadow: var(--shadow-sm);
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        }

        .doc-profile-card:hover {
            transform: translateY(-3px);
            border-color: var(--border-blue);
            box-shadow: var(--shadow-blue);
        }

        /* ============================================================
           STATUS CARDS
        ============================================================ */
        .status-card {
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border-width: 2px;
            border-style: solid;
        }

        .status-card.success {
            background-color: var(--success-bg);
            border-color: var(--success-border);
        }

        .status-card.error {
            background-color: var(--error-bg);
            border-color: var(--error-border);
        }

        .status-card h4 {
            margin: 0 0 10px 0;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 16px;
        }

        .status-card.success h4 { color: var(--success-text); }
        .status-card.error h4   { color: var(--error-text); }

        .status-card p {
            font-size: 14px;
            margin: 0 0 12px 0;
            font-weight: 500;
            line-height: 1.5;
        }

        .status-card.success p { color: var(--success-subtext); }
        .status-card.error p   { color: var(--error-subtext); }

        .status-card hr {
            border: 0;
            margin: 10px 0;
        }

        .status-card.success hr { border-top: 1px solid var(--success-border) !important; }
        .status-card.error hr   { border-top: 1px solid var(--error-border) !important; }

        .status-card ul { font-size: 13px; margin: 0; padding-left: 20px; line-height: 1.7; }
        .status-card.success ul { color: var(--success-subtext); }
        .status-card.error ul   { color: var(--error-subtext); }

        /* ============================================================
           CHAT MESSAGES
        ============================================================ */
        [data-testid="stChatMessage"] {
            background-color: var(--bg-surface) !important;
            border: 1px solid var(--border-default) !important;
            border-radius: 12px !important;
            padding: 14px !important;
            box-shadow: var(--shadow-sm) !important;
        }

        /* ============================================================
           FLOATING PANELS — adaptive
           These target the popover body panels for both chat + settings
        ============================================================ */
        [data-testid="stPopoverBody"] {
            background-color: var(--bg-surface) !important;
            border-color: var(--border-default) !important;
        }

        /* ============================================================
           ANIMATIONS
        ============================================================ */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(12px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .hospital-header,
        .hospital-card,
        .stat-card-blue,
        .doc-profile-card {
            animation: fadeInUp 0.35s ease both;
        }

        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50%       { opacity: 0.4; }
        }

        .live-dot {
            display: inline-block;
            width: 8px; height: 8px;
            background: #22c55e;
            border-radius: 50%;
            animation: pulse-dot 1.8s ease infinite;
            flex-shrink: 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
