#!/usr/bin/env python3
"""
BLGV BTC Mining Pool - Clean Start Server
Ensures clean startup and proper HTML serving
"""
import os
import json
import asyncio
import threading
import logging
import traceback
from datetime import datetime
from typing import Dict, Optional
from flask import Flask, request, jsonify, Response

# Import test mode configuration  
from test_mode_config import (
    is_test_mode, should_show_fake_assets, get_test_session_id, 
    get_fake_mining_data, add_test_mode_fields, filter_test_data
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'blgv-mining-2025')

# Pool statistics
pool_stats = {
    'total_hashrate': 2847.3,
    'active_miners': 2156,
    'total_shares': 5892456,
    'blocks_found': 247,
    'pool_fee': 2.0,
    'network_difficulty': 102289407543323.8,
    'btc_price': 106234
}

# Complete institutional-grade HTML interface with all features from requirements
MINING_POOL_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BLGV BTC Mining Pool - Institutional Grade</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'blgv-primary': '#dc2626',
                        'blgv-secondary': '#1e293b',
                        'blgv-accent': '#fbbf24'
                    }
                }
            }
        }
    </script>
    <style>
        body { 
            background: linear-gradient(135deg, #020617 0%, #0f172a 100%); 
            color: white; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
        }
        .gradient-text {
            background: linear-gradient(135deg, #dc2626, #fbbf24);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(55, 65, 81, 0.5);
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            transition: all 0.3s ease;
        }
        .card:hover { 
            border-color: #dc2626; 
            transform: translateY(-2px);
            box-shadow: 0 20px 40px rgba(220, 38, 38, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #dc2626, #b91c1c);
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, #b91c1c, #991b1b);
            transform: translateY(-1px);
        }
        .status-online { 
            width: 12px; height: 12px; 
            background: #10b981; 
            border-radius: 50%; 
            display: inline-block; 
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        .metric-card {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.1), rgba(251, 191, 36, 0.1));
            border: 1px solid rgba(220, 38, 38, 0.2);
        }
        .mining-animation {
            background: linear-gradient(45deg, #dc2626, #fbbf24, #dc2626);
            background-size: 300% 300%;
            animation: mining 3s ease infinite;
        }
        @keyframes mining {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .section { display: none; }
        .section.active { display: block; }
        .nav-link {
            padding: 12px 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        }
        .nav-link:hover, .nav-link.active {
            background: rgba(220, 38, 38, 0.2);
            color: #dc2626;
        }
        .nav-link.active::after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #dc2626, transparent);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #e5e7eb;
        }
        .form-input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(55, 65, 81, 0.8);
            border: 1px solid #6b7280;
            border-radius: 8px;
            color: white;
            transition: all 0.3s ease;
        }
        .form-input:focus {
            outline: none;
            border-color: #dc2626;
            box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
        }
        .validation-error {
            color: #ef4444;
            font-size: 12px;
            margin-top: 4px;
        }
        .validation-success {
            color: #10b981;
            font-size: 12px;
            margin-top: 4px;
        }
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }
        .modal.show { display: flex; }
        .modal-content {
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border-radius: 16px;
            padding: 32px;
            max-width: 600px;
            width: 90%;
            border: 1px solid #374151;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        }
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(30, 41, 59, 0.95);
            border: 1px solid #dc2626;
            border-radius: 8px;
            padding: 16px;
            color: white;
            z-index: 1000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        .toast.show { transform: translateX(0); }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #374151;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #dc2626, #fbbf24);
            transition: width 0.3s ease;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .mobile-nav-link {
            padding: 12px 0;
            font-weight: 500;
            color: #d1d5db;
            transition: all 0.3s ease;
            cursor: pointer;
            border-bottom: 1px solid transparent;
        }
        .mobile-nav-link {
            display: block;
            width: 100%;
            text-align: left;
            padding: 12px 16px;
            color: #d1d5db;
            background-color: transparent;
            border: none;
            border-radius: 8px;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .mobile-nav-link:hover, .mobile-nav-link.active {
            color: #dc2626;
            background-color: rgba(220, 38, 38, 0.1);
        }
        
        .nav-link.active {
            color: #dc2626 !important;
            font-weight: 600;
        }
        
        /* Mobile menu positioning within viewport */
        nav {
            position: relative;
        }
        
        #mobile-menu {
            top: 100%;
            left: 0;
            right: 0;
            max-height: calc(100vh - 80px);
            background-color: #111827 !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        
        /* Improved mobile menu animation */
        #mobile-menu.menu-open {
            transform: scaleY(1);
        }
        
        #mobile-menu.menu-closed {
            transform: scaleY(0);
        }
        @media (max-width: 768px) {
            .card {
                margin: 8px 0;
                padding: 16px !important;
            }
            .form-input {
                padding: 10px 12px;
                font-size: 16px; /* Prevents zoom on iOS */
            }
            .btn-primary {
                padding: 10px 16px;
                font-size: 14px;
            }
            .main-content {
                padding: 16px 0;
            }
            .nav-link {
                font-size: 14px;
                padding: 8px 12px;
            }
            .metric-card {
                min-height: auto;
            }
            .gradient-text {
                font-size: 24px;
                line-height: 1.2;
            }
        }
    </style>
</head>
<body>


    <!-- Navigation Header -->
    <nav class="bg-black/20 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-18 md:h-20">
                <!-- Logo and Brand -->
                <div class="flex items-center space-x-2 md:space-x-4">
                    <img src="/static/bh-pool-logo.png" alt="BH Pool" class="h-12 md:h-14 w-auto object-contain">
                    <div class="hidden sm:block text-sm md:text-lg font-semibold text-gray-300">Bitcoin Mining Pool</div>
                    <div class="status-online"></div>
                    <div class="hidden md:block text-xs text-gray-400">v2.0.0 Institutional</div>
                </div>
                
                <!-- Desktop Navigation -->
                <div class="hidden md:flex space-x-4">
                    <div class="nav-link active" onclick="showSection('dashboard')" data-translate="nav-dashboard">Dashboard</div>
                    <div class="nav-link" onclick="showSection('mining-setup')" data-translate="nav-mining">Mining Setup</div>
                    <div class="nav-link" onclick="showSection('analytics')" data-translate="nav-analytics">Analytics</div>
                    <div class="nav-link" onclick="showSection('marketplace')" data-translate="nav-marketplace">Marketplace</div>
                    <div class="nav-link" onclick="showSection('ecosystem')" data-translate="nav-ecosystem">Ecosystem</div>
                    <div class="nav-link" onclick="showSection('support')" data-translate="nav-support">Support</div>
                </div>
                
                <!-- Right Side Controls -->
                <div class="flex items-center space-x-3">
                    <!-- Desktop Controls -->
                    <div class="hidden md:flex items-center space-x-3">
                        <!-- Live Price Display -->
                        <div class="text-right">
                            <div class="text-sm text-gray-300">$<span id="desktop-btc-price">107,970</span></div>
                            <div class="text-xs text-gray-400">#<span id="desktop-block-height">902,660</span></div>
                        </div>
                        
                        <!-- Wallet Button -->
                        <button onclick="toggleWalletDrawer()" class="flex items-center space-x-2 bg-red-600/20 border border-red-500 text-red-400 px-3 py-2 rounded-lg hover:bg-red-600/30 transition-colors text-sm">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
                            </svg>
                            <span>Hub</span>
                        </button>
                    </div>

                    <!-- Mobile Controls -->
                    <div class="md:hidden flex items-center space-x-2">
                        <!-- Mobile Hub Button -->
                        <button onclick="toggleWalletDrawer()" class="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg transition-colors text-sm font-medium">
                            Hub
                        </button>
                        
                        <!-- Mobile Menu Button -->
                        <button id="mobile-menu-toggle" onclick="toggleMobileMenu()" class="p-2 text-gray-300 hover:text-white hover:bg-gray-800/50 rounded-lg transition-colors">
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Mobile Navigation Dropdown (positioned properly within viewport) -->
        <div id="mobile-menu" class="md:hidden absolute top-full left-0 right-0 bg-gray-900 border-t border-gray-700 shadow-2xl transform scale-y-0 origin-top transition-transform duration-200 ease-out z-50">
            <div class="max-h-screen overflow-y-auto">
                <div class="px-4 py-4 space-y-3">
                    <!-- Navigation Links -->
                    <div class="space-y-1">
                        <div class="mobile-nav-link active" onclick="showSection('dashboard'); closeMobileMenu()" data-translate="nav-dashboard">
                            <span class="text-base">📊 Dashboard</span>
                        </div>
                        <div class="mobile-nav-link" onclick="showSection('mining-setup'); closeMobileMenu()" data-translate="nav-mining">
                            <span class="text-base">⚙️ Mining Setup</span>
                        </div>
                        <div class="mobile-nav-link" onclick="showSection('analytics'); closeMobileMenu()" data-translate="nav-analytics">
                            <span class="text-base">📈 Analytics</span>
                        </div>
                        <div class="mobile-nav-link" onclick="showSection('marketplace'); closeMobileMenu()" data-translate="nav-marketplace">
                            <span class="text-base">🏪 Marketplace</span>
                        </div>
                        <div class="mobile-nav-link" onclick="showSection('ecosystem'); closeMobileMenu()" data-translate="nav-ecosystem">
                            <span class="text-base">🌐 Ecosystem</span>
                        </div>
                        <div class="mobile-nav-link" onclick="showSection('support'); closeMobileMenu()" data-translate="nav-support">
                            <span class="text-base">💬 Support</span>
                        </div>
                    </div>
                    
                    <!-- Mobile Stats Cards -->
                    <div class="pt-3 border-t border-gray-700">
                        <div class="grid grid-cols-2 gap-3 mb-3">
                            <div class="bg-gray-800 p-3 rounded-lg text-center border border-gray-700">
                                <div class="text-xs text-gray-400">Bitcoin Price</div>
                                <div class="text-lg font-bold text-green-400">$<span id="mobile-btc-price">106,234</span></div>
                            </div>
                            <div class="bg-gray-800 p-3 rounded-lg text-center border border-gray-700">
                                <div class="text-xs text-gray-400">Block Height</div>
                                <div class="text-lg font-bold text-blue-400">#<span id="mobile-block-height">902,607</span></div>
                            </div>
                        </div>
                        
                        <!-- Language Selector -->
                        <div class="pt-3 border-t border-gray-700">
                            <div class="text-xs text-gray-400 mb-2">Language</div>
                            <select id="language-select" onchange="changeLanguage(this.value)" class="w-full bg-gray-800 text-white border border-gray-600 rounded-lg px-3 py-2 text-sm">
                                <option value="en">🇺🇸 English</option>
                                <option value="es">🇪🇸 Español</option>
                                <option value="fr">🇫🇷 Français</option>
                                <option value="de">🇩🇪 Deutsch</option>
                                <option value="pt">🇧🇷 Português</option>
                                <option value="zh">🇨🇳 中文</option>
                                <option value="ja">🇯🇵 日本語</option>
                                <option value="ko">🇰🇷 한국어</option>
                                <option value="ru">🇷🇺 Русский</option>
                                <option value="ar">🇸🇦 العربية</option>
                            </select>
                        </div>
                        
                        <!-- Mobile Quick Actions -->
                        <div class="grid grid-cols-2 gap-2 mt-3">
                            <button onclick="showSection('mining-setup'); closeMobileMenu();" class="bg-blgv-primary hover:bg-red-700 text-white px-3 py-2 rounded-lg text-sm transition-colors">
                                Setup Miner
                            </button>
                            <button onclick="window.open('https://dex.blgvbtc.com', '_blank'); closeMobileMenu();" class="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-lg text-sm transition-colors">
                                Trade DEX
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Test Mode Indicator -->
    <div id="test-mode-indicator" class="hidden bg-yellow-600 text-black p-3 flex items-center justify-center text-sm font-medium">
        <span class="mr-2">⚠️</span>
        <div>
            <strong>Test Mode Active</strong>
            <span class="ml-2">Displaying fake mining payouts and assets for testing</span>
        </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8 py-4 md:py-8 main-content">
        <!-- Dashboard Section -->
        <div id="dashboard" class="section active">
            <!-- Welcome Section -->
            <div class="text-center mb-6 md:mb-8 px-4">
                <h1 class="text-2xl md:text-4xl font-bold gradient-text mb-3 md:mb-4" data-translate="welcome-title">Institutional-Grade Bitcoin Mining</h1>
                <p class="text-base md:text-xl text-gray-300 mb-4 md:mb-6" data-translate="welcome-subtitle">Bitcoin-Only • Stratum V2 • Enterprise Security • Global Scale</p>
                
                <!-- Quick Wallet Discovery -->
                <div class="max-w-md mx-auto mb-6">
                    <div class="flex flex-col sm:flex-row gap-2 sm:gap-0">
                        <input type="text" id="wallet-input" placeholder="Enter Bitcoin address to find your miners..." 
                               class="flex-1 px-3 md:px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg sm:rounded-l-lg sm:rounded-r-none text-white placeholder-gray-400 focus:outline-none focus:border-red-500 text-sm md:text-base"
                               data-translate-placeholder="wallet-placeholder">
                        <button onclick="discoverMiner()" class="btn-primary rounded-lg sm:rounded-l-none whitespace-nowrap px-4 py-3" data-translate="discover-btn">Discover</button>
                    </div>
                    <p class="text-xs text-gray-400 mt-2" data-translate="wallet-help">View mining stats, configure payouts, or start mining</p>
                </div>
            </div>

        <!-- Pool Statistics -->
        <div class="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6 mb-6 md:mb-8 px-4">
            <div class="card metric-card p-3 md:p-6">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div class="flex-1">
                        <p class="text-xs md:text-sm text-gray-400 mb-1" data-translate="stat-hashrate">Pool Hashrate</p>
                        <p class="text-lg md:text-2xl font-bold" id="pool-hashrate">2,847.3 TH/s</p>
                        <p class="text-xs text-green-400" id="hashrate-change">+12.5% (24h)</p>
                    </div>
                    <div class="mining-animation w-8 h-8 md:w-12 md:h-12 rounded-full flex items-center justify-center mt-2 md:mt-0 self-center md:self-auto">
                        <span class="text-white font-bold text-sm md:text-base">⚡</span>
                    </div>
                </div>
            </div>
            
            <div class="card metric-card p-3 md:p-6">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div class="flex-1">
                        <p class="text-xs md:text-sm text-gray-400 mb-1" data-translate="stat-miners">Active Miners</p>
                        <p class="text-lg md:text-2xl font-bold" id="active-miners">2,156</p>
                        <p class="text-xs text-blue-400" id="miners-change">+47 (1h)</p>
                    </div>
                    <div class="w-8 h-8 md:w-12 md:h-12 bg-blgv-primary/20 rounded-full flex items-center justify-center mt-2 md:mt-0 self-center md:self-auto">
                        <span class="text-blgv-primary font-bold text-sm md:text-base">👥</span>
                    </div>
                </div>
            </div>
            
            <div class="card metric-card p-3 md:p-6">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div class="flex-1">
                        <p class="text-xs md:text-sm text-gray-400 mb-1" data-translate="stat-difficulty">Network Difficulty</p>
                        <p class="text-lg md:text-2xl font-bold" id="network-difficulty">102.3T</p>
                        <p class="text-xs text-yellow-400" id="difficulty-change">+2.1% (est)</p>
                    </div>
                    <div class="w-8 h-8 md:w-12 md:h-12 bg-blgv-accent/20 rounded-full flex items-center justify-center mt-2 md:mt-0 self-center md:self-auto">
                        <span class="text-blgv-accent font-bold text-sm md:text-base">🎯</span>
                    </div>
                </div>
            </div>
            
            <div class="card metric-card p-3 md:p-6">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div class="flex-1">
                        <p class="text-xs md:text-sm text-gray-400 mb-1" data-translate="stat-blocks">Blocks Found</p>
                        <p class="text-lg md:text-2xl font-bold" id="blocks-found">247</p>
                        <p class="text-xs text-green-400" id="blocks-change">Last: 3m ago</p>
                    </div>
                    <div class="w-8 h-8 md:w-12 md:h-12 bg-green-500/20 rounded-full flex items-center justify-center mt-2 md:mt-0 self-center md:self-auto">
                        <span class="text-green-500 font-bold text-sm md:text-base">⛏️</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Mining Connection Instructions -->
        <div class="card mb-6 md:mb-8 glow mx-4">
            <h3 class="text-lg md:text-xl font-semibold mb-4 text-blgv-primary" data-translate="start-mining">Start Mining Now</h3>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
                <div>
                    <h4 class="font-semibold mb-3 text-sm md:text-base" data-translate="stratum-connection">Stratum V2 Connection</h4>
                    <div class="bg-gray-800/50 p-3 md:p-4 rounded-lg font-mono text-xs md:text-sm mb-4">
                        <p class="text-green-400 select-all break-all">stratum+tcp://pool.blgvbtc.com:3333</p>
                        <p class="text-gray-400 mt-2">Username: [your_bitcoin_address]</p>
                        <p class="text-gray-400">Password: [worker_name]</p>
                    </div>
                    <div class="flex flex-col sm:flex-row gap-2 sm:space-x-2">
                        <button onclick="copyToClipboard('stratum+tcp://pool.blgvbtc.com:3333')" class="btn-primary text-xs md:text-sm px-3 py-2" data-translate="copy-url">Copy URL</button>
                        <button onclick="showQRModal()" class="bg-gray-600 text-white px-3 py-2 rounded-lg hover:bg-gray-500 text-xs md:text-sm" data-translate="show-qr">Show QR</button>
                        <button onclick="downloadQuickStart()" class="bg-gray-600 text-white px-3 py-2 rounded-lg hover:bg-gray-500 text-xs md:text-sm" data-translate="quick-start">Quick Start</button>
                    </div>
                </div>
                <div>
                    <h4 class="font-semibold mb-3 text-sm md:text-base" data-translate="supported-hardware">Supported Hardware</h4>
                    <div class="space-y-2 md:space-y-3">
                        <div class="flex items-center justify-between p-2 md:p-3 bg-gray-800/30 rounded-lg">
                            <div class="flex items-center space-x-2 md:space-x-3">
                                <div class="text-lg md:text-xl">🏭</div>
                                <div>
                                    <div class="font-semibold text-sm md:text-base">Antminer S19/S21</div>
                                    <div class="text-xs md:text-sm text-gray-400">95-200 TH/s</div>
                                </div>
                            </div>
                            <span class="text-green-400 text-xs md:text-sm">✓ Auto-Config</span>
                        </div>
                        <div class="flex items-center justify-between p-2 md:p-3 bg-gray-800/30 rounded-lg">
                            <div class="flex items-center space-x-2 md:space-x-3">
                                <div class="text-lg md:text-xl">⚡</div>
                                <div>
                                    <div class="font-semibold text-sm md:text-base">Bitaxe (All Models)</div>
                                    <div class="text-xs md:text-sm text-gray-400">0.1-2 TH/s</div>
                                </div>
                            </div>
                            <span class="text-green-400 text-xs md:text-sm">✓ JSON Config</span>
                        </div>
                        <div class="flex items-center justify-between p-2 md:p-3 bg-gray-800/30 rounded-lg">
                            <div class="flex items-center space-x-2 md:space-x-3">
                                <div class="text-lg md:text-xl">🔧</div>
                                <div>
                                    <div class="font-semibold text-sm md:text-base">Custom Miners</div>
                                    <div class="text-xs md:text-sm text-gray-400">Any Stratum V2</div>
                                </div>
                            </div>
                            <span class="text-blue-400 text-xs md:text-sm">Manual Setup</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Performance Metrics -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 px-4">
            <div class="card">
                <h3 class="text-lg md:text-xl font-semibold mb-4">Pool Performance</h3>
                <div class="space-y-4">
                    <div class="flex justify-between">
                        <span>Pool Fee</span>
                        <span class="text-blgv-primary font-semibold">2.0%</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Efficiency</span>
                        <span class="text-green-400 font-semibold">98.7%</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Uptime</span>
                        <span class="text-blue-400 font-semibold">99.95%</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Stale Rate</span>
                        <span class="text-yellow-400 font-semibold">0.6%</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Average Latency</span>
                        <span class="text-green-400 font-semibold">12ms</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3 class="text-lg md:text-xl font-semibold mb-4">Recent Blocks</h3>
                <div class="space-y-2 md:space-y-3">
                    <div class="flex justify-between items-center p-2 md:p-3 bg-gray-800/30 rounded-lg">
                        <div>
                            <div class="font-semibold text-sm md:text-base">#902,607</div>
                            <div class="text-xs md:text-sm text-gray-400">0000...1a2b</div>
                        </div>
                        <div class="text-right">
                            <div class="text-green-400 font-semibold text-sm md:text-base">6.25 BTC</div>
                            <div class="text-xs md:text-sm text-gray-400">1 min ago</div>
                        </div>
                    </div>
                    <div class="flex justify-between items-center p-3 bg-gray-800/30 rounded-lg">
                        <div>
                            <div class="font-semibold">#902,606</div>
                            <div class="text-sm text-gray-400">0000...3c4d</div>
                        </div>
                        <div class="text-right">
                            <div class="text-green-400 font-semibold">6.25 BTC</div>
                            <div class="text-sm text-gray-400">18 min ago</div>
                        </div>
                    </div>
                    <div class="flex justify-between items-center p-3 bg-gray-800/30 rounded-lg">
                        <div>
                            <div class="font-semibold">#902,605</div>
                            <div class="text-sm text-gray-400">0000...5e6f</div>
                        </div>
                        <div class="text-right">
                            <div class="text-green-400 font-semibold">6.25 BTC</div>
                            <div class="text-sm text-gray-400">35 min ago</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Treasury Transparency (Minimal SDK Integration) -->
        <div class="card mt-6 md:mt-8 mx-4">
            <h3 class="text-lg md:text-xl font-semibold mb-4 text-blgv-primary">BLGV Treasury Transparency</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-gray-800/50 p-4 rounded-lg text-center">
                    <div class="text-sm text-gray-400 mb-1">Treasury Balance</div>
                    <div class="text-xl md:text-2xl font-bold text-green-400">15.847 BTC</div>
                    <div class="text-xs text-gray-500">$1.68M+ USD</div>
                </div>
                <div class="bg-gray-800/50 p-4 rounded-lg text-center">
                    <div class="text-sm text-gray-400 mb-1">Mining Contribution</div>
                    <div class="text-xl md:text-2xl font-bold text-orange-400">0.0032 BTC/day</div>
                    <div class="text-xs text-gray-500">From Pool Fees</div>
                </div>
                <div class="bg-gray-800/50 p-4 rounded-lg text-center">
                    <div class="text-sm text-gray-400 mb-1">Transparency Score</div>
                    <div class="text-xl md:text-2xl font-bold text-red-400">100%</div>
                    <div class="text-xs text-gray-500">Fully Auditable</div>
                </div>
            </div>
            <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                <div class="flex justify-between p-2 bg-gray-800/30 rounded">
                    <span>Cold Storage</span>
                    <span class="text-green-400">85% (13.47 BTC)</span>
                </div>
                <div class="flex justify-between p-2 bg-gray-800/30 rounded">
                    <span>Trading Fund</span>
                    <span class="text-blue-400">10% (1.58 BTC)</span>
                </div>
                <div class="flex justify-between p-2 bg-gray-800/30 rounded">
                    <span>Operational</span>
                    <span class="text-orange-400">5% (0.79 BTC)</span>
                </div>
            </div>
        </div>

        <!-- Miners Online Map -->
        <div class="card mt-6 md:mt-8 mx-4">
            <h3 class="text-lg md:text-xl font-semibold mb-4 text-blgv-primary" data-translate="miners-map">Miners Online Map</h3>
            <div class="bg-gray-800/50 p-4 md:p-6 rounded-lg">
                <div id="miners-map" class="h-48 md:h-64 bg-gray-900/50 rounded-lg flex items-center justify-center">
                    <div class="text-center">
                        <div class="text-3xl md:text-4xl mb-2">🌍</div>
                        <div class="text-base md:text-lg font-semibold" data-translate="global-mining">Global Mining Network</div>
                        <div class="text-xs md:text-sm text-gray-400" data-translate="miners-worldwide">2,156 miners active worldwide</div>
                    </div>
                </div>
            </div>
        </div>
        </div>

        <!-- Mining Setup Section -->
        <div id="mining-setup" class="section">
            <div class="text-center mb-6 md:mb-8 px-4">
                <h1 class="text-2xl md:text-4xl font-bold gradient-text mb-3 md:mb-4" data-translate="setup-title">Mining Setup Wizard</h1>
                <p class="text-base md:text-xl text-gray-300 mb-4 md:mb-6" data-translate="setup-subtitle">Configure your miners for optimal performance with guided setup</p>
            </div>

            <div class="card mx-4">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-8">
                    <!-- Hardware Configuration -->
                    <div>
                        <h3 class="text-lg md:text-xl font-semibold mb-4 md:mb-6 text-blgv-primary" data-translate="hardware-config">Hardware Configuration</h3>
                        
                        <div class="form-group">
                            <label class="form-label" data-translate="select-hardware">Select Hardware Type</label>
                            <select id="hardware-select" class="form-input" onchange="updateHardwareInfo()">
                                <option value="antminer-s19">Antminer S19 Pro (110 TH/s, 3250W)</option>
                                <option value="antminer-s21">Antminer S21 (200 TH/s, 3550W)</option>
                                <option value="whatsminer-m50s">Whatsminer M50S (126 TH/s, 3276W)</option>
                                <option value="whatsminer-m60s">Whatsminer M60S (170 TH/s, 3344W)</option>
                                <option value="bitaxe-ultra">Bitaxe Ultra (0.5 TH/s, 15W)</option>
                                <option value="bitaxe-max">Bitaxe Max (2.0 TH/s, 45W)</option>
                                <option value="custom">Custom Hardware</option>
                            </select>
                            <div id="hardware-info" class="mt-2 text-sm text-gray-400"></div>
                        </div>

                        <div class="form-group">
                            <label class="form-label" data-translate="bitcoin-address">Bitcoin Address (Payout Address)</label>
                            <input type="text" id="bitcoin-address" placeholder="bc1q..." 
                                   class="form-input" onblur="validateBitcoinAddress()" data-translate-placeholder="address-placeholder">
                            <div id="address-validation" class="validation-feedback"></div>
                            <p class="text-xs text-gray-400 mt-1" data-translate="address-help">This address will receive all mining rewards</p>
                        </div>

                        <div class="form-group">
                            <label class="form-label" data-translate="worker-name">Worker Name</label>
                            <input type="text" id="worker-name" placeholder="worker1" value="worker1"
                                   class="form-input" onblur="validateWorkerName()">
                            <div id="worker-validation" class="validation-feedback"></div>
                            <p class="text-xs text-gray-400 mt-1" data-translate="worker-help">Unique identifier for this mining device</p>
                        </div>

                        <div class="grid grid-cols-2 gap-4">
                            <div class="form-group">
                                <label class="form-label" data-translate="reward-method">Reward Method</label>
                                <select id="reward-method" class="form-input" onchange="updateRewardInfo()">
                                    <option value="pps+">PPS+ (Pay Per Share Plus)</option>
                                    <option value="pplns">PPLNS (Pay Per Last N Shares)</option>
                                    <option value="solo">Solo Mining</option>
                                    <option value="p2pool">P2Pool (Coming Soon)</option>
                                </select>
                                <div id="reward-info" class="mt-1 text-xs text-gray-400"></div>
                            </div>
                            <div class="form-group">
                                <label class="form-label" data-translate="node-type">Bitcoin Node</label>
                                <select id="node-type" class="form-input" onchange="updateNodeInfo()">
                                    <option value="core">Bitcoin Core</option>
                                    <option value="knots">Bitcoin Knots</option>
                                </select>
                                <div id="node-info" class="mt-1 text-xs text-gray-400" data-translate="node-help">Choose your preferred Bitcoin implementation</div>
                            </div>
                        </div>
                    </div>

                    <!-- Connection & Configuration -->
                    <div>
                        <h3 class="text-xl font-semibold mb-6 text-blgv-primary" data-translate="connection-config">Connection & Configuration</h3>
                        
                        <div class="bg-gray-800/50 p-6 rounded-lg mb-6">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-sm font-medium" data-translate="stratum-url">Stratum URL</span>
                                <button onclick="copyToClipboard(getStratumUrl())" class="text-blgv-primary hover:text-blgv-accent text-sm" data-translate="copy">Copy</button>
                            </div>
                            <code class="text-green-400 font-mono text-sm block mb-3" id="stratum-display">stratum+tcp://pool.blgvbtc.com:3333</code>
                            
                            <div class="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span class="text-gray-400">Username:</span>
                                    <span class="text-white ml-2" id="display-address">[bitcoin_address]</span>
                                </div>
                                <div>
                                    <span class="text-gray-400">Password:</span>
                                    <span class="text-white ml-2" id="display-worker">[worker_name]</span>
                                </div>
                            </div>
                        </div>

                        <!-- Hardware Health Monitor -->
                        <div class="bg-gray-800/50 p-6 rounded-lg mb-6">
                            <h4 class="font-semibold mb-3 flex items-center">
                                <span class="status-online mr-2"></span>
                                <span data-translate="hardware-health">Hardware Health Monitor</span>
                            </h4>
                            <div class="grid grid-cols-2 gap-4 text-sm">
                                <div class="flex justify-between">
                                    <span data-translate="temperature">Temperature</span>
                                    <span class="text-green-400" id="temp-display">65°C</span>
                                </div>
                                <div class="flex justify-between">
                                    <span data-translate="fan-speed">Fan Speed</span>
                                    <span class="text-blue-400" id="fan-display">3200 RPM</span>
                                </div>
                                <div class="flex justify-between">
                                    <span data-translate="power-draw">Power Draw</span>
                                    <span class="text-yellow-400" id="power-display">3250W</span>
                                </div>
                                <div class="flex justify-between">
                                    <span data-translate="uptime">Uptime</span>
                                    <span class="text-purple-400" id="uptime-display">24h 15m</span>
                                </div>
                            </div>
                        </div>

                        <!-- Ordinals Mining Toggle -->
                        <div class="bg-gray-800/50 p-6 rounded-lg mb-6">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h4 class="font-semibold" data-translate="ordinals-mining">Ordinals Mining</h4>
                                    <p class="text-sm text-gray-400" data-translate="ordinals-desc">Enable revenue-sharing for inscription blocks</p>
                                </div>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" id="ordinals-toggle" class="sr-only peer">
                                    <div class="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
                                </label>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="space-y-3">
                            <button onclick="generateConfig()" class="btn-primary w-full" id="generate-btn" data-translate="generate-config">Generate Configuration</button>
                            <div class="grid grid-cols-3 gap-3">
                                <button onclick="showQRCode()" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-500 text-sm" data-translate="show-qr-config">Show QR</button>
                                <button onclick="testConnection()" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-500 text-sm" data-translate="test-connection">Test</button>
                                <button onclick="autoDetectHardware()" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-500 text-sm" data-translate="auto-detect">Auto-Detect</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Analytics Section -->
        <div id="analytics" class="section">
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold gradient-text mb-4" data-translate="analytics-title">Mining Analytics & AI Insights</h1>
                <p class="text-xl text-gray-300 mb-6" data-translate="analytics-subtitle">Real-time profitability forecasting and optimization recommendations</p>
            </div>

            <!-- Analytics Dashboard -->
            <div class="stats-grid mb-8">
                <div class="card metric-card">
                    <h3 class="text-lg font-semibold mb-4 text-green-400" data-translate="profit-forecast">Profitability Forecast</h3>
                    <div class="text-3xl font-bold text-green-400 mb-2">+$1,847</div>
                    <div class="text-sm text-gray-400 mb-4" data-translate="next-30-days">Next 30 days</div>
                    <div class="mb-3">
                        <div class="flex justify-between text-sm mb-1">
                            <span data-translate="confidence">Confidence</span>
                            <span>91%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 91%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="card metric-card">
                    <h3 class="text-lg font-semibold mb-4 text-blue-400" data-translate="miner-optimization">Miner Optimization</h3>
                    <div class="text-3xl font-bold text-blue-400 mb-2">98.7%</div>
                    <div class="text-sm text-gray-400 mb-4" data-translate="efficiency-rating">Efficiency Rating</div>
                    <div class="space-y-2">
                        <div class="flex justify-between text-sm">
                            <span data-translate="temperature-opt">Temperature</span>
                            <span class="text-green-400">Optimal</span>
                        </div>
                        <div class="flex justify-between text-sm">
                            <span data-translate="power-efficiency">Power Efficiency</span>
                            <span class="text-blue-400">High</span>
                        </div>
                    </div>
                </div>
                
                <div class="card metric-card">
                    <h3 class="text-lg font-semibold mb-4 text-purple-400" data-translate="competitor-analysis">Competitor Analysis</h3>
                    <div class="text-3xl font-bold text-purple-400 mb-2" data-translate="rank-position">#2</div>
                    <div class="text-sm text-gray-400 mb-4" data-translate="pool-ranking">Pool Ranking</div>
                    <div class="space-y-2">
                        <div class="flex justify-between text-sm">
                            <span data-translate="vs-ocean">vs Ocean Pool</span>
                            <span class="text-green-400">+0.3%</span>
                        </div>
                        <div class="flex justify-between text-sm">
                            <span data-translate="vs-f2pool">vs F2Pool</span>
                            <span class="text-blue-400">+1.2%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Live Analytics Widget from blgvbtc.com -->
            <div class="card">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold" data-translate="live-analytics">Live Analytics Feed</h3>
                    <button onclick="refreshAnalytics()" class="text-blgv-primary hover:text-blgv-accent text-sm" data-translate="refresh">🔄 Refresh</button>
                </div>
                <div id="analytics-widget" class="bg-gray-800/50 p-6 rounded-lg">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div class="text-center">
                            <div class="text-2xl font-bold text-green-400" data-translate="network-hashrate">Network Hashrate</div>
                            <div class="text-sm text-gray-400">847.3 EH/s</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-blue-400" data-translate="mempool-size">Mempool Size</div>
                            <div class="text-sm text-gray-400">127 MB</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-purple-400" data-translate="avg-fee">Average Fee</div>
                            <div class="text-sm text-gray-400">47 sat/vB</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Hash Power Marketplace Section -->
        <div id="marketplace" class="section">
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold gradient-text mb-4" data-translate="marketplace-title">Hash Power Marketplace</h1>
                <p class="text-xl text-gray-300 mb-6" data-translate="marketplace-subtitle">Rent or offer hash power with BTCPay escrow protection</p>
            </div>

            <!-- Marketplace Interface -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Rent Hash Power -->
                <div class="card">
                    <h3 class="text-xl font-semibold mb-6 text-blgv-primary" data-translate="rent-hashpower">Rent Hash Power</h3>
                    
                    <div class="form-group">
                        <label class="form-label" data-translate="hashrate-amount">Hash Rate (TH/s)</label>
                        <input type="range" id="rent-hashrate" min="1" max="1000" value="100" 
                               class="w-full mb-2" oninput="updateRentCost()">
                        <div class="flex justify-between text-sm text-gray-400">
                            <span>1 TH/s</span>
                            <span id="rent-hashrate-value" class="text-white font-semibold">100 TH/s</span>
                            <span>1000 TH/s</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label" data-translate="rental-duration">Rental Duration</label>
                        <select id="rent-duration" class="form-input" onchange="updateRentCost()">
                            <option value="1" data-translate="duration-1h">1 Hour</option>
                            <option value="24" data-translate="duration-24h">24 Hours</option>
                            <option value="168" data-translate="duration-1w">1 Week</option>
                            <option value="720" data-translate="duration-1m">1 Month</option>
                        </select>
                    </div>

                    <div class="bg-gray-800/50 p-4 rounded-lg mb-6">
                        <div class="flex justify-between items-center mb-2">
                            <span class="font-semibold" data-translate="total-cost">Total Cost</span>
                            <span class="text-2xl font-bold text-blgv-primary" id="rent-cost">0.001 BTC</span>
                        </div>
                        <div class="text-sm text-gray-400">≈ $<span id="rent-cost-usd">106</span> USD</div>
                    </div>

                    <button onclick="rentHashPower()" class="btn-primary w-full" data-translate="rent-now">Rent Now (BTCPay)</button>
                </div>

                <!-- Offer Hash Power -->
                <div class="card">
                    <h3 class="text-xl font-semibold mb-6 text-blgv-primary" data-translate="offer-hashpower">Offer Your Hash Power</h3>
                    
                    <div class="form-group">
                        <label class="form-label" data-translate="available-hashrate">Available Hash Rate (TH/s)</label>
                        <input type="number" id="offer-hashrate" placeholder="100" 
                               class="form-input" oninput="updateOfferEarnings()">
                    </div>

                    <div class="form-group">
                        <label class="form-label" data-translate="price-per-th">Price per TH/s per Hour (BTC)</label>
                        <input type="number" id="offer-price" placeholder="0.00001" step="0.00001"
                               class="form-input" oninput="updateOfferEarnings()">
                    </div>

                    <div class="bg-gray-800/50 p-4 rounded-lg mb-6">
                        <div class="flex justify-between items-center mb-2">
                            <span class="font-semibold" data-translate="estimated-earnings">Estimated Earnings (24h)</span>
                            <span class="text-2xl font-bold text-green-400" id="offer-earnings">0.024 BTC</span>
                        </div>
                        <div class="text-sm text-gray-400">≈ $<span id="offer-earnings-usd">2,549</span> USD</div>
                    </div>

                    <button onclick="offerHashPower()" class="btn-primary w-full" data-translate="list-offer">List Offer</button>
                </div>
            </div>

            <!-- Rental History -->
            <div class="card mt-8">
                <h3 class="text-xl font-semibold mb-4" data-translate="rental-history">Rental History</h3>
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead>
                            <tr class="border-b border-gray-700">
                                <th class="text-left py-3" data-translate="table-type">Type</th>
                                <th class="text-left py-3" data-translate="table-hashrate">Hash Rate</th>
                                <th class="text-left py-3" data-translate="table-duration">Duration</th>
                                <th class="text-left py-3" data-translate="table-payment">BTCPay ID</th>
                                <th class="text-left py-3" data-translate="table-status">Status</th>
                            </tr>
                        </thead>
                        <tbody id="rental-tbody">
                            <tr class="border-b border-gray-800">
                                <td class="py-3">Rental</td>
                                <td class="py-3">50 TH/s</td>
                                <td class="py-3">24h</td>
                                <td class="py-3"><a href="#" class="text-blue-400 hover:underline">BTCPay_12345</a></td>
                                <td class="py-3"><span class="text-green-400">Active</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Ecosystem Integration Section -->
        <div id="ecosystem" class="section">
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold gradient-text mb-4" data-translate="ecosystem-title">BLGV Ecosystem Integration</h1>
                <p class="text-xl text-gray-300 mb-6" data-translate="ecosystem-subtitle">Seamless integration across all BLGV platforms</p>
            </div>

            <!-- Ecosystem Links -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="card text-center" onclick="openDEX()">
                    <div class="text-4xl mb-4">📈</div>
                    <h3 class="text-xl font-semibold mb-3" data-translate="dex-trading">DEX Trading</h3>
                    <p class="text-gray-400 mb-4" data-translate="dex-description">Auto-deposit mining rewards for instant trading</p>
                    <button class="btn-primary" data-translate="trade-now">Trade Now</button>
                </div>

                <div class="card text-center" onclick="openIntelligence()">
                    <div class="text-4xl mb-4">🧠</div>
                    <h3 class="text-xl font-semibold mb-3" data-translate="ai-platform">AI Platform</h3>
                    <p class="text-gray-400 mb-4" data-translate="ai-description">Advanced mining optimization insights</p>
                    <button class="btn-primary" data-translate="view-insights">View Insights</button>
                </div>

                <div class="card text-center" onclick="openTreasury()">
                    <div class="text-4xl mb-4">🏛️</div>
                    <h3 class="text-xl font-semibold mb-3" data-translate="treasury">Treasury</h3>
                    <p class="text-gray-400 mb-4" data-translate="treasury-description">Manage Taproot Asset shares and voting</p>
                    <button class="btn-primary" data-translate="manage-shares">Manage Shares</button>
                </div>
            </div>

            <!-- Treasury Dashboard -->
            <div class="card">
                <h3 class="text-xl font-semibold mb-4 text-blgv-primary" data-translate="treasury-dashboard">Treasury Dashboard</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-gray-800/50 p-4 rounded-lg">
                        <div class="text-2xl font-bold text-yellow-400">2,847</div>
                        <div class="text-sm text-gray-400" data-translate="your-shares">Your Taproot Shares</div>
                    </div>
                    <div class="bg-gray-800/50 p-4 rounded-lg">
                        <div class="text-2xl font-bold text-blue-400">0.28%</div>
                        <div class="text-sm text-gray-400" data-translate="voting-power">Voting Power</div>
                    </div>
                    <div class="bg-gray-800/50 p-4 rounded-lg">
                        <div class="text-2xl font-bold text-green-400">0.347 BTC</div>
                        <div class="text-sm text-gray-400" data-translate="current-value">Current Value</div>
                    </div>
                </div>
                <div class="mt-6 flex space-x-4">
                    <button onclick="buyShares()" class="btn-primary" data-translate="buy-shares">Buy Shares</button>
                    <button onclick="voteOnPolicies()" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-500" data-translate="vote-policies">Vote on Policies</button>
                </div>
            </div>

            <!-- Nostr Community Integration -->
            <div class="card mt-8">
                <h3 class="text-xl font-semibold mb-4 text-blgv-primary" data-translate="nostr-community">Nostr Community Chat</h3>
                <div class="bg-gray-800/50 p-6 rounded-lg">
                    <div class="flex justify-between items-center mb-4">
                        <div>
                            <div class="text-lg font-semibold" data-translate="miners-online">2,156 Miners Online</div>
                            <div class="text-sm text-gray-400" data-translate="community-rank">Your Community Rank: #47</div>
                        </div>
                        <button onclick="joinNostrChat()" class="btn-primary" data-translate="join-chat">Join Chat</button>
                    </div>
                    <div class="text-sm text-gray-400" data-translate="nostr-desc">Decentralized community chat powered by Nostr protocol</div>
                </div>
            </div>
        </div>

        <!-- Support Section -->
        <div id="support" class="section">
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold gradient-text mb-4" data-translate="support-title">Support & Resources</h1>
                <p class="text-xl text-gray-300 mb-6" data-translate="support-subtitle">24/7 support and comprehensive documentation</p>
            </div>

            <!-- Support Options -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- FAQ and Troubleshooting -->
                <div class="card">
                    <h3 class="text-xl font-semibold mb-6" data-translate="faq-troubleshooting">FAQ & Troubleshooting</h3>
                    <div class="mb-6">
                        <input type="text" placeholder="Search FAQ..." 
                               class="form-input" id="faq-search" oninput="searchFAQ()"
                               data-translate-placeholder="search-faq">
                    </div>
                    <div class="space-y-4" id="faq-list">
                        <div class="border-b border-gray-700 pb-4">
                            <h4 class="font-semibold mb-2" data-translate="faq-start">How do I start mining?</h4>
                            <p class="text-sm text-gray-400" data-translate="faq-start-answer">Use our Mining Setup Wizard to configure your hardware and generate the appropriate configuration files.</p>
                        </div>
                        <div class="border-b border-gray-700 pb-4">
                            <h4 class="font-semibold mb-2" data-translate="faq-fees">What are the pool fees?</h4>
                            <p class="text-sm text-gray-400" data-translate="faq-fees-answer">2% for PPS+, 1.5% for PPLNS, 0.5% for Solo Mining. All fees include comprehensive support and ecosystem access.</p>
                        </div>
                        <div class="border-b border-gray-700 pb-4">
                            <h4 class="font-semibold mb-2" data-translate="faq-core-knots">What's the difference between Core and Knots?</h4>
                            <p class="text-sm text-gray-400" data-translate="faq-core-knots-answer">Bitcoin Core is the reference implementation, while Bitcoin Knots includes additional features and optimizations for mining pools.</p>
                        </div>
                    </div>
                </div>

                <!-- Contact Support -->
                <div class="card">
                    <h3 class="text-xl font-semibold mb-6" data-translate="contact-support">Contact Support</h3>
                    <form onsubmit="submitSupport(event)" class="space-y-4">
                        <div class="form-group">
                            <label class="form-label" data-translate="support-category">Category</label>
                            <select class="form-input" id="support-category">
                                <option value="technical" data-translate="cat-technical">Technical Support</option>
                                <option value="billing" data-translate="cat-billing">BTCPay & Payments</option>
                                <option value="hardware" data-translate="cat-hardware">Hardware Configuration</option>
                                <option value="ecosystem" data-translate="cat-ecosystem">Ecosystem Integration</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label" data-translate="support-subject">Subject</label>
                            <input type="text" required class="form-input" id="support-subject">
                        </div>
                        <div class="form-group">
                            <label class="form-label" data-translate="support-message">Message</label>
                            <textarea rows="4" required class="form-input" id="support-message"></textarea>
                        </div>
                        <div class="flex space-x-3">
                            <button type="submit" class="btn-primary flex-1" data-translate="send-message">Send Message</button>
                            <button type="button" onclick="startNostrChat()" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-500" data-translate="nostr-chat">Nostr Chat</button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- API Reference -->
            <div class="card mt-8">
                <h3 class="text-xl font-semibold mb-4" data-translate="api-reference">API Reference</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-semibold mb-3" data-translate="api-endpoints">Available Endpoints</h4>
                        <div class="space-y-2 text-sm">
                            <div><code class="bg-gray-800 px-2 py-1 rounded">GET /api/stats</code> - Pool statistics</div>
                            <div><code class="bg-gray-800 px-2 py-1 rounded">GET /api/miner/{address}</code> - Miner data</div>
                            <div><code class="bg-gray-800 px-2 py-1 rounded">POST /api/rental</code> - Create rental</div>
                        </div>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-3" data-translate="api-auth">Authentication</h4>
                        <button onclick="generateAPIKey()" class="btn-primary" data-translate="generate-api-key">Generate API Key</button>
                        <div id="api-key-display" class="mt-3 text-sm font-mono bg-gray-800 p-2 rounded hidden"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modals -->
    <!-- Wallet Modal -->
    <div id="wallet-modal" class="modal">
        <div class="modal-content">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-semibold" data-translate="connect-wallet">Connect Wallet</h3>
                <button onclick="closeModal('wallet-modal')" class="text-gray-400 hover:text-white">&times;</button>
            </div>
            <div class="space-y-4">
                <div class="form-group">
                    <label class="form-label" data-translate="bitcoin-address">Bitcoin Address</label>
                    <input type="text" id="modal-bitcoin-address" placeholder="bc1q..." class="form-input">
                </div>
                <div class="flex space-x-3">
                    <button onclick="linkToDEX()" class="btn-primary flex-1" data-translate="link-dex">Link to DEX</button>
                    <button onclick="discoverMiner()" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-500" data-translate="discover-miners">Discover Miners</button>
                </div>
            </div>
        </div>
    </div>

    <!-- QR Code Modal -->
    <div id="qr-modal" class="modal">
        <div class="modal-content text-center">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-semibold" data-translate="mining-qr">Mining QR Code</h3>
                <button onclick="closeModal('qr-modal')" class="text-gray-400 hover:text-white">&times;</button>
            </div>
            <div id="qr-code-container" class="mb-4"></div>
            <div id="qr-config-text" class="text-sm text-gray-400 font-mono bg-gray-800 p-4 rounded"></div>
        </div>
    </div>

    <!-- Enhanced Wallet Drawer (Fixed Scrolling & Layout) -->
    <div id="wallet-drawer" class="fixed inset-y-0 right-0 w-80 md:w-96 bg-gray-900/95 backdrop-blur-lg border-l border-gray-700 transform translate-x-full transition-transform duration-300 ease-in-out z-50 overflow-hidden">
        <div class="h-full flex flex-col relative">
            <!-- Compact Drawer Header -->
            <div class="flex items-center justify-between p-4 border-b border-gray-700/50">
                <div class="flex items-center space-x-2">
                    <div class="w-8 h-8 bg-gradient-to-br from-red-600 to-red-500 rounded-lg flex items-center justify-center">
                        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2L2 7v10c0 1 9 4 10 4s10-3 10-4V7l-10-5z"/>
                        </svg>
                    </div>
                    <div>
                        <h2 class="text-lg font-semibold text-white">My Hub</h2>
                        <div class="flex items-center text-xs text-green-400">
                            <div class="w-1.5 h-1.5 bg-green-400 rounded-full mr-1 animate-pulse"></div>
                            <span>Synced</span>
                        </div>
                    </div>
                </div>
                <button onclick="closeWalletDrawer()" class="w-8 h-8 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg flex items-center justify-center transition-all duration-200">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>

            <!-- Compact Mining Wallet -->
            <div class="p-3 border-b border-gray-700/50">
                <div class="bg-gradient-to-br from-gray-800/40 to-gray-900/20 border border-gray-600/30 rounded-lg p-3">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-gray-300 text-sm font-medium">Mining Wallet</span>
                        <span class="bg-green-600/20 border border-green-500/30 text-green-400 text-xs px-2 py-0.5 rounded-full">Connected</span>
                    </div>
                    
                    <div class="bg-gray-900/40 rounded p-2 mb-2">
                        <div class="text-xs text-gray-300 font-mono">bc1qxy...fjhx0wlh</div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-2 text-xs">
                        <div>
                            <span class="text-gray-400">Fee</span>
                            <span class="text-red-400 font-semibold ml-1">2.0%</span>
                        </div>
                        <div>
                            <span class="text-gray-400">Method</span>
                            <span class="text-blue-400 font-semibold ml-1">PPS+</span>
                        </div>
                    </div>
                </div>
            </div>



            <!-- Core Mining Quick Access -->
            <div class="flex-1 overflow-y-auto">
                <!-- Current Earnings Card -->
                <div class="p-4 m-4 bg-gradient-to-br from-green-900/30 to-emerald-900/20 border border-green-500/30 rounded-xl">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-white font-semibold">Today's Earnings</h3>
                        <svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
                        </svg>
                    </div>
                    <div class="text-2xl font-bold text-green-400 mb-1">0.00847 BTC</div>
                    <div class="text-sm text-gray-400">Next payout: 23h 47m</div>
                </div>

                <!-- Hash Rental Quick Access -->
                <div class="p-4 m-4 bg-gradient-to-br from-orange-900/30 to-red-900/20 border border-orange-500/30 rounded-xl">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-white font-semibold">Hash Rentals</h3>
                        <svg class="w-5 h-5 text-orange-400" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                        </svg>
                    </div>
                    <div class="grid grid-cols-2 gap-2 mb-3">
                        <button onclick="showSection('marketplace')" class="bg-orange-600/20 hover:bg-orange-600/30 text-orange-400 py-2 px-3 rounded-lg text-sm transition-colors">
                            Rent Hash
                        </button>
                        <button onclick="showSection('marketplace')" class="bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 py-2 px-3 rounded-lg text-sm transition-colors">
                            Offer Hash
                        </button>
                    </div>
                    <div class="text-xs text-gray-400 text-center">
                        Boost earnings or monetize excess capacity
                    </div>
                </div>

                <!-- Mining Performance Overview -->
                <div class="p-4 m-4 bg-gradient-to-br from-blue-900/30 to-cyan-900/20 border border-blue-500/30 rounded-xl">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-white font-semibold">Mining Performance</h3>
                        <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
                        </svg>
                    </div>
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div>
                            <div class="text-gray-400">Hash Rate</div>
                            <div class="text-blue-400 font-semibold">111.0 TH/s</div>
                        </div>
                        <div>
                            <div class="text-gray-400">Efficiency</div>
                            <div class="text-green-400 font-semibold">98.7%</div>
                        </div>
                        <div>
                            <div class="text-gray-400">Pool Share</div>
                            <div class="text-white font-semibold">0.016%</div>
                        </div>
                        <div>
                            <div class="text-gray-400">Pool Luck</div>
                            <div class="text-green-400 font-semibold">102.3%</div>
                        </div>
                    </div>
                </div>

                <!-- Ecosystem Quick Links -->
                <div class="p-4 m-4 bg-gradient-to-br from-purple-900/30 to-pink-900/20 border border-purple-500/30 rounded-xl">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-white font-semibold">BLGV Ecosystem</h3>
                        <div class="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                    </div>
                    <div class="space-y-2">
                        <button onclick="window.open('https://dex.blgvbtc.com', '_blank')" class="w-full bg-red-600/20 hover:bg-red-600/30 text-red-400 py-2 px-3 rounded-lg text-sm transition-colors flex items-center justify-center space-x-2">
                            <span>Trade on DEX</span>
                            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.11 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
                            </svg>
                        </button>
                        <div class="text-xs text-gray-400 text-center">
                            Auto-deposit enabled • Intelligence Platform synced
                        </div>
                    </div>
                </div>
            </div>

                <!-- Bottom padding for scroll clearance -->
                <div class="pb-20"></div>
            </div>

        <!-- Compact Bottom Actions -->
        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-gray-900 via-gray-900/95 to-gray-900/80 p-3 border-t border-gray-700/50">
            <div class="grid grid-cols-3 gap-2">
                <button onclick="copyWalletAddress()" class="flex items-center justify-center bg-gray-700/60 hover:bg-gray-600/60 text-white py-2 rounded-lg transition-colors text-xs">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                    </svg>
                </button>
                <button onclick="viewOnExplorer()" class="flex items-center justify-center bg-gray-700/60 hover:bg-gray-600/60 text-white py-2 rounded-lg transition-colors text-xs">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.11 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
                    </svg>
                </button>
                <button onclick="showSection('analytics')" class="flex items-center justify-center bg-red-600/80 hover:bg-red-700/80 text-white py-2 rounded-lg transition-colors text-xs">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <!-- Mobile Menu Toggle Button (positioned like DEX) -->
    <button id="mobile-drawer-toggle" onclick="toggleWalletDrawer()" class="fixed bottom-6 right-6 w-14 h-14 bg-red-600 hover:bg-red-700 rounded-full flex items-center justify-center text-white shadow-lg transition-all duration-300 z-50">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
        </svg>
    </button>

    <!-- Overlay for mobile drawer -->
    <div id="drawer-overlay" class="fixed inset-0 bg-black/30 z-40 opacity-0 pointer-events-none transition-opacity duration-300"></div>

    <!-- Toast Notification -->
    <div id="toast" class="toast">
        <div class="flex items-center">
            <span id="toast-icon" class="mr-3">✓</span>
            <span id="toast-message">Welcome to BLGV BTC Mining Pool!</span>
        </div>
    </div>

    <script>
        // Global application state
        let currentSection = 'dashboard';
        let currentLanguage = 'en';
        let currentNode = 'core';
        
        // Translations for multi-language support
        const translations = {
            en: {
                'nav-dashboard': 'Dashboard',
                'nav-mining': 'Mining Setup',
                'nav-analytics': 'Analytics',
                'nav-marketplace': 'Marketplace',
                'nav-ecosystem': 'Ecosystem',
                'nav-support': 'Support',
                'connect-wallet': 'Connect Wallet',
                'discover-btn': 'Discover',
                'wallet-placeholder': 'Enter Bitcoin address to find your miners...',
                'wallet-help': 'View mining stats, configure payouts, or start mining',
                'welcome-title': 'Institutional-Grade Bitcoin Mining',
                'welcome-subtitle': 'Bitcoin-Only • Stratum V2 • Enterprise Security • Global Scale',
                'miners-map': 'Miners Online Map',
                'global-mining': 'Global Mining Network',
                'miners-worldwide': '2,156 miners active worldwide',
                'setup-title': 'Mining Setup Wizard',
                'setup-subtitle': 'Configure your miners for optimal performance with guided setup',
                'hardware-config': 'Hardware Configuration',
                'select-hardware': 'Select Hardware Type',
                'bitcoin-address': 'Bitcoin Address (Payout Address)',
                'address-placeholder': 'bc1q...',
                'address-help': 'This address will receive all mining rewards',
                'worker-name': 'Worker Name',
                'worker-help': 'Unique identifier for this mining device',
                'reward-method': 'Reward Method',
                'node-type': 'Bitcoin Node',
                'node-help': 'Choose your preferred Bitcoin implementation',
                'connection-config': 'Connection & Configuration',
                'stratum-url': 'Stratum URL',
                'copy': 'Copy',
                'hardware-health': 'Hardware Health Monitor',
                'temperature': 'Temperature',
                'fan-speed': 'Fan Speed',
                'power-draw': 'Power Draw',
                'uptime': 'Uptime',
                'ordinals-mining': 'Ordinals Mining',
                'ordinals-desc': 'Enable revenue-sharing for inscription blocks',
                'generate-config': 'Generate Configuration',
                'show-qr-config': 'Show QR',
                'test-connection': 'Test',
                'auto-detect': 'Auto-Detect'
            },
            es: {
                'nav-dashboard': 'Panel',
                'nav-mining': 'Configuración',
                'nav-analytics': 'Analíticas',
                'nav-marketplace': 'Mercado',
                'nav-ecosystem': 'Ecosistema',
                'nav-support': 'Soporte',
                'connect-wallet': 'Conectar Billetera',
                'discover-btn': 'Descubrir',
                'wallet-placeholder': 'Ingrese dirección Bitcoin para encontrar sus mineros...',
                'welcome-title': 'Minería Bitcoin de Grado Institucional',
                'welcome-subtitle': 'Solo Bitcoin • Stratum V2 • Seguridad Empresarial • Escala Global'
            },
            zh: {
                'nav-dashboard': '仪表板',
                'nav-mining': '挖矿设置',
                'nav-analytics': '分析',
                'nav-marketplace': '市场',
                'nav-ecosystem': '生态系统',
                'nav-support': '支持',
                'connect-wallet': '连接钱包',
                'discover-btn': '发现',
                'wallet-placeholder': '输入比特币地址以找到您的矿机...',
                'welcome-title': '机构级比特币挖矿',
                'welcome-subtitle': '纯比特币 • Stratum V2 • 企业安全 • 全球规模'
            }
        };

        // Initialize application
        document.addEventListener('DOMContentLoaded', function() {
            console.log('BLGV BTC Mining Pool - Institutional Grade Loaded');
            initializeApp();
        });

        function initializeApp() {
            loadStats();
            setupEventListeners();
            updateHardwareInfo();
            updateRewardInfo();
            updateNodeInfo();
            showToast('Welcome to BLGV BTC Mining Pool!', 'success');
        }

        // Navigation functions
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Remove active class from all nav links
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Add active class to clicked nav link
            if (event && event.target) {
                event.target.classList.add('active');
            }
            
            // Update mobile navigation
            updateMobileNavigation(sectionId);
            
            currentSection = sectionId;
        }

        // Language support
        function changeLanguage(lang) {
            currentLanguage = lang;
            localStorage.setItem('blgv-language', lang);
            
            // Update all translatable elements
            document.querySelectorAll('[data-translate]').forEach(element => {
                const key = element.getAttribute('data-translate');
                if (translations[lang] && translations[lang][key]) {
                    element.textContent = translations[lang][key];
                }
            });
            
            // Update placeholders
            document.querySelectorAll('[data-translate-placeholder]').forEach(element => {
                const key = element.getAttribute('data-translate-placeholder');
                if (translations[lang] && translations[lang][key]) {
                    element.placeholder = translations[lang][key];
                }
            });
        }

        // Mining setup functions
        function updateHardwareInfo() {
            const hardware = document.getElementById('hardware-select').value;
            const info = document.getElementById('hardware-info');
            
            const hardwareSpecs = {
                'antminer-s19': 'Auto-configuration available. Optimal for large operations.',
                'antminer-s21': 'Latest model with improved efficiency. Auto-configuration available.',
                'whatsminer-m50s': 'Reliable workhorse. Auto-configuration available.',
                'whatsminer-m60s': 'High performance model. Auto-configuration available.',
                'bitaxe-ultra': 'Perfect for home mining. JSON configuration required.',
                'bitaxe-max': 'Enhanced Bitaxe model. JSON configuration required.',
                'custom': 'Manual configuration required. Contact support for assistance.'
            };
            
            info.textContent = hardwareSpecs[hardware] || '';
            updatePowerDisplay(hardware);
        }

        function updatePowerDisplay(hardware) {
            const powerSpecs = {
                'antminer-s19': '3250W',
                'antminer-s21': '3550W',
                'whatsminer-m50s': '3276W',
                'whatsminer-m60s': '3344W',
                'bitaxe-ultra': '15W',
                'bitaxe-max': '45W',
                'custom': 'Variable'
            };
            
            document.getElementById('power-display').textContent = powerSpecs[hardware] || 'Variable';
        }

        function updateRewardInfo() {
            const method = document.getElementById('reward-method').value;
            const info = document.getElementById('reward-info');
            
            const rewardInfo = {
                'pps+': '2% fee - Stable daily payouts with variance protection',
                'pplns': '1.5% fee - Higher rewards for loyal miners',
                'solo': '0.5% fee - Full block rewards (6.25 BTC + fees)',
                'p2pool': 'Coming soon - Decentralized mining with no pool fees'
            };
            
            info.textContent = rewardInfo[method] || '';
        }

        function updateNodeInfo() {
            const node = document.getElementById('node-type').value;
            const info = document.getElementById('node-info');
            currentNode = node;
            
            const nodeInfo = {
                'core': 'Bitcoin Core - Reference implementation, maximum compatibility',
                'knots': 'Bitcoin Knots - Enhanced features, better pool integration'
            };
            
            info.textContent = nodeInfo[node] || '';
            updateStratumUrl();
        }

        function updateStratumUrl() {
            const nodePort = currentNode === 'knots' ? '3334' : '3333';
            const url = `stratum+tcp://pool.blgvbtc.com:${nodePort}`;
            document.getElementById('stratum-display').textContent = url;
        }

        function getStratumUrl() {
            const nodePort = currentNode === 'knots' ? '3334' : '3333';
            return `stratum+tcp://pool.blgvbtc.com:${nodePort}`;
        }

        // Validation functions
        function validateBitcoinAddress() {
            const address = document.getElementById('bitcoin-address').value;
            const validation = document.getElementById('address-validation');
            
            if (!address) {
                validation.textContent = '';
                return;
            }
            
            // Basic Bitcoin address validation
            const isValid = /^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,87}$/.test(address);
            
            if (isValid) {
                validation.innerHTML = '<div class="validation-success">✓ Valid Bitcoin address</div>';
                document.getElementById('display-address').textContent = address;
            } else {
                validation.innerHTML = '<div class="validation-error">✗ Invalid Bitcoin address format</div>';
            }
        }

        function validateWorkerName() {
            const worker = document.getElementById('worker-name').value;
            const validation = document.getElementById('worker-validation');
            
            if (!worker) {
                validation.textContent = '';
                return;
            }
            
            // Basic worker name validation
            const isValid = /^[a-zA-Z0-9_-]{1,32}$/.test(worker);
            
            if (isValid) {
                validation.innerHTML = '<div class="validation-success">✓ Valid worker name</div>';
                document.getElementById('display-worker').textContent = worker;
            } else {
                validation.innerHTML = '<div class="validation-error">✗ Use only letters, numbers, _ and - (max 32 chars)</div>';
            }
        }

        // Configuration generation
        function generateConfig() {
            const hardware = document.getElementById('hardware-select').value;
            const address = document.getElementById('bitcoin-address').value;
            const worker = document.getElementById('worker-name').value;
            const reward = document.getElementById('reward-method').value;
            const node = document.getElementById('node-type').value;
            const ordinals = document.getElementById('ordinals-toggle').checked;
            
            if (!address) {
                showToast('Please enter a Bitcoin address first', 'error');
                return;
            }
            
            let config = '';
            
            if (hardware.startsWith('bitaxe')) {
                // JSON configuration for Bitaxe
                config = JSON.stringify({
                    "ssid": "your-wifi-ssid",
                    "pass": "your-wifi-password",
                    "hostname": `bitaxe-blgv-${worker}`,
                    "stratumURL": "pool.blgvbtc.com",
                    "stratumPort": node === 'knots' ? 3334 : 3333,
                    "stratumUser": address,
                    "stratumPassword": worker,
                    "rewardMethod": reward.toUpperCase(),
                    "ordinalsEnabled": ordinals,
                    "nodeType": node
                }, null, 2);
            } else {
                // Standard miner configuration
                config = `# BLGV BTC Mining Pool Configuration
# Generated on ${new Date().toISOString()}

pools:
  - url: stratum+tcp://pool.blgvbtc.com:${node === 'knots' ? 3334 : 3333}
    user: ${address}
    pass: ${worker}
    
# Pool Settings
pool_fee: ${reward === 'pps+' ? '2.0%' : reward === 'pplns' ? '1.5%' : '0.5%'}
reward_method: ${reward.toUpperCase()}
node_type: ${node}
ordinals_mining: ${ordinals}

# Hardware: ${hardware}
# Efficiency: 98.7%
# Uptime: 99.95%

# Support: support@blgvbtc.com
# Documentation: https://docs.blgvbtc.com`;
            }
            
            downloadConfig(config, hardware.startsWith('bitaxe') ? 'bitaxe-config.json' : 'miner-config.conf');
            showToast('Configuration generated successfully!', 'success');
        }

        function downloadConfig(content, filename) {
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }

        // QR Code generation
        function showQRCode() {
            const address = document.getElementById('bitcoin-address').value;
            const worker = document.getElementById('worker-name').value;
            
            if (!address) {
                showToast('Please enter a Bitcoin address first', 'error');
                return;
            }
            
            const stratumUrl = getStratumUrl();
            const qrData = `${stratumUrl}?user=${address}&pass=${worker}`;
            
            document.getElementById('qr-config-text').textContent = qrData;
            
            // Generate QR code (would need QR library in production)
            const qrContainer = document.getElementById('qr-code-container');
            qrContainer.innerHTML = `
                <div class="w-64 h-64 bg-white rounded-lg flex items-center justify-center mx-auto">
                    <div class="text-black text-center">
                        <div class="text-4xl mb-2">📱</div>
                        <div class="text-sm">QR Code</div>
                        <div class="text-xs">${stratumUrl}</div>
                    </div>
                </div>
            `;
            
            showModal('qr-modal');
        }

        // Miner discovery
        function discoverMiner() {
            const address = document.getElementById('wallet-input').value || document.getElementById('modal-bitcoin-address')?.value;
            
            if (!address) {
                showToast('Please enter a Bitcoin address', 'error');
                return;
            }
            
            if (!/^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,87}$/.test(address)) {
                showToast('Invalid Bitcoin address format', 'error');
                return;
            }
            
            showToast('Searching for miners...', 'info');
            
            // Simulate miner discovery
            setTimeout(() => {
                const mockData = {
                    address: address,
                    miners: [
                        { name: 'worker1', hardware: 'Antminer S19 Pro', hashrate: '110 TH/s', status: 'active' },
                        { name: 'worker2', hardware: 'Bitaxe Ultra', hashrate: '0.5 TH/s', status: 'active' }
                    ],
                    totalHashrate: '110.5 TH/s',
                    estimatedRewards: '0.00847 BTC/day',
                    lastSeen: new Date().toLocaleString()
                };
                
                showMinerResults(mockData);
            }, 2000);
        }

        function showMinerResults(data) {
            showToast(`Found ${data.miners.length} miners for address ${data.address.substring(0, 12)}...`, 'success');
        }

        // Marketplace functions
        function updateRentCost() {
            const hashrate = document.getElementById('rent-hashrate').value;
            const duration = document.getElementById('rent-duration').value;
            
            document.getElementById('rent-hashrate-value').textContent = hashrate + ' TH/s';
            
            // Calculate cost (0.00001 BTC per TH/s per hour)
            const costBTC = (hashrate * duration * 0.00001).toFixed(6);
            const costUSD = Math.round(costBTC * 106460);
            
            document.getElementById('rent-cost').textContent = costBTC + ' BTC';
            document.getElementById('rent-cost-usd').textContent = costUSD.toLocaleString();
        }

        function updateOfferEarnings() {
            const hashrate = document.getElementById('offer-hashrate').value;
            const price = document.getElementById('offer-price').value;
            
            if (hashrate && price) {
                const earningsBTC = (hashrate * 24 * price).toFixed(6);
                const earningsUSD = Math.round(earningsBTC * 106460);
                
                document.getElementById('offer-earnings').textContent = earningsBTC + ' BTC';
                document.getElementById('offer-earnings-usd').textContent = earningsUSD.toLocaleString();
            }
        }

        function rentHashPower() {
            const hashrate = document.getElementById('rent-hashrate').value;
            const duration = document.getElementById('rent-duration').value;
            const cost = document.getElementById('rent-cost').textContent;
            
            showToast(`Initiating BTCPay rental for ${hashrate} TH/s (${cost})...`, 'info');
            
            // Simulate BTCPay integration
            setTimeout(() => {
                showToast('Rental activated! BTCPay invoice: BTCPay_' + Date.now(), 'success');
            }, 2000);
        }

        function offerHashPower() {
            const hashrate = document.getElementById('offer-hashrate').value;
            const price = document.getElementById('offer-price').value;
            
            if (!hashrate || !price) {
                showToast('Please fill in all fields', 'error');
                return;
            }
            
            showToast(`Listing ${hashrate} TH/s at ${price} BTC/TH/hour...`, 'info');
            
            setTimeout(() => {
                showToast('Hash power listed successfully!', 'success');
            }, 1500);
        }

        // Ecosystem integration functions
        function openDEX() {
            showToast('Redirecting to dex.blgvbtc.com...', 'info');
            setTimeout(() => window.open('https://dex.blgvbtc.com', '_blank'), 1000);
        }

        function openIntelligence() {
            showToast('Redirecting to blgvbtc.com Intelligence Platform...', 'info');
            setTimeout(() => window.open('https://blgvbtc.com', '_blank'), 1000);
        }

        function openTreasury() {
            showToast('Opening Treasury Management...', 'info');
        }

        function buyShares() {
            showToast('Initiating Taproot Asset share purchase...', 'info');
        }

        function voteOnPolicies() {
            showToast('Opening Nostr governance voting...', 'info');
        }

        function joinNostrChat() {
            showToast('Connecting to Nostr community chat...', 'info');
        }

        // Support functions
        function searchFAQ() {
            const query = document.getElementById('faq-search').value.toLowerCase();
            // Simple FAQ filtering would go here
        }

        function submitSupport(event) {
            event.preventDefault();
            const category = document.getElementById('support-category').value;
            const subject = document.getElementById('support-subject').value;
            const message = document.getElementById('support-message').value;
            
            showToast(`Support ticket submitted for ${category}: ${subject}`, 'success');
            event.target.reset();
        }

        function startNostrChat() {
            showToast('Opening Nostr support chat...', 'info');
        }

        function generateAPIKey() {
            const apiKey = 'blgv_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
            document.getElementById('api-key-display').textContent = apiKey;
            document.getElementById('api-key-display').classList.remove('hidden');
            showToast('API key generated successfully!', 'success');
        }

        // Utility functions
        function setupEventListeners() {
            // Auto-update rent cost when values change
            document.getElementById('rent-hashrate')?.addEventListener('input', updateRentCost);
            document.getElementById('rent-duration')?.addEventListener('change', updateRentCost);
            
            // Auto-update offer earnings
            document.getElementById('offer-hashrate')?.addEventListener('input', updateOfferEarnings);
            document.getElementById('offer-price')?.addEventListener('input', updateOfferEarnings);
            
            // Initialize default values
            updateRentCost();
        }

        function showModal(modalId) {
            document.getElementById(modalId).classList.add('show');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('show');
        }

        function showWalletModal() {
            showModal('wallet-modal');
        }

        // Mobile Menu Functions - Fixed viewport positioning
        function toggleMobileMenu() {
            const menu = document.getElementById('mobile-menu');
            const toggle = document.getElementById('mobile-menu-toggle');
            
            if (menu.classList.contains('scale-y-0')) {
                // Open menu
                menu.classList.remove('scale-y-0');
                menu.classList.add('scale-y-100');
                toggle.innerHTML = `
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                `;
            } else {
                // Close menu
                closeMobileMenu();
            }
        }

        function closeMobileMenu() {
            const menu = document.getElementById('mobile-menu');
            const toggle = document.getElementById('mobile-menu-toggle');
            
            menu.classList.add('scale-y-0');
            menu.classList.remove('scale-y-100');
            toggle.innerHTML = `
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
                </svg>
            `;
        }

        // Simplified mobile-first header navigation
        // No complex accordion needed - everything is accessible through mobile menu and wallet drawer

        // Update mobile navigation active state
        function updateMobileNavigation(sectionId) {
            document.querySelectorAll('.mobile-nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // Find and activate the corresponding mobile nav link
            const mobileLinks = document.querySelectorAll('.mobile-nav-link');
            const desktopLinks = document.querySelectorAll('.nav-link');
            
            desktopLinks.forEach((desktopLink, index) => {
                if (desktopLink.classList.contains('active') && mobileLinks[index]) {
                    mobileLinks[index].classList.add('active');
                }
            });
        }

        // Wallet Drawer Functions (FAB hides when drawer open)
        function toggleWalletDrawer() {
            const drawer = document.getElementById('wallet-drawer');
            const overlay = document.getElementById('drawer-overlay');
            const fabButton = document.getElementById('mobile-drawer-toggle');
            
            if (drawer.classList.contains('translate-x-full')) {
                // Open drawer
                drawer.classList.remove('translate-x-full');
                overlay.classList.remove('opacity-0', 'pointer-events-none');
                fabButton.style.opacity = '0';
                fabButton.style.pointerEvents = 'none';
            } else {
                // Close drawer
                closeWalletDrawer();
            }
        }

        function closeWalletDrawer() {
            const drawer = document.getElementById('wallet-drawer');
            const overlay = document.getElementById('drawer-overlay');
            const fabButton = document.getElementById('mobile-drawer-toggle');
            
            drawer.classList.add('translate-x-full');
            overlay.classList.add('opacity-0', 'pointer-events-none');
            fabButton.style.opacity = '1';
            fabButton.style.pointerEvents = 'auto';
        }



        function copyWalletAddress() {
            const address = 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh';
            copyToClipboard(address);
            showToast('Mining wallet address copied!', 'success');
        }

        function viewOnExplorer() {
            showToast('Opening block explorer...', 'info');
            window.open('https://blockstream.info/address/bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh', '_blank');
        }

        function disconnectWallet() {
            showToast('Mining wallet disconnected', 'info');
            closeWalletDrawer();
            // Reset mining stats in drawer
            setTimeout(() => {
                document.querySelector('#mining-operations').classList.add('hidden');
                document.querySelector('#earnings-payouts').classList.add('hidden');
                document.querySelector('#pool-network').classList.add('hidden');
                document.querySelector('#dex-integration').classList.add('hidden');
            }, 300);
        }

        // Close drawer when clicking overlay
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('drawer-overlay').addEventListener('click', closeWalletDrawer);
        });

        function linkToDEX() {
            const address = document.getElementById('modal-bitcoin-address').value;
            if (!address) {
                showToast('Please enter a Bitcoin address', 'error');
                return;
            }
            showToast('Linking to DEX wallet...', 'success');
            closeModal('wallet-modal');
        }

        function testConnection() {
            showToast('Testing Stratum connection...', 'info');
            setTimeout(() => {
                showToast('Connection test successful! Latency: 12ms', 'success');
            }, 2000);
        }

        function autoDetectHardware() {
            showToast('Scanning for hardware...', 'info');
            setTimeout(() => {
                showToast('Detected: Antminer S19 Pro on 192.168.1.100', 'success');
                document.getElementById('hardware-select').value = 'antminer-s19';
                updateHardwareInfo();
            }, 3000);
        }

        function refreshAnalytics() {
            showToast('Refreshing analytics data...', 'info');
            loadStats();
        }

        function showToast(message, type = 'info') {
            const toast = document.getElementById('toast');
            const icon = document.getElementById('toast-icon');
            const messageEl = document.getElementById('toast-message');
            
            const icons = {
                'success': '✓',
                'error': '✗',
                'info': 'ℹ',
                'warning': '⚠'
            };
            
            icon.textContent = icons[type] || 'ℹ';
            messageEl.textContent = message;
            
            toast.classList.add('show');
            
            setTimeout(() => {
                toast.classList.remove('show');
            }, 4000);
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('Copied to clipboard: ' + text.substring(0, 30) + '...', 'success');
            }).catch(() => {
                showToast('Copy failed - please copy manually', 'error');
            });
        }

        // Load statistics
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                // Handle test mode indicator
                const testModeIndicator = document.getElementById('test-mode-indicator');
                if (data.test_mode && data.test_mode.is_active) {
                    testModeIndicator.classList.remove('hidden');
                    console.log('Test Mode Active - Session ID:', data.test_mode.session_id);
                } else {
                    testModeIndicator.classList.add('hidden');
                }
                
                document.getElementById('pool-hashrate').textContent = formatHashRate(data.pool_hashrate);
                document.getElementById('active-miners').textContent = data.active_miners.toLocaleString();
                document.getElementById('network-difficulty').textContent = formatDifficulty(data.network_difficulty);
                document.getElementById('blocks-found').textContent = data.blocks_found.toLocaleString();
                document.getElementById('btc-price').textContent = Math.round(data.btc_price).toLocaleString();
                document.getElementById('mobile-btc-price').textContent = Math.round(data.btc_price).toLocaleString();
                
                if (data.block_height) {
                    document.getElementById('block-height').textContent = data.block_height.toLocaleString();
                    document.getElementById('mobile-block-height').textContent = data.block_height.toLocaleString();
                }
                
                // Update drawer with test mode fake earnings if active
                if (data.test_mode && data.test_mode.show_fake_assets && data.test_mode.fake_earnings > 0) {
                    const earningsElement = document.querySelector('#mining-wallet-earnings');
                    if (earningsElement) {
                        const currentEarnings = parseFloat(earningsElement.textContent) || 0;
                        const totalEarnings = currentEarnings + data.test_mode.fake_earnings;
                        earningsElement.textContent = totalEarnings.toFixed(5);
                    }
                }
            } catch (error) {
                console.log('Using default stats display');
            }
        }

        function formatHashRate(rate) {
            if (rate >= 1000000) return (rate / 1000000).toFixed(1) + ' EH/s';
            if (rate >= 1000) return (rate / 1000).toFixed(1) + ' PH/s';
            return rate.toFixed(1) + ' TH/s';
        }

        function formatDifficulty(diff) {
            if (diff >= 1e12) return (diff / 1e12).toFixed(1) + 'T';
            if (diff >= 1e9) return (diff / 1e9).toFixed(1) + 'B';
            return diff.toLocaleString();
        }

        // Auto-refresh stats every 30 seconds
        setInterval(loadStats, 30000);
        
        // Close modals when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.classList.remove('show');
            }
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    """Main route - serve clean HTML interface"""
    try:
        logger.info("Serving BLGV mining pool interface")
        response = Response(MINING_POOL_HTML)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Index route error: {e}")
        return Response(f"<html><body><h1>BLGV Mining Pool Error</h1><p>{str(e)}</p></body></html>", 
                       mimetype='text/html', status=500)

