def get_dashboard_html() -> str:
    """Returns the raw HTML string for the premium, glassmorphic Offline AI Stack Web Dashboard."""
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline AI Stack - Web Control Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #080b11;
            --card-bg: rgba(13, 18, 30, 0.65);
            --border-glow: rgba(255, 255, 255, 0.07);
            --accent-primary: #6366f1; /* Neon Purple/Indigo */
            --accent-secondary: #a855f7; /* Violet */
            --accent-emerald: #10b981; /* Green */
            --accent-rose: #f43f5e; /* Rose Red */
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
            scroll-behavior: smooth;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(168, 85, 247, 0.08) 0%, transparent 40%);
            background-attachment: fixed;
        }

        /* Container Layout */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* Header Brand */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .brand-logo {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
        }

        .brand-logo svg {
            width: 24px;
            height: 24px;
            fill: #fff;
        }

        .brand-title h1 {
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #ffffff, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-title p {
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 400;
        }

        .badge-live {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid var(--accent-emerald);
            color: var(--accent-emerald);
            padding: 6px 14px;
            border-radius: 50px;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .badge-live .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: var(--accent-emerald);
            border-radius: 50%;
            animation: pulse-ring 1.8s infinite;
        }

        @keyframes pulse-ring {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Service Cards Grid */
        .services-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .grid-services {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 25px;
            margin-bottom: 45px;
        }

        .service-card {
            background: var(--card-bg);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(16px);
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 200px;
            text-decoration: none;
            color: inherit;
        }

        .service-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%);
            opacity: 0;
            transition: opacity 0.4s ease;
        }

        .service-card:hover {
            transform: translateY(-8px);
            border-color: rgba(99, 102, 241, 0.35);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3), 0 0 25px rgba(99, 102, 241, 0.15);
        }

        .service-card:hover::before {
            opacity: 1;
        }

        .card-top {
            position: relative;
            z-index: 2;
        }

        .card-icon {
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }

        .service-card:hover .card-icon {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-color: transparent;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
        }

        .card-icon svg {
            width: 24px;
            height: 24px;
            fill: #fff;
            transition: fill 0.3s ease;
        }

        .card-info h3 {
            font-size: 19px;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: -0.3px;
        }

        .card-info p {
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
        }

        .card-bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 25px;
            position: relative;
            z-index: 2;
        }

        .card-port {
            font-size: 12px;
            color: var(--text-muted);
            background: rgba(255, 255, 255, 0.04);
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 500;
        }

        .card-link-arrow {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.03);
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }

        .service-card:hover .card-link-arrow {
            background: #fff;
            transform: translateX(3px);
        }

        .card-link-arrow svg {
            width: 14px;
            height: 14px;
            fill: var(--text-muted);
            transition: fill 0.3s ease;
        }

        .service-card:hover .card-link-arrow svg {
            fill: var(--bg-dark);
        }

        /* Two Column Layout */
        .workspace-layout {
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 30px;
        }

        /* Left: Ingestion Engine Panel */
        .ingestion-panel {
            background: var(--card-bg);
            border: 1px solid var(--border-glow);
            border-radius: 24px;
            padding: 35px;
            backdrop-filter: blur(16px);
            display: flex;
            flex-direction: column;
            gap: 25px;
        }

        .panel-header {
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 15px;
        }

        .panel-header h2 {
            font-size: 21px;
            font-weight: 600;
            background: linear-gradient(to right, #ffffff, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }

        .panel-header p {
            font-size: 13px;
            color: var(--text-muted);
        }

        /* Tab Headers */
        .tab-headers {
            display: flex;
            background: rgba(0, 0, 0, 0.25);
            padding: 5px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }

        .tab-btn {
            flex: 1;
            background: none;
            border: none;
            color: var(--text-muted);
            padding: 12px;
            border-radius: 9px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .tab-btn svg {
            width: 16px;
            height: 16px;
            fill: currentColor;
        }

        .tab-btn.active {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: #fff;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.25);
            font-weight: 600;
        }

        /* Form Controls */
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .form-group label {
            font-size: 13px;
            font-weight: 500;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .input-wrapper {
            position: relative;
        }

        .input-wrapper input, .input-wrapper select {
            width: 100%;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 14px 16px;
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: all 0.3s ease;
        }

        .input-wrapper input:focus, .input-wrapper select:focus {
            border-color: var(--accent-primary);
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.15);
            background: rgba(0, 0, 0, 0.4);
        }

        .input-help {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }

        .btn-submit {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border: none;
            border-radius: 12px;
            padding: 16px;
            color: #fff;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(99, 102, 241, 0.45);
            filter: brightness(1.1);
        }

        .btn-submit:active {
            transform: translateY(0);
        }

        .btn-submit svg {
            width: 18px;
            height: 18px;
            fill: #fff;
        }

        /* Right: System Status & Monitor */
        .right-column {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .monitor-panel {
            background: var(--card-bg);
            border: 1px solid var(--border-glow);
            border-radius: 24px;
            padding: 30px;
            backdrop-filter: blur(16px);
        }

        .monitor-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 12px;
        }

        .monitor-header h2 {
            font-size: 18px;
            font-weight: 600;
        }

        .monitor-header span {
            font-size: 12px;
            color: var(--text-muted);
        }

        /* Health rows */
        .health-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .health-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 18px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 12px;
        }

        .row-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .row-left svg {
            width: 18px;
            height: 18px;
            fill: var(--text-muted);
        }

        .row-left-info h4 {
            font-size: 14px;
            font-weight: 500;
        }

        .row-left-info p {
            font-size: 11px;
            color: var(--text-muted);
        }

        .row-right {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-badge {
            font-size: 11px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 6px;
            text-transform: uppercase;
        }

        .status-badge.online {
            background: rgba(16, 185, 129, 0.1);
            color: var(--accent-emerald);
        }

        .status-badge.offline {
            background: rgba(244, 63, 94, 0.1);
            color: var(--accent-rose);
        }

        .status-indicator-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .status-indicator-dot.online {
            background-color: var(--accent-emerald);
            box-shadow: 0 0 8px var(--accent-emerald);
        }

        .status-indicator-dot.offline {
            background-color: var(--accent-rose);
            box-shadow: 0 0 8px var(--accent-rose);
        }

        /* Resources Stats panel */
        .resources-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }

        .resource-card-mini {
            background: rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 14px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .resource-card-mini span {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 500;
        }

        .resource-card-mini h4 {
            font-size: 18px;
            font-weight: 600;
        }

        /* Loader Overlay inside Panels */
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(8, 11, 17, 0.85);
            backdrop-filter: blur(8px);
            z-index: 10;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 15px;
            border-radius: 24px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }

        .loading-overlay.active {
            opacity: 1;
            pointer-events: all;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(99, 102, 241, 0.1);
            border-top: 3px solid var(--accent-primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Feedback Popups / Status Notifications */
        .notification-banner {
            display: none;
            padding: 15px 20px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            line-height: 1.5;
            margin-top: 15px;
            border: 1px solid transparent;
            animation: fadeIn 0.4s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .notification-banner.success {
            display: block;
            background: rgba(16, 185, 129, 0.08);
            border-color: rgba(16, 185, 129, 0.25);
            color: #d1fae5;
        }

        .notification-banner.error {
            display: block;
            background: rgba(244, 63, 94, 0.08);
            border-color: rgba(244, 63, 94, 0.25);
            color: #ffe4e6;
        }

        /* Responsive */
        @media (max-width: 900px) {
            .workspace-layout {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        
        <!-- Header brand -->
        <header>
            <div class="brand">
                <div class="brand-logo">
                    <svg viewBox="0 0 24 24">
                        <path d="M12 2L2 22h20L12 2zm0 3.8L18.4 18H5.6L12 5.8zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z"/>
                    </svg>
                </div>
                <div class="brand-title">
                    <h1>Offline AI Stack</h1>
                    <p>Local Ingestion & Workflow Portal</p>
                </div>
            </div>
            <div class="badge-live">
                <div class="pulse-dot"></div>
                <span>Local Air-Gapped Network</span>
            </div>
        </header>

        <!-- Services Launcher Section -->
        <h2 class="services-title">Quick-Launch Private Dashboards</h2>
        <div class="grid-services">
            
            <!-- OpenWebUI Card -->
            <a href="http://localhost:3000" target="_blank" class="service-card">
                <div class="card-top">
                    <div class="card-icon">
                        <!-- Chat Icon -->
                        <svg viewBox="0 0 24 24">
                            <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/>
                        </svg>
                    </div>
                    <div class="card-info">
                        <h3>Chat with AI</h3>
                        <p>Launch OpenWebUI interface to chat with local models (llama3) and discuss context.</p>
                    </div>
                </div>
                <div class="card-bottom">
                    <span class="card-port">Port 3000</span>
                    <div class="card-link-arrow">
                        <svg viewBox="0 0 24 24"><path d="M5 13h11.86l-5.43 5.43 1.42 1.42L21 12l-8.15-8.15-1.42 1.42 5.43 5.43H5v2z"/></svg>
                    </div>
                </div>
            </a>

            <!-- n8n Card -->
            <a href="http://localhost:5678" target="_blank" class="service-card">
                <div class="card-top">
                    <div class="card-icon">
                        <!-- Workflow Automation Icon -->
                        <svg viewBox="0 0 24 24">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/>
                        </svg>
                    </div>
                    <div class="card-info">
                        <h3>n8n Workflows</h3>
                        <p>Open local automation server to build webhook flows, cron schedulers, and n8n pipelines.</p>
                    </div>
                </div>
                <div class="card-bottom">
                    <span class="card-port">Port 5678</span>
                    <div class="card-link-arrow">
                        <svg viewBox="0 0 24 24"><path d="M5 13h11.86l-5.43 5.43 1.42 1.42L21 12l-8.15-8.15-1.42 1.42 5.43 5.43H5v2z"/></svg>
                    </div>
                </div>
            </a>

            <!-- Qdrant Card -->
            <a href="http://localhost:6333/dashboard" target="_blank" class="service-card">
                <div class="card-top">
                    <div class="card-icon">
                        <!-- Database Icon -->
                        <svg viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H7c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.04-.42 1.99-1.07 2.75z"/>
                        </svg>
                    </div>
                    <div class="card-info">
                        <h3>Qdrant Vector DB</h3>
                        <p>Inspect search collections, active points counts, storage configurations, and payload fields.</p>
                    </div>
                </div>
                <div class="card-bottom">
                    <span class="card-port">Port 6333</span>
                    <div class="card-link-arrow">
                        <svg viewBox="0 0 24 24"><path d="M5 13h11.86l-5.43 5.43 1.42 1.42L21 12l-8.15-8.15-1.42 1.42 5.43 5.43H5v2z"/></svg>
                    </div>
                </div>
            </a>

            <!-- FastAPI Card -->
            <a href="http://localhost:8000/docs" target="_blank" class="service-card">
                <div class="card-top">
                    <div class="card-icon">
                        <!-- API Icon -->
                        <svg viewBox="0 0 24 24">
                            <path d="M12 3c-4.97 0-9 4.03-9 9 0 2.12.74 4.07 1.97 5.61L4.35 19.4c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0l1.9-1.9C9.17 19.58 10.53 20 12 20c4.97 0 9-4.03 9-9s-4.03-9-9-9zm1 14h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                        </svg>
                    </div>
                    <div class="card-info">
                        <h3>FastAPI API Docs</h3>
                        <p>Interact with standard Swagger REST API schemas for files, folder mappings, and query testing.</p>
                    </div>
                </div>
                <div class="card-bottom">
                    <span class="card-port">Port 8000</span>
                    <div class="card-link-arrow">
                        <svg viewBox="0 0 24 24"><path d="M5 13h11.86l-5.43 5.43 1.42 1.42L21 12l-8.15-8.15-1.42 1.42 5.43 5.43H5v2z"/></svg>
                    </div>
                </div>
            </a>

        </div>

        <!-- Working Panels section -->
        <div class="workspace-layout">
            
            <!-- Left: Document Ingestion panel -->
            <div class="ingestion-panel" style="position: relative;">
                
                <!-- Panel Loader -->
                <div class="loading-overlay" id="ingest-loader">
                    <div class="spinner"></div>
                    <p style="font-weight: 500; font-size: 15px;" id="ingest-loading-text">Chunking and embedding document...</p>
                </div>

                <div class="panel-header">
                    <h2>Document Indexer</h2>
                    <p>Paste the local computer path of a document file or an entire folder to feed your AI context.</p>
                </div>

                <!-- Tabs -->
                <div class="tab-headers">
                    <button class="tab-btn active" onclick="switchTab('file')">
                        <svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                        <span>Single Document File</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('folder')">
                        <svg viewBox="0 0 24 24"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>
                        <span>Entire Folder / Folder Ingestion</span>
                    </button>
                </div>

                <!-- Collection Target Group -->
                <div class="form-group">
                    <label>Target Vector Database Collection</label>
                    <div class="input-wrapper">
                        <input type="text" id="target-collection" value="rag_documents" placeholder="e.g. sales_contracts">
                    </div>
                    <span class="input-help">The index name where embeddings will be saved. We recommend leaving as default.</span>
                </div>

                <!-- Dynamic Tab Form Ingest Local File -->
                <div id="form-file" class="tab-form-content">
                    <div class="form-group">
                        <label>Local File Path</label>
                        <div class="input-wrapper">
                            <input type="text" id="file-path" placeholder="e.g. C:\Users\root\Desktop\technical_manual.pdf">
                        </div>
                        <span class="input-help">Supports absolute paths to PDF, Text (.txt), or Markdown (.md) documents.</span>
                    </div>
                </div>

                <!-- Dynamic Tab Form Ingest Local Folder -->
                <div id="form-folder" class="tab-form-content" style="display: none;">
                    <div class="form-group">
                        <label>Local Folder / Directory Path</label>
                        <div class="input-wrapper">
                            <input type="text" id="folder-path" placeholder="e.g. C:\Users\root\Desktop\offline-ai-stack\data\ingest">
                        </div>
                        <span class="input-help">Indexes all supported document files recursively inside this local directory.</span>
                    </div>
                </div>

                <!-- Action Button -->
                <button class="btn-submit" onclick="executeIngestion()">
                    <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                    <span id="btn-text">Execute Ingestion and Index</span>
                </button>

                <!-- Feedback Banner -->
                <div class="notification-banner" id="ingest-notification"></div>

            </div>

            <!-- Right: Status Monitor panel -->
            <div class="right-column">
                
                <!-- System Monitor Panel -->
                <div class="monitor-panel">
                    <div class="monitor-header">
                        <h2>Services Telemetry</h2>
                        <span id="last-update">Updating...</span>
                    </div>

                    <div class="health-list">
                        
                        <!-- OpenWebUI Status -->
                        <div class="health-row">
                            <div class="row-left">
                                <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
                                <div class="row-left-info">
                                    <h4>OpenWebUI Dashboard</h4>
                                    <p>Chat interface port 3000</p>
                                </div>
                            </div>
                            <div class="row-right">
                                <span class="status-badge offline" id="status-openwebui-badge">Checking</span>
                                <div class="status-indicator-dot offline" id="status-openwebui-dot"></div>
                            </div>
                        </div>

                        <!-- n8n Status -->
                        <div class="health-row">
                            <div class="row-left">
                                <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>
                                <div class="row-left-info">
                                    <h4>n8n Automation</h4>
                                    <p>Webhook triggers port 5678</p>
                                </div>
                            </div>
                            <div class="row-right">
                                <span class="status-badge offline" id="status-n8n-badge">Checking</span>
                                <div class="status-indicator-dot offline" id="status-n8n-dot"></div>
                            </div>
                        </div>

                        <!-- Qdrant Status -->
                        <div class="health-row">
                            <div class="row-left">
                                <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>
                                <div class="row-left-info">
                                    <h4>Qdrant Vector DB</h4>
                                    <p>Cosines collection port 6333</p>
                                </div>
                            </div>
                            <div class="row-right">
                                <span class="status-badge offline" id="status-qdrant-badge">Checking</span>
                                <div class="status-indicator-dot offline" id="status-qdrant-dot"></div>
                            </div>
                        </div>

                        <!-- Ollama Status -->
                        <div class="health-row">
                            <div class="row-left">
                                <svg viewBox="0 0 24 24"><path d="M12 3c-4.97 0-9 4.03-9 9 0 2.12.74 4.07 1.97 5.61L4.35 19.4c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0l1.9-1.9C9.17 19.58 10.53 20 12 20c4.97 0 9-4.03 9-9s-4.03-9-9-9z"/></svg>
                                <div class="row-left-info">
                                    <h4>Ollama AI Engine</h4>
                                    <p>Model inference port 11434</p>
                                </div>
                            </div>
                            <div class="row-right">
                                <span class="status-badge offline" id="status-ollama-badge">Checking</span>
                                <div class="status-indicator-dot offline" id="status-ollama-dot"></div>
                            </div>
                        </div>

                    </div>

                    <!-- Mini resource graphs -->
                    <div class="resources-row">
                        <div class="resource-card-mini">
                            <span>System CPU Cores</span>
                            <h4 id="cpu-stat">- Cores</h4>
                        </div>
                        <div class="resource-card-mini">
                            <span>Available RAM</span>
                            <h4 id="ram-stat">- GB</h4>
                        </div>
                    </div>
                </div>

            </div>

        </div>
    </div>

    <!-- Telemetry Client Script -->
    <script>
        let currentTab = 'file';

        function switchTab(tab) {
            currentTab = tab;
            // Toggle active buttons
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            if (tab === 'file') {
                buttons[0].classList.add('active');
                document.getElementById('form-file').style.display = 'block';
                document.getElementById('form-folder').style.display = 'none';
            } else {
                buttons[1].classList.add('active');
                document.getElementById('form-file').style.display = 'none';
                document.getElementById('form-folder').style.display = 'block';
            }
        }

        // Live Telemetry status polling
        async function checkStatus() {
            try {
                const response = await fetch('/status');
                if (!response.ok) throw new Error("Status API returned HTTP " + response.status);
                
                const data = await response.json();
                
                // Update time
                document.getElementById('last-update').innerText = "Live Telemetry - " + new Date().toLocaleTimeString();

                // Update RAM & CPU
                document.getElementById('cpu-stat').innerText = data.host_resources.cpu_cores + " Cores";
                document.getElementById('ram-stat').innerText = data.host_resources.ram_gb + " GB";

                // Update services
                updateRowStatus('openwebui', data.openwebui.running);
                updateRowStatus('n8n', data.n8n.running);
                updateRowStatus('qdrant', data.qdrant.running);
                updateRowStatus('ollama', data.ollama.running);

            } catch (error) {
                console.error("Failed to poll status telemetry:", error);
                document.getElementById('last-update').innerText = "Reconnecting...";
                
                // Set all to offline
                updateRowStatus('openwebui', false);
                updateRowStatus('n8n', false);
                updateRowStatus('qdrant', false);
                updateRowStatus('ollama', false);
            }
        }

        function updateRowStatus(service, isOnline) {
            const badge = document.getElementById(`status-${service}-badge`);
            const dot = document.getElementById(`status-${service}-dot`);
            
            if (isOnline) {
                badge.innerText = "Online";
                badge.className = "status-badge online";
                dot.className = "status-indicator-dot online";
            } else {
                badge.innerText = "Offline";
                badge.className = "status-badge offline";
                dot.className = "status-indicator-dot offline";
            }
        }

        // Action: Ingestion Execution
        async function executeIngestion() {
            const collection = document.getElementById('target-collection').value.trim();
            const notification = document.getElementById('ingest-notification');
            
            // Hide notification initially
            notification.style.display = 'none';
            notification.className = 'notification-banner';

            if (!collection) {
                showNotification("Error: Target database collection name cannot be empty.", true);
                return;
            }

            const loader = document.getElementById('ingest-loader');
            const loaderText = document.getElementById('ingest-loading-text');

            if (currentTab === 'file') {
                const filePath = document.getElementById('file-path').value.trim();
                if (!filePath) {
                    showNotification("Error: Please provide a valid file path.", true);
                    return;
                }

                // Show Loader
                loaderText.innerText = "Ingesting and chunking file. Generating Nomics vector embeddings...";
                loader.classList.add('active');

                try {
                    const response = await fetch('/ingest/file', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            file_path: filePath,
                            collection_name: collection
                        })
                    });

                    const result = await response.json();
                    loader.classList.remove('active');

                    if (response.ok && result.success) {
                        showNotification(`🎉 <b>Ingestion Complete!</b><br>${result.message}`, false);
                    } else {
                        showNotification(`⚠️ <b>Ingestion Failed:</b> ${result.detail || result.message || "Unknown error"}`, true);
                    }
                } catch (err) {
                    loader.classList.remove('active');
                    showNotification(`❌ <b>Network Error:</b> Failed to connect to local API server. Check if FastAPI is running.`, true);
                }

            } else {
                // Folder Tab
                const folderPath = document.getElementById('folder-path').value.trim();
                if (!folderPath) {
                    showNotification("Error: Please provide a valid folder path.", true);
                    return;
                }

                // Show Loader
                loaderText.innerText = "Scanning folder structure. Recursively chunking and embedding documents...";
                loader.classList.add('active');

                try {
                    const response = await fetch('/ingest/folder', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            folder_path: folderPath,
                            collection_name: collection
                        })
                    });

                    const result = await response.json();
                    loader.classList.remove('active');

                    if (response.ok && result.success) {
                        showNotification(`🎉 <b>Folder Ingestion Complete!</b><br>${result.message}`, false);
                    } else {
                        showNotification(`⚠️ <b>Folder Ingestion Failed:</b> ${result.detail || result.message || "Unknown error"}`, true);
                    }
                } catch (err) {
                    loader.classList.remove('active');
                    showNotification(`❌ <b>Network Error:</b> Failed to connect to local API server. Check if FastAPI is running.`, true);
                }
            }
        }

        function showNotification(message, isError) {
            const notification = document.getElementById('ingest-notification');
            notification.innerHTML = message;
            notification.style.display = 'block';
            if (isError) {
                notification.className = 'notification-banner error';
            } else {
                notification.className = 'notification-banner success';
            }
        }

        // Start Polling Loops
        checkStatus();
        setInterval(checkStatus, 5000);
    </script>
</body>
</html>
"""