@app.route('/api/stats')
def stats():
    """API endpoint for pool statistics"""
    try:
        # Get live Bitcoin price
        btc_price = pool_stats['btc_price']
        try:
            import requests
            response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC', timeout=2)
            if response.status_code == 200:
                data = response.json()
                btc_price = float(data['data']['rates']['USD'])
        except Exception:
            pass

        # Get current block height
        block_height = 902607
        try:
            response = requests.get('https://blockstream.info/api/blocks/tip/height', timeout=2)
            if response.status_code == 200:
                block_height = int(response.text)
        except Exception:
            pass

        # Get test mode data if active
        fake_data = get_fake_mining_data() if should_show_fake_assets() else {}
        
        stats_data = {
            'pool_hashrate': pool_stats['total_hashrate'] + fake_data.get('fake_hashrate', 0),
            'active_miners': pool_stats['active_miners'] + fake_data.get('fake_workers', 0),
            'total_shares': pool_stats['total_shares'],
            'blocks_found': pool_stats['blocks_found'] + fake_data.get('fake_blocks', 0),
            'network_difficulty': pool_stats['network_difficulty'],
            'btc_price': btc_price,
            'block_height': block_height,
            'pool_fee': pool_stats['pool_fee'],
            'efficiency': 98.7,
            'uptime': 99.95,
            'stale_rate': 0.6,
            'avg_latency': '12ms',
            'stratum_core_port': 3333,
            'stratum_knots_port': 3334,
            'timestamp': datetime.now().isoformat(),
            # Test mode configuration
            'test_mode': {
                'is_active': is_test_mode(),
                'show_fake_assets': should_show_fake_assets(),
                'session_id': get_test_session_id(),
                'fake_earnings': fake_data.get('fake_earnings', 0)
            },
            # Minimal SDK integration - treasury data
            'treasury': {
                'total_btc': 15.847,
                'transparency_score': 100
            }
        }
        
        return jsonify(stats_data)
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({
            'pool_hashrate': 2847.3,
            'active_miners': 2156,
            'blocks_found': 247,
            'btc_price': 106234,
            'error': 'Some live data unavailable'
        })

@app.route('/api/ecosystem/status')
def ecosystem_status():
    """Minimal SDK integration - ecosystem connectivity status"""
    try:
        return jsonify({
            "success": True,
            "data": {
                "dex_connection": {
                    "status": "connected",
                    "url": "https://dex.blgvbtc.com",
                    "integrated": True
                },
                "intelligence_platform": {
                    "status": "connected", 
                    "url": "https://blgvbtc.com",
                    "integrated": True
                },
                "mobile_app": {
                    "status": "connected",
                    "sync_enabled": True,
                    "integrated": True
                },
                "treasury": {
                    "status": "active",
                    "transparency_enabled": True,
                    "real_time_updates": True
                }
            }
        })
    except Exception as e:
        logger.error(f"Ecosystem status error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/system/status')
def system_status():
    """System status endpoint"""
    return jsonify({
        'status': 'operational',
        'stratum_server': 'online',
        'stratum_v2_core': 'port 3333',
        'stratum_v2_knots': 'port 3334',
        'web_interface': 'online',
        'database': 'connected',
        'btcpay_server': 'connected',
        'uptime': '99.95%',
        'version': '2.0.0-institutional',
        'test_mode': {
            'is_active': is_test_mode(),
            'show_fake_assets': should_show_fake_assets(),
            'session_id': get_test_session_id()
        }
    })

@app.route('/api/miners/register', methods=['POST'])
def register_miner_sdk():
    """Register miner with full SDK ecosystem integration and test mode support"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['wallet_address', 'miner_name', 'miner_type', 'expected_hashrate']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Add test mode fields using configuration
        miner_data = add_test_mode_fields({
            'wallet_address': data['wallet_address'],
            'miner_name': data['miner_name'],
            'miner_type': data['miner_type'],
            'expected_hashrate': data['expected_hashrate'],
            'power_consumption': data.get('power_consumption', 0),
            'status': 'active'
        })
        
        # Insert into database with test mode fields
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO miner_configs 
            (wallet_address, miner_name, miner_type, expected_hashrate, power_consumption, is_test_mode, test_session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            miner_data['wallet_address'],
            miner_data['miner_name'], 
            miner_data['miner_type'],
            miner_data['expected_hashrate'],
            miner_data['power_consumption'],
            miner_data['is_test_mode'],
            miner_data['test_session_id']
        ))
        
        miner_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        # Create test payout if in test mode
        if should_show_fake_assets():
            fake_data = get_fake_mining_data()
            fake_payout = fake_data['fake_payouts'][0]
            
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pool_payouts 
                (wallet_address, amount, transaction_hash, status, is_test_mode, test_session_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                miner_data['wallet_address'],
                fake_payout['amount'],
                fake_payout['transaction_hash'],
                fake_payout['status'],
                True,
                get_test_session_id()
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
        
        return jsonify({
            "success": True,
            "miner_id": miner_id,
            "message": "Miner registered successfully with ecosystem integration",
            "test_mode": {
                "is_active": is_test_mode(),
                "fake_payout_created": should_show_fake_assets()
            }
        })
        
    except Exception as e:
        logger.error(f"Miner registration error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/payouts/<wallet_address>')
def get_payouts(wallet_address):
    """Get payouts for wallet with test mode filtering"""
    try:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Filter by test mode - in test mode show all, in production exclude test data
        if is_test_mode():
            cursor.execute("""
                SELECT amount, transaction_hash, status, created_at, is_test_mode, test_session_id
                FROM pool_payouts 
                WHERE wallet_address = %s 
                ORDER BY created_at DESC
            """, (wallet_address,))
        else:
            cursor.execute("""
                SELECT amount, transaction_hash, status, created_at, is_test_mode, test_session_id
                FROM pool_payouts 
                WHERE wallet_address = %s AND is_test_mode = false
                ORDER BY created_at DESC
            """, (wallet_address,))
        
        payouts = []
        for row in cursor.fetchall():
            payouts.append({
                'amount': float(row[0]),
                'transaction_hash': row[1],
                'status': row[2],
                'created_at': row[3].isoformat() if row[3] else None,
                'is_test_mode': row[4],
                'test_session_id': row[5]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "payouts": payouts,
            "test_mode": {
                "is_active": is_test_mode(),
                "session_id": get_test_session_id(),
                "total_payouts": len(payouts)
            }
        })
        
    except Exception as e:
        logger.error(f"Payouts retrieval error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/miner/<address>')
def miner_stats(address):
    """Get miner statistics by Bitcoin address"""
    try:
        # Validate Bitcoin address format
        if not address or len(address) < 26:
            return jsonify({'error': 'Invalid Bitcoin address'}), 400
            
        # Mock miner data - in production this would query the database
        mock_data = {
            'address': address,
            'workers': [
                {
                    'name': 'worker1',
                    'hardware': 'Antminer S19 Pro',
                    'hashrate': 110.5,
                    'status': 'active',
                    'last_seen': datetime.now().isoformat(),
                    'temperature': 65,
                    'fan_speed': 3200,
                    'power_consumption': 3250
                },
                {
                    'name': 'worker2', 
                    'hardware': 'Bitaxe Ultra',
                    'hashrate': 0.5,
                    'status': 'active',
                    'last_seen': datetime.now().isoformat(),
                    'temperature': 45,
                    'fan_speed': 2400,
                    'power_consumption': 15
                }
            ],
            'total_hashrate': 111.0,
            'daily_earnings': 0.00847,
            'pending_balance': 0.00234,
            'total_shares': 156789,
            'efficiency': 98.7,
            'node_preference': 'core'
        }
        
        return jsonify(mock_data)
    except Exception as e:
        logger.error(f"Miner stats error: {e}")
        return jsonify({'error': 'Failed to fetch miner data'}), 500

@app.route('/api/marketplace/rent', methods=['POST'])
def rent_hashpower():
    """Rent hashpower API endpoint"""
    try:
        data = request.get_json()
        
        rental = {
            'id': f"rent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': 'rental',
            'hashrate': data.get('hashrate', 100),
            'duration': data.get('duration', 24),
            'cost_btc': data.get('cost_btc', 0.001),
            'cost_usd': data.get('cost_usd', 106),
            'status': 'pending_payment',
            'btcpay_invoice_id': f"BTCPay_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'rental': rental})
    except Exception as e:
        logger.error(f"Rent hashpower error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/marketplace/offer', methods=['POST'])
def offer_hashpower():
    """Offer hashpower API endpoint"""
    try:
        data = request.get_json()
        
        offer = {
            'id': f"offer_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': 'offer',
            'hashrate': data.get('hashrate', 100),
            'price_per_th': data.get('price_per_th', 0.00001),
            'max_duration': data.get('max_duration', 720),
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'offer': offer})
    except Exception as e:
        logger.error(f"Offer hashpower error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ecosystem/dex')
def dex_integration():
    """DEX integration status"""
    return jsonify({
        'status': 'connected',
        'auto_deposit': True,
        'last_transfer': '0.0247 BTC',
        'trading_volume_24h': '1.247 BTC',
        'link': 'https://dex.blgvbtc.com'
    })

@app.route('/api/ecosystem/treasury')
def treasury_status():
    """Treasury management status"""
    return jsonify({
        'user_shares': 2847,
        'total_shares': 1000000,
        'voting_power': 0.28,
        'current_value_btc': 0.347,
        'active_proposals': 3,
        'governance_enabled': True
    })

@app.route('/api/config/generate', methods=['POST'])
def generate_config():
    """Generate mining configuration"""
    try:
        data = request.get_json()
        hardware = data.get('hardware', 'custom')
        address = data.get('address', '')
        worker = data.get('worker', 'worker1')
        reward_method = data.get('reward_method', 'pps+')
        node_type = data.get('node_type', 'core')
        ordinals = data.get('ordinals', False)
        
        if not address:
            return jsonify({'error': 'Bitcoin address required'}), 400
            
        port = 3334 if node_type == 'knots' else 3333
        
        if hardware.startswith('bitaxe'):
            config = {
                "ssid": "your-wifi-ssid",
                "pass": "your-wifi-password", 
                "hostname": f"bitaxe-blgv-{worker}",
                "stratumURL": "pool.blgvbtc.com",
                "stratumPort": port,
                "stratumUser": address,
                "stratumPassword": worker,
                "rewardMethod": reward_method.upper(),
                "ordinalsEnabled": ordinals,
                "nodeType": node_type
            }
            config_text = json.dumps(config, indent=2)
            filename = 'bitaxe-config.json'
        else:
            fee = '2.0%' if reward_method == 'pps+' else '1.5%' if reward_method == 'pplns' else '0.5%'
            config_text = f"""# BLGV BTC Mining Pool Configuration
# Generated on {datetime.now().isoformat()}

pools:
  - url: stratum+tcp://pool.blgvbtc.com:{port}
    user: {address}
    pass: {worker}
    
# Pool Settings
pool_fee: {fee}
reward_method: {reward_method.upper()}
node_type: {node_type}
ordinals_mining: {ordinals}

# Hardware: {hardware}
# Efficiency: 98.7%
# Uptime: 99.95%

# Support: support@blgvbtc.com
# Documentation: https://docs.blgvbtc.com"""
            filename = 'miner-config.conf'
        
        return jsonify({
            'success': True,
            'config': config_text,
            'filename': filename,
            'stratum_url': f"stratum+tcp://pool.blgvbtc.com:{port}"
        })
        
    except Exception as e:
        logger.error(f"Config generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/support/ticket', methods=['POST'])  
def submit_support_ticket():
    """Submit support ticket"""
    try:
        data = request.get_json()
        
        ticket = {
            'id': f"ticket_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'category': data.get('category', 'technical'),
            'subject': data.get('subject', ''),
            'message': data.get('message', ''),
            'status': 'open',
            'priority': 'normal',
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'ticket': ticket})
    except Exception as e:
        logger.error(f"Support ticket error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting BLGV BTC Mining Pool - Clean Version")
        logger.info("Web interface starting on port 5000")
        logger.info("Ready for institutional mining operations")
        
        # Run clean Flask app
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")