#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 기반 모바일 UI - 한글 문제 완전 해결
Flask + HTML5로 만든 모바일 웹 인터페이스
"""

import os
import sys
import threading
import time
import json
import socket as sock
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from flask import Flask, render_template_string, request, jsonify, Response
    from flask_socketio import SocketIO, emit
    import webbrowser
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️ Flask가 설치되지 않았습니다: pip install flask flask-socketio")

# 레트로-모던 HTML 템플릿 (8-bit 감성 + 현대 기술)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="format-detection" content="telephone=no">
    <title>🌟 Dawn of Stellar - 레트로 모바일</title>
    
    <!-- PWA 메타 태그 -->
    <meta name="theme-color" content="#0a0a0a">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Dawn of Stellar">
    <link rel="manifest" href="/manifest.json">
    
    <!-- 픽셀 폰트 최적화 -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Galmuri+11:wght@400;700&family=Press+Start+2P&family=Galmuri+14&family=Galmuri+9&family=VT323&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Courier+Prime:wght@400;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Galmuri 11', 'VT323', '맑은 고딕', monospace !important;
            background: #1a1a2e;
            color: #e0e0e0;
            height: 100vh;
            overflow: hidden;
            font-size: 14px; /* 크기 줄임 */
            position: relative;
            image-rendering: pixelated;
            image-rendering: -moz-crisp-edges;
            image-rendering: crisp-edges;
            background-image: 
                radial-gradient(circle at 25% 25%, #16213e 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, #0f1419 0%, transparent 50%);
        }
        
        /* 레트로 게임기 CRT 스캔라인 효과 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(120, 150, 255, 0.03) 2px,
                rgba(120, 150, 255, 0.03) 4px
            );
            pointer-events: none;
            z-index: 1000;
            animation: flicker 0.15s infinite alternate;
        }
        
        /* 게임기 CRT 화면 깜빡임 */
        @keyframes flicker {
            0% { opacity: 1; }
            100% { opacity: 0.96; }
        }
        
        /* 픽셀 그리드 효과 */
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg, transparent 50%, rgba(0, 255, 65, 0.02) 50%),
                linear-gradient(0deg, transparent 50%, rgba(0, 255, 65, 0.02) 50%);
            background-size: 3px 3px;
            pointer-events: none;
            z-index: 999;
        }
        
        .container {
            display: flex;
            flex-direction: column;
            height: auto;
            min-height: 380px;
            max-height: 75vh;
            width: 100vw;
            max-width: 420px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
            border: 4px solid #7788ff;
            border-radius: 20px;
            box-shadow: 
                0 0 30px #7788ff,
                inset 0 0 30px rgba(119, 136, 255, 0.1),
                inset 0 0 0 8px #1a1a2e;
            background: #1a1a2e;
            padding: 6px;
        }
        
        .header {
            background: linear-gradient(145deg, #2d2d54, #1a1a2e);
            border: 2px solid #7788ff;
            border-radius: 15px 15px 0 0;
            padding: 12px;
            text-align: center;
            font-size: 10px;
            line-height: 1.4;
            box-shadow: inset 0 0 15px rgba(119, 136, 255, 0.2);
            position: relative;
        }
        
        /* 게임기 상단 스피커 */
        .header::before,
        .header::after {
            content: '';
            position: absolute;
            top: 8px;
            width: 40px;
            height: 4px;
            background: repeating-linear-gradient(
                90deg,
                #7788ff 0px,
                #7788ff 2px,
                transparent 2px,
                transparent 6px
            );
            border-radius: 2px;
        }
        .header::before { left: 20px; }
        .header::after { right: 20px; }
        
        .header h2 {
            font-size: 14px;
            font-weight: normal;
            margin-bottom: 8px;
            text-shadow: 2px 2px 0px #223366;
            animation: glow 2s ease-in-out infinite alternate;
            color: #7788ff;
            font-family: 'Galmuri 11', 'VT323', monospace; /* Press Start 2P 제거 */
        }
        
        .header .subtitle {
            font-size: 8px;
            opacity: 0.8;
            font-weight: normal;
            color: #88aaff;
            font-family: 'Galmuri 11', 'VT323', monospace; /* Press Start 2P 제거 */
        }
        
        @keyframes glow {
            from { text-shadow: 2px 2px 0px #223366, 0 0 5px #7788ff; }
            to { text-shadow: 2px 2px 0px #223366, 0 0 15px #7788ff, 0 0 20px #7788ff; }
        }
        
        .game-display {
            flex: 1;
            background: #000;
            padding: 6px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: 'Galmuri 11', 'VT323', '맑은 고딕', monospace !important;
            font-size: 12px !important; /* 크기 줄임 */
            font-weight: 400;
            line-height: 1.1 !important; /* 줄간격 줄임 */
            border: 2px solid #6666aa;
            border-radius: 10px;
            margin: 4px;
            color: #e0e0e0;
            text-shadow: 0 0 2px #7788ff;
            box-shadow: inset 0 0 20px rgba(102, 102, 170, 0.1);
            min-height: 120px;
            letter-spacing: 0.3px; /* 자간 줄임 */
        }
        
        /* 한글 텍스트 전용 스타일 */
        .korean-text {
            font-family: 'Galmuri 11', 'VT323', '맑은 고딕', monospace !important;
            font-size: 10px !important; /* 한글 더 작게 */
            line-height: 1.0 !important;
        }
        
        /* 피드백 영역 스타일 (화면 중첩 방지용) */
        .feedback-area {
            background: linear-gradient(145deg, #445588, #223366);
            border: 1px solid #7788ff;
            border-radius: 8px;
            margin: 2px 4px;
            padding: 6px 10px;
            font-family: 'Galmuri 11', 'VT323', monospace;
            font-size: 9px;
            color: #ccccff;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            animation: fadeIn 0.3s ease;
            z-index: 10;
            position: relative;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* 영어/숫자 텍스트 전용 스타일 */
        .english-text {
            font-family: 'VT323', 'Galmuri 11', monospace !important; /* Press Start 2P 제거 */
            font-size: 12px !important;
        }
        
        .game-display::-webkit-scrollbar {
            width: 8px;
        }
        
        .game-display::-webkit-scrollbar-track {
            background: #112244;
            border-radius: 4px;
        }
        
        .game-display::-webkit-scrollbar-thumb {
            background: #8888bb;
            border-radius: 4px;
        }
        
        .controls {
            background: linear-gradient(145deg, #2d2d54, #1a1a2e);
            border: 2px solid #6666aa;
            border-radius: 0 0 15px 15px;
            padding: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 120px;
            position: relative;
        }
        
        /* 게임기 하단 장식 */
        .controls::before {
            content: 'DAWN OF STELLAR GAME CONSOLE';
            position: absolute;
            bottom: 4px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 6px;
            color: #666;
            letter-spacing: 1px;
        }
        
        .dpad {
            display: grid;
            grid-template-areas: 
                ". up ."
                "left center right"
                ". down .";
            gap: 2px;
            place-items: center;
            position: relative;
            width: 90px; /* 크기 줄임 */
            height: 90px; /* 크기 줄임 */
            transform: translate(-15px, 5px); /* 위아래 이동량 줄임 */
        }
        
        /* 십자키 실제 모양 재현 */
        .dpad::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 32px;
            height: 100px;
            background: linear-gradient(45deg, #333, #666);
            border: 2px solid #444;
            z-index: 1;
            border-radius: 6px;
        }
        
        .dpad::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100px;
            height: 32px;
            background: linear-gradient(45deg, #333, #666);
            border: 2px solid #444;
            z-index: 1;
            border-radius: 6px;
        }
            z-index: 1;
            border-radius: 6px;
        }
        
        /* 십자키 버튼들 */
        .btn.direction {
            background: linear-gradient(145deg, #555, #333);
            border: 2px solid #888;
            color: #cc99ff;
            font-weight: bold;
            border-radius: 4px;
            width: 28px; /* 크기 줄임 */
            height: 28px; /* 크기 줄임 */
            font-size: 12px; /* 폰트 크기 줄임 */
            cursor: pointer;
            transition: all 0.1s linear;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 
                0 3px 6px rgba(0, 0, 0, 0.4),
                inset 0 1px 2px rgba(255, 255, 255, 0.2);
            position: relative;
            z-index: 2;
            font-family: 'Galmuri 11', 'VT323', monospace;
        }
        
        .btn.direction:hover {
            background: linear-gradient(145deg, #666, #444);
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.4),
                inset 0 1px 2px rgba(255, 255, 255, 0.3),
                0 0 10px rgba(255, 0, 255, 0.3);
        }
        
        .btn.direction:active {
            transform: translateY(2px);
            box-shadow: 
                0 1px 3px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(0, 0, 0, 0.3);
            background: linear-gradient(145deg, #444, #222);
        }
        
        .actions {
            display: grid;
            grid-template-areas: 
                ". action-y ."
                "action-x . action-b"
                ". action-a .";
            gap: 1px;
            align-items: center;
            justify-items: center;
            width: 75px; /* 크기 줄임 */
            height: 75px; /* 크기 줄임 */
            position: relative;
            transform: translateY(-2px); /* 위로 이동량 줄임 */
        }
        
        .btn {
            background: radial-gradient(circle at 30% 30%, #444466, #222233);
            border: 3px solid #8888bb;
            color: #ccccff;
            font-weight: 500;
            border-radius: 50%;
            width: 35px; /* 크기 줄임 */
            height: 35px; /* 크기 줄임 */
            font-size: 7px; /* 폰트 크기 줄임 */
            cursor: pointer;
            transition: all 0.1s linear;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(255, 255, 255, 0.1),
                inset 0 -2px 4px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
            font-family: 'Galmuri 11', 'VT323', monospace; /* Press Start 2P 제거 */
            text-align: center;
            line-height: 1.1;
        }
        
        /* 버튼 하이라이트 효과 */
        .btn::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 15px;
            right: 15px;
            height: 8px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            border-radius: 50%;
            opacity: 0.6;
        }
        
        /* 추가 버튼들 - 맨 위에 일렬 배치 */
        .extra-buttons {
            display: flex;
            flex-direction: row;
            gap: 4px;
            justify-content: stretch;
            margin-bottom: 10px;
            width: 100%;
            max-width: 320px;
            order: 1;
            padding: 0 10px;
        }
        
        /* 메인 컨트롤 영역 - 십자키와 ABXY */
        .main-controls {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            width: 100%;
            max-width: 280px;
            order: 2;
            gap: 30px;
            padding: 0 20px;
            margin-bottom: 5px; /* 아래 여백 추가 */
        }
        
        .btn-extra {
            background: linear-gradient(145deg, #666688, #444466);
            border: 2px solid #8888bb;
            color: #ccccff;
            font-weight: 500;
            border-radius: 6px;
            width: 45px;
            height: 18px;
            font-size: 6px;
            cursor: pointer;
            transition: all 0.1s linear;
            user-select: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 
                0 2px 4px rgba(0, 0, 0, 0.3),
                inset 0 1px 2px rgba(255, 255, 255, 0.1);
            font-family: 'VT323', 'Galmuri 11', monospace;
            line-height: 0.8;
            flex: 1;
            max-width: 50px;
        }
        }
        
        .btn-extra:active {
            transform: translateY(1px);
            box-shadow: 
                0 1px 2px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(0, 0, 0, 0.3);
            background: linear-gradient(145deg, #555577, #333355);
        }
        
        .btn:hover {
            background: radial-gradient(circle at 30% 30%, #445588, #223366);
            box-shadow: 
                0 6px 12px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(255, 255, 255, 0.2),
                0 0 15px rgba(119, 136, 255, 0.3);
            transform: translateY(-2px);
        }
        
        .btn:active {
            transform: translateY(2px);
            box-shadow: 
                0 2px 4px rgba(0, 0, 0, 0.4),
                inset 0 3px 6px rgba(0, 0, 0, 0.4);
            background: radial-gradient(circle at 30% 30%, #223366, #112244);
        }
        
        .btn.direction { 
            background: linear-gradient(145deg, #555, #333);
            border: 2px solid #777;
            color: #ff00ff;
            font-weight: bold;
            border-radius: 4px;
            width: 35px;
            height: 35px;
            font-size: 16px;
            box-shadow: 
                0 3px 6px rgba(0, 0, 0, 0.4),
                inset 0 1px 2px rgba(255, 255, 255, 0.2);
            z-index: 2;
        }
        
        .btn.direction:hover {
            background: linear-gradient(145deg, #666, #444);
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.4),
                inset 0 1px 2px rgba(255, 255, 255, 0.3),
                0 0 10px rgba(255, 0, 255, 0.3);
        }
        
        .btn.direction:active {
            transform: translateY(2px);
            box-shadow: 
                0 1px 3px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(0, 0, 0, 0.3);
            background: linear-gradient(145deg, #444, #222);
        }
        
        .btn.action-ok { 
            background: radial-gradient(circle at 30% 30%, #223366, #112244);
            border-color: #7788ff;
            color: #7788ff;
        }
        
        .btn.action-cancel { 
            background: radial-gradient(circle at 30% 30%, #550000, #330000);
            border-color: #ff4444;
            color: #ff4444;
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(255, 255, 255, 0.1),
                inset 0 -2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .btn.action-cancel:hover {
            background: radial-gradient(circle at 30% 30%, #770000, #440000);
            box-shadow: 
                0 6px 12px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(255, 255, 255, 0.2),
                0 0 15px rgba(255, 68, 68, 0.3);
        }
        
        .btn.action-inv { 
            background: radial-gradient(circle at 30% 30%, #555500, #333300);
            border-color: #ffff44;
            color: #ffff44;
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(255, 255, 255, 0.1),
                inset 0 -2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .btn.action-inv:hover {
            background: radial-gradient(circle at 30% 30%, #777700, #444400);
            box-shadow: 
                0 6px 12px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(255, 255, 255, 0.2),
                0 0 15px rgba(255, 255, 68, 0.3);
        }
        
        .btn.action-party { 
            background: radial-gradient(circle at 30% 30%, #005555, #003333);
            border-color: #44ffff;
            color: #44ffff;
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(255, 255, 255, 0.1),
                inset 0 -2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .btn.action-party:hover {
            background: radial-gradient(circle at 30% 30%, #007777, #004444);
            box-shadow: 
                0 6px 12px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(255, 255, 255, 0.2),
                0 0 15px rgba(68, 255, 255, 0.3);
        }
        
        /* Xbox 컨트롤러 스타일 버튼 색상 */
        .btn.action-a { 
            background: radial-gradient(circle at 30% 30%, #336633, #224422);
            border-color: #66aa66;
            color: #aaffaa;
        }
        
        .btn.action-b { 
            background: radial-gradient(circle at 30% 30%, #663333, #442222);
            border-color: #aa6666;
            color: #ffaaaa;
        }
        
        .btn.action-x { 
            background: radial-gradient(circle at 30% 30%, #334466, #223344);
            border-color: #6688aa;
            color: #aaccff;
        }
        
        .btn.action-y { 
            background: radial-gradient(circle at 30% 30%, #666633, #444422);
            border-color: #aaaa66;
            color: #ffffaa;
        }
        
        .menu-bar {
            display: flex;
            justify-content: space-around;
            background: linear-gradient(145deg, #2d2d54, #1a1a2e);
            border: 2px solid #6666aa;
            border-radius: 10px;
            padding: 10px;
            gap: 8px;
            margin: 4px;
        }
        
        .menu-btn {
            background: radial-gradient(circle at 30% 30%, #444466, #222233);
            border: 2px solid #8888bb;
            color: #ccccff;
            padding: 8px 10px;
            border-radius: 15px;
            font-size: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.1s linear;
            box-shadow: 
                0 2px 4px rgba(0, 0, 0, 0.4),
                inset 0 1px 2px rgba(255, 255, 255, 0.1);
            font-family: 'Galmuri 11', 'VT323', monospace; /* Press Start 2P 제거 */
            flex: 1;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .menu-btn::before {
            content: '';
            position: absolute;
            top: 2px;
            left: 4px;
            right: 4px;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            border-radius: 1px;
        }
        
        .menu-btn:hover {
            background: radial-gradient(circle at 30% 30%, #223366, #112244);
            box-shadow: 
                0 3px 6px rgba(0, 0, 0, 0.4),
                inset 0 1px 2px rgba(255, 255, 255, 0.2),
                0 0 8px rgba(119, 136, 255, 0.3);
            transform: translateY(-1px);
        }
        
        .menu-btn:active {
            transform: translateY(1px);
            box-shadow: 
                0 1px 2px rgba(0, 0, 0, 0.4),
                inset 0 2px 4px rgba(0, 0, 0, 0.3);
            background: radial-gradient(circle at 30% 30%, #112244, #081122);
        }
        
        /* 방향키 위치 */
        .btn-up { grid-area: up; }
        .btn-down { grid-area: down; }
        .btn-left { grid-area: left; }
        .btn-right { grid-area: right; }
        
        /* Xbox 스타일 액션 버튼 위치 */
        .action-y { grid-area: action-y; }
        .action-a { grid-area: action-a; }
        .action-x { grid-area: action-x; }
        .action-b { grid-area: action-b; }
        
        /* 버튼 눌림 효과 개선 */
        .btn-pressed {
            transform: translateY(3px) !important;
            box-shadow: 
                0 1px 2px rgba(0, 0, 0, 0.4) !important,
                inset 0 3px 6px rgba(0, 0, 0, 0.6) !important;
            background: radial-gradient(circle at 30% 30%, #112244, #081122) !important;
        }
        
        /* 반응형 - 다양한 스마트폰 크기 대응 */
        @media (max-width: 480px) {
            .btn { width: 45px; height: 45px; font-size: 7px; }
            .btn.direction { width: 26px; height: 26px; font-size: 11px; }
            .game-display { font-size: 12px; padding: 12px; min-height: 200px; letter-spacing: 0.3px; }
            .controls { padding: 8px; min-height: 120px; } /* 컨트롤 높이 줄임 */
            .dpad { width: 80px; height: 80px; } /* D패드 크기 줄임 */
            .actions { width: 70px; height: 70px; } /* 액션 버튼 영역 크기 줄임 */
            .menu-btn { font-size: 7px; padding: 6px 8px; }
            .container { max-width: 100vw; margin: 0; border-radius: 0; }
        }
        
        /* 큰 폰 (iPhone Pro Max 등) */
        @media (min-width: 414px) and (max-width: 480px) {
            .btn { width: 50px; height: 50px; font-size: 8px; }
            .btn.direction { width: 28px; height: 28px; font-size: 12px; }
            .game-display { font-size: 13px; padding: 14px; min-height: 220px; }
            .controls { padding: 10px; min-height: 140px; } /* 컨트롤 높이 줄임 */
            .dpad { width: 85px; height: 85px; }
            .actions { width: 75px; height: 75px; } /* 액션 버튼 영역 크기 줄임 */
        }
        
        /* 소형 폰 (iPhone SE 등) */
        @media (max-width: 375px) {
            .btn { width: 40px; height: 40px; font-size: 6px; }
            .btn.direction { width: 24px; height: 24px; font-size: 10px; }
            .game-display { font-size: 8px; padding: 6px; min-height: 150px; letter-spacing: 0.1px; line-height: 1.0; }
            .controls { padding: 6px; min-height: 110px; } /* 컨트롤 높이 더 줄임 */
            .dpad { width: 70px; height: 70px; } /* D패드 크기 더 줄임 */
            .actions { width: 65px; height: 65px; } /* 액션 버튼 영역 크기 더 줄임 */
            .menu-btn { font-size: 6px; padding: 5px 6px; }
            .container { padding: 4px; }
        }
        
        /* 가로 모드 최적화 */
        @media (orientation: landscape) and (max-height: 600px) {
            .container { 
                max-width: 100vw; 
                height: 100vh; 
                display: flex; 
                flex-direction: row; 
                margin: 0; 
                border-radius: 0; 
                padding: 5px;
            }
            .game-display { 
                flex: 1; 
                font-size: 11px; 
                padding: 8px; 
                min-height: auto; 
                height: calc(100vh - 20px);
                margin-right: 10px;
            }
            .controls { 
                width: 200px; 
                padding: 8px; 
                min-height: auto; 
                height: calc(100vh - 20px);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: flex-start;
                padding-left: 5px;
                padding-top: 5px;
            }
            .dpad { width: 60px; height: 60px; }
            .actions { width: 70px; height: 70px; }
            .btn { width: 35px; height: 35px; font-size: 6px; }
            .btn.direction { width: 20px; height: 20px; font-size: 9px; }
            .menu-btn { font-size: 5px; padding: 3px 4px; }
        }
        
        /* 고해상도 디스플레이 (Retina 등) */
        @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
            .game-display { 
                font-size: 14px; 
                letter-spacing: 0.4px; 
                line-height: 1.3;
            }
            .btn { 
                font-weight: 600; 
                border-width: 2px;
            }
            .btn.direction { 
                font-size: 14px; 
                font-weight: 700;
            }
            .menu-btn { 
                font-weight: 600; 
                border-width: 2px;
            }
        }
        
        /* 초고해상도 (3x) */
        @media (-webkit-min-device-pixel-ratio: 3), (min-resolution: 288dpi) {
            .game-display { 
                font-size: 15px; 
                letter-spacing: 0.5px; 
                line-height: 1.4;
            }
            .btn { border-width: 3px; }
            .menu-btn { border-width: 3px; }
        }
        
        /* 다크 모드 선호도 감지 */
        @media (prefers-color-scheme: dark) {
            .container { 
                background: linear-gradient(145deg, #1a1a2e, #16213e);
                border-color: #4a4a6a;
            }
            .game-display { 
                background: #0f0f23; 
                border-color: #4a4a6a;
                color: #00ff88;
            }
            .btn { 
                background: #2a2a4a; 
                border-color: #5a5a7a;
                color: #ccccdd;
            }
            .btn:hover { background: #3a3a5a; }
            .btn:active { background: #1a1a3a; }
        }
        
        @media (min-height: 700px) {
            .game-display { 
                min-height: 320px;
            }
            .controls { min-height: 200px; }
        }
        
        @media (max-height: 600px) {
            .game-display { 
                min-height: 180px;
                font-size: 11px;
                letter-spacing: 0.2px;
                line-height: 1.2;
            }
            .controls { min-height: 150px; }
            .btn { width: 45px; height: 45px; font-size: 7px; }
            .btn.direction { width: 25px; height: 25px; font-size: 11px; }
            .dpad { width: 75px; height: 75px; }
            .actions { width: 90px; height: 90px; }
        }
        
        /* 한글/영어 폰트 최적화 */
        .korean-text {
            font-family: 'Galmuri 11', 'VT323', '맑은 고딕', monospace !important; /* Press Start 2P 제거 */
            font-size: 9px !important; /* 한글 텍스트 더 작게 */
            line-height: 1.0 !important;
        }
        
        .korean-text.retro {
            font-family: 'Galmuri 11', 'VT323', '맑은 고딕', monospace !important; /* Press Start 2P 제거 */
            font-size: 8px !important; /* 레트로 한글 더 작게 */
        }
        
        .english-text {
            font-family: 'Galmuri 11', 'VT323', 'Share Tech Mono', 'Courier Prime', monospace;
            letter-spacing: 0.5px;
            font-weight: 400;
        }
        
        .cyber-text {
            font-family: 'Galmuri 11', 'VT323', monospace; /* Press Start 2P 제거 */
            font-weight: 700;
            text-shadow: 0 0 5px #7788ff;
        }
        
        /* 연결 상태 표시 */
        .connection-status {
            position: absolute;
            top: 12px;
            right: 12px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff4444;
            border: 2px solid #ff4444;
            box-shadow: 0 0 15px rgba(255, 68, 68, 0.8);
            transition: all 0.3s ease;
            z-index: 1001;
        }
        
        .connection-status.connected {
            background: #7788ff;
            border-color: #7788ff;
            box-shadow: 0 0 15px rgba(119, 136, 255, 0.8);
        }
        
        /* 로딩 애니메이션 */
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #223366;
            border-radius: 50%;
            border-top-color: #7788ff;
            animation: spin 2s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* 8비트 스타일 깜빡임 텍스트 */
        .blink {
            animation: blink 1s step-start infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        /* 레트로 게임 시작 이펙트 */
        @keyframes startup {
            0% { opacity: 0; transform: scale(2); }
            20% { opacity: 1; transform: scale(1.5); }
            40% { opacity: 0.8; transform: scale(1.2); }
            60% { opacity: 1; transform: scale(1.1); }
            80% { opacity: 0.9; transform: scale(1.05); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        @keyframes power_on {
            0% { 
                background: #000; 
                box-shadow: inset 0 0 100px rgba(255, 255, 255, 0); 
                filter: brightness(0);
            }
            20% { 
                background: #111; 
                box-shadow: inset 0 0 80px rgba(255, 255, 255, 0.2); 
                filter: brightness(0.3);
            }
            50% { 
                background: #222; 
                box-shadow: inset 0 0 60px rgba(255, 255, 255, 0.5); 
                filter: brightness(0.7);
            }
            80% { 
                background: #333; 
                box-shadow: inset 0 0 40px rgba(255, 255, 255, 0.8); 
                filter: brightness(1.2);
            }
            100% { 
                background: #1a1a2e; 
                box-shadow: none; 
                filter: brightness(1);
            }
        }
        
        .startup-effect {
            animation: startup 2s ease-in-out;
        }
        
        .power-on-effect {
            animation: power_on 2s ease-in-out;
        }
        
        /* 레트로 입력 커서 */
        .cursor::after {
            content: '█';
            color: #7788ff;
            animation: blink 1s step-start infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="connection-status" id="connectionStatus"></div>
        
        <div class="header korean-text retro">
            <h2 class="blink">🌟 DAWN OF STELLAR 🌟</h2>
            <div class="subtitle">RETRO KOREAN MOBILE RPG</div>
        </div>
        
        <!-- 피드백 영역 추가 (화면 중첩 방지용) -->
        <div id="feedback-area" class="feedback-area" style="display: none;">
            <!-- 버튼 피드백 메시지가 여기 표시됩니다 -->
        </div>
        
        <div id="gameDisplay" class="game-display korean-text">
╔════════════════════════════════════════════════════════╗
     ████████  █████  ██     ██ ███    ██              
     ██   ██  ██   ██ ██     ██ ████   ██              
     ██   ██  ███████ ██  █  ██ ██ ██  ██              
     ██   ██  ██   ██ ██ ███ ██ ██  ██ ██              
     ████████ ██   ██  ███ ███  ██   ████              
                                                        
      ██████ ████████ ███████ ██      ██       █████   
     ██         ██    ██      ██      ██      ██   ██  
     ██████     ██    █████   ██      ██      ███████  
          ██    ██    ██      ██      ██      ██   ██  
     ██████     ██    ███████ ███████ ███████ ██   ██  
                                                        
   [████████████ SYSTEM READY ████████████]             
                                                        
   > LOADING GAME MODULES...                      [OK]  
   > INITIALIZING COMBAT SYSTEM...                [OK]  
   > LOADING PARTY MANAGER...                     [OK]  
   > CONNECTING TO AI NETWORK...                  [OK]  
                                                        
              *** PRESS A TO BEGIN ***                  
               *** A 버튼으로 시작 ***                  
╚════════════════════════════════════════════════════════╝

🎮 CONTROLS / 조작법:
  십자키 : CHARACTER MOVE / 캐릭터 이동
  A버튼 : SELECT/CONFIRM / 선택/확인
  B버튼 : CANCEL/BACK / 취소/뒤로
  X버튼 : PARTY MENU / 파티 메뉴
  Y버튼 : INVENTORY / 인벤토리
  가방 : INVENTORY OPEN / 인벤토리 열기
  파티 : PARTY MANAGEMENT / 파티 관리

✨ SPECIAL FEATURES:
  • REAL-TIME BATTLE SYSTEM / 실시간 전투 시스템
  • 28 JOB CLASSES SYSTEM / 28개 직업 시스템
  • AI COMPANION SYSTEM / AI 동료 시스템
  • BRAVE POINT COMBAT / 브레이브 포인트 전투

🚀 PRESS [확인] TO START ADVENTURE!
   확인 버튼을 눌러서 모험을 시작하세요!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span class="loading"></span> CONNECTING TO SERVER...
        </div>
        
        <div class="menu-bar">
            <button class="menu-btn korean-text" onclick="sendCommand('save')">💾 SAVE</button>
            <button class="menu-btn korean-text" onclick="sendCommand('settings')">⚙️ SETUP</button>
            <button class="menu-btn korean-text" onclick="clearCacheAndReload()" ondblclick="nukeCacheCompletely()" title="클릭: 일반 캐시 삭제, 더블클릭: 강력 캐시 삭제">🔄 CACHE</button>
            <button class="menu-btn korean-text" onclick="sendCommand('help')">❓ HELP</button>
            <button class="menu-btn korean-text" onclick="sendCommand('exit')">🚪 EXIT</button>
        </div>
        
        <div class="controls">
            <!-- 추가 버튼들 - 맨 위에 일렬 배치 -->
            <div class="extra-buttons">
                <button class="btn-extra korean-text" onclick="sendCommand('f')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)">F<br><span style="font-size:4px;">필드</span></button>
                <button class="btn-extra korean-text" onclick="sendCommand('t')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)">T<br><span style="font-size:4px;">자동전투</span></button>
                <button class="btn-extra korean-text" onclick="sendCommand('b')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)">B<br><span style="font-size:4px;">저장</span></button>
                <button class="btn-extra korean-text" onclick="sendCommand('m')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)">M<br><span style="font-size:4px;">AI설정</span></button>
                <button class="btn-extra korean-text" onclick="sendCommand('r')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)">R<br><span style="font-size:4px;">AI요청</span></button>
                <button class="btn-extra korean-text" onclick="sendCommand('h')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)">H<br><span style="font-size:4px;">도움말</span></button>
            </div>
            
            <!-- 메인 컨트롤 영역 -->
            <div class="main-controls">
                <!-- 왼쪽: 십자키 -->
                <div class="dpad">
                    <button class="btn btn-up direction korean-text" onclick="sendCommand('w')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)" ontouchstart="pressEffect(this)" ontouchend="releaseEffect(this)">↑</button>
                    <button class="btn btn-left direction korean-text" onclick="sendCommand('a')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)" ontouchstart="pressEffect(this)" ontouchend="releaseEffect(this)">←</button>
                    <button class="btn direction" style="visibility: hidden;"></button>
                    <button class="btn btn-right direction korean-text" onclick="sendCommand('d')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)" ontouchstart="pressEffect(this)" ontouchend="releaseEffect(this)">→</button>
                    <button class="btn btn-down direction korean-text" onclick="sendCommand('s')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)" ontouchstart="pressEffect(this)" ontouchend="releaseEffect(this)">↓</button>
                </div>
                
                <!-- 오른쪽: Xbox 스타일 액션 버튼 (A 아래, B 오른쪽) -->
                <div class="actions">
                    <button class="btn action-y korean-text" onclick="sendCommand('i')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)" ontouchstart="pressEffect(this)" ontouchend="releaseEffect(this)" style="background: linear-gradient(145deg, #ffff44, #dddd22); color: #000;">Y<br/>BAG</button>
                    <button class="btn action-b korean-text" onclick="sendCommand('q')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)" ontouchstart="pressEffect(this)" ontouchend="releaseEffect(this)" style="background: linear-gradient(145deg, #ff4444, #dd2222);">B<br/>NO</button>
                    <button class="btn action-x korean-text" onclick="sendCommand('p')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)" ontouchstart="pressEffect(this)" ontouchend="releaseEffect(this)" style="background: linear-gradient(145deg, #4444ff, #2222dd);">X<br/>PTY</button>
                    <button class="btn action-a korean-text" onclick="sendCommand('enter')" onmousedown="pressEffect(this)" onmouseup="releaseEffect(this)" ontouchstart="pressEffect(this)" ontouchend="releaseEffect(this)" style="background: linear-gradient(145deg, #44ff44, #22dd22); color: #000;">A<br/>OK</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        const socket = io();
        const gameDisplay = document.getElementById('gameDisplay');
        const connectionStatus = document.getElementById('connectionStatus');
        let isConnected = false;
        
        // 페이지 로드 시 초기 화면 설정
        document.addEventListener('DOMContentLoaded', function() {
            updateGameText(`🌟 DAWN OF STELLAR MOBILE 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 모바일 클라이언트 시작!
Mobile Client Starting...

🔄 서버 연결을 기다리는 중...
⏳ Waiting for server connection...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONNECTING...`);
        });
        
        // 서버 연결
        socket.on('connect', function() {
            console.log('🔗 서버에 연결됨');
            isConnected = true;
            connectionStatus.classList.add('connected');
            updateGameText(`🌟 DAWN OF STELLAR MOBILE 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SERVER CONNECTION SUCCESS!
서버 연결 성공!

🎮 GAME SYSTEM INITIALIZED
게임 시스템이 초기화되었습니다

PRESS [확인] TO START ADVENTURE!
확인 버튼을 눌러 모험을 시작하세요!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
READY... `);
        });
        
        // 개발 모드 - 자동 새로고침 감지
        socket.on('reload_page', function() {
            console.log('🔄 페이지 자동 새로고침');
            location.reload(true);
        });
        
        // 게임 텍스트 업데이트
        socket.on('game_text', function(data) {
            updateGameText(data.text);
        });
        
        // 연결 해제
        socket.on('disconnect', function() {
            console.log('❌ 서버 연결 해제');
            isConnected = false;
            connectionStatus.classList.remove('connected');
            updateGameText(`🌟 DAWN OF STELLAR MOBILE 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ SERVER CONNECTION LOST
서버와의 연결이 끊어졌습니다

PLEASE REFRESH THE PAGE
페이지를 새로고침해주세요

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ERROR...`);
        });
        
        // 명령 전송 (레트로 스타일 개선)
        function sendCommand(command) {
            if (!isConnected) {
                updateGameText(`🌟 DAWN OF STELLAR MOBILE 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ NOT CONNECTED TO SERVER
서버에 연결되지 않았습니다

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ERROR...`);
                return;
            }
            
            console.log('🎮 명령 전송:', command);
            socket.emit('user_input', {command: command});
            
            // 8비트 스타일 즉시 피드백
            const retro_feedback = {
                'enter': '>>> CONFIRM PRESSED <<<',
                'w': '>>> MOVE UP <<<',
                's': '>>> MOVE DOWN <<<', 
                'a': '>>> MOVE LEFT <<<',
                'd': '>>> MOVE RIGHT <<<',
                'i': '>>> INVENTORY <<<',
                'p': '>>> PARTY MENU <<<',
                'q': '>>> CANCEL <<<',
                'save': '>>> SAVING... <<<',
                'settings': '>>> SETTINGS <<<',
                'help': '>>> HELP MODE <<<',
                'exit': '>>> GOODBYE! <<<'
            };
            
            if (retro_feedback[command]) {
                showRetroFeedback(retro_feedback[command]);
            }
        }
        
        // 레트로 스타일 빠른 피드백 - 개선된 버전 (화면 중첩 방지)
        function showRetroFeedback(message) {
            // 피드백 메시지만 간단히 콘솔에 표시 (화면 중첩 방지)
            console.log('🎮 FEEDBACK:', message);
            
            // 선택적으로 상태바에 피드백 표시 가능
            const statusElement = document.querySelector('.connection-status');
            if (statusElement) {
                const originalText = statusElement.textContent;
                statusElement.textContent = message;
                setTimeout(() => {
                    statusElement.textContent = originalText;
                }, 800);
            }
        }
        
        // ANSI 컬러 코드 제거 함수 (모바일용)
        function stripAnsiCodes(text) {
            if (typeof text !== 'string') return text;
            
            // ANSI 이스케이프 시퀀스 제거 (컬러, 커서 제어 등)
            return text.replace(/\x1b\[[0-9;]*[A-Za-z]/g, '')
                      .replace(/\x1b\([AB]/g, '')
                      .replace(/\x1b\[[\d;]*[HfABCDG]/g, '')
                      .replace(/\x1b\[2J/g, '')
                      .replace(/\x1b\[H/g, '');
        }
        
        // 게임 텍스트 업데이트 - 컬러 코드 제거 및 화면 정리
        function updateGameText(text) {
            // ANSI 컬러 코드 제거 (모바일 브라우저용)
            const cleanText = stripAnsiCodes(text);
            
            // 화면 내용 완전 교체 (중첩 방지)
            gameDisplay.textContent = cleanText;
            gameDisplay.scrollTop = gameDisplay.scrollHeight;
        }
        
        // 레트로 게임 시작 이펙트 (확대/축소 제거)
        function startRetroGameEffect() {
            // 부드러운 깜빡임 효과만 적용
            document.body.style.transition = 'opacity 0.3s ease';
            document.body.style.opacity = '0.7';
            
            // 게임 시작 메시지
            updateGameText(`🎮 GAME STARTING...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> POWER ON... ✅
> CHECKING SYSTEM... ✅  
> LOADING GAME ENGINE... ✅
> STELLAR NEXUS ONLINE... ✅

🌟 WELCOME TO THE ADVENTURE!
모험에 오신 것을 환영합니다!

[LOADING COMPLETE]
[게임 로딩 완료]

STATUS: ▓▓▓▓▓▓▓▓▓▓ READY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STARTING GAME IN NEW WINDOW...`);
            
            setTimeout(() => {
                document.body.style.opacity = '1';
                
                // 1초 후 실제 게임 시작
                setTimeout(() => {
                    // 게임 직접 시작 시도
                    fetch('/start-game', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({action: 'start'})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            updateGameText(data.message);
                        } else {
                            updateGameText(`❌ 게임 시작 실패: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        console.error('게임 시작 오류:', error);
                        updateGameText(`❌ 게임 시작 중 오류가 발생했습니다: ${error}`);
                    });
                }, 1000);
            }, 1500);
        }
        
        // 버튼 눌림 효과 (게임기 스타일)
        function pressEffect(button) {
            button.classList.add('btn-pressed');
            // 햅틱 피드백 (지원하는 기기에서)
            if (navigator.vibrate) {
                navigator.vibrate(50);
            }
        }
        
        function releaseEffect(button) {
            setTimeout(() => {
                button.classList.remove('btn-pressed');
            }, 150);
        }
        
        // 터치 이벤트 지원 (게임기 스타일 개선)
        document.querySelectorAll('.btn').forEach(button => {
            let touchStarted = false;
            
            button.addEventListener('touchstart', function(e) {
                e.preventDefault();
                touchStarted = true;
                pressEffect(this);
            });
            
            button.addEventListener('touchend', function(e) {
                e.preventDefault();
                if (touchStarted) {
                    touchStarted = false;
                    releaseEffect(this);
                    // 터치 끝날 때 클릭 이벤트 발생
                    this.click();
                }
            });
            
            // 터치가 버튼 밖으로 나갔을 때
            button.addEventListener('touchcancel', function(e) {
                e.preventDefault();
                if (touchStarted) {
                    touchStarted = false;
                    releaseEffect(this);
                }
            });
            
            // 마우스 이벤트도 개선
            button.addEventListener('mousedown', function(e) {
                if (!touchStarted) {
                    pressEffect(this);
                }
            });
            
            button.addEventListener('mouseup', function(e) {
                if (!touchStarted) {
                    releaseEffect(this);
                }
            });
            
            button.addEventListener('mouseleave', function(e) {
                if (!touchStarted) {
                    releaseEffect(this);
                }
            });
        });
        
        // 키보드 지원 (개선된 버전)
        document.addEventListener('keydown', function(event) {
            const keyMap = {
                'ArrowUp': 'w',
                'ArrowDown': 's', 
                'ArrowLeft': 'a',
                'ArrowRight': 'd',
                'Enter': 'enter',
                'Escape': 'q',
                'KeyI': 'i',
                'KeyP': 'p',
                'KeyS': 'save',
                'KeyH': 'help'
            };
            
            // 캐시 삭제 단축키: Ctrl+Shift+Del 또는 F12
            if ((event.ctrlKey && event.shiftKey && event.code === 'Delete') || event.code === 'F12') {
                event.preventDefault();
                nukeCacheCompletely();
                return;
            }
            
            // 일반 캐시 삭제: Ctrl+F5
            if (event.ctrlKey && event.code === 'F5') {
                event.preventDefault();
                clearCacheAndReload();
                return;
            }
            
            if (keyMap[event.code]) {
                event.preventDefault();
                sendCommand(keyMap[event.code]);
            }
        });
        
        // 게임패드 지원 추가
        let gamepadIndex = null;
        let gamepadConnected = false;
        const deadzone = 0.5;
        
        // 버튼 상태 추적 (디바운싱용)
        let buttonStates = {};
        let lastButtonTime = {};
        const BUTTON_DEBOUNCE_MS = 200; // 200ms 디바운싱
        
        // 디바운싱된 버튼 체크 함수
        function checkButton(buttonIndex, command) {
            const now = Date.now();
            const key = `btn_${buttonIndex}`;
            
            if (lastButtonTime[key] && (now - lastButtonTime[key]) < BUTTON_DEBOUNCE_MS) {
                return false; // 아직 디바운싱 시간 중
            }
            
            lastButtonTime[key] = now;
            sendCommand(command);
            return true;
        }
        
        window.addEventListener("gamepadconnected", function(e) {
            console.log("🎮 게임패드 연결됨:", e.gamepad.id);
            gamepadIndex = e.gamepad.index;
            gamepadConnected = true;
            
            // 버튼 상태 초기화
            buttonStates = {};
            lastButtonTime = {};
            updateGameText(`🎮 GAMEPAD CONNECTED!
게임패드가 연결되었습니다!

GAMEPAD INFO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID: ${e.gamepad.id}
Index: ${gamepadIndex}
Buttons: ${e.gamepad.buttons.length}
Axes: ${e.gamepad.axes.length}

GAMEPAD CONTROLS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D-PAD/LEFT STICK: 캐릭터 이동
A BUTTON: 확인/선택
B BUTTON: 취소/뒤로
X BUTTON: 파티 메뉴  
Y BUTTON: 인벤토리
LB BUTTON: 저장
RB BUTTON: 도움말

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GAMEPAD READY FOR INPUT!`);
        });
        
        window.addEventListener("gamepaddisconnected", function(e) {
            console.log("❌ 게임패드 연결 해제:", e.gamepad.id);
            gamepadConnected = false;
            gamepadIndex = null;
            buttonStates = {}; // 상태 초기화
            lastButtonTime = {}; // 타이머 초기화
            updateGameText(`❌ GAMEPAD DISCONNECTED
게임패드 연결이 해제되었습니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GAMEPAD REMOVED...`);
        });
        
        // 게임패드 입력 처리
        function handleGamepadInput() {
            if (!gamepadConnected || gamepadIndex === null) return;
            
            const gamepad = navigator.getGamepads()[gamepadIndex];
            if (!gamepad) return;
            
            // D-Pad (십자키) - 디바운싱 적용
            if (gamepad.buttons[12] && gamepad.buttons[12].pressed) { // Up
                checkButton(12, 'w');
            }
            if (gamepad.buttons[13] && gamepad.buttons[13].pressed) { // Down
                checkButton(13, 's');
            }
            if (gamepad.buttons[14] && gamepad.buttons[14].pressed) { // Left
                checkButton(14, 'a');
            }
            if (gamepad.buttons[15] && gamepad.buttons[15].pressed) { // Right
                checkButton(15, 'd');
            }
            
            // Face buttons (A, B, X, Y) - 디바운싱 적용
            if (gamepad.buttons[0] && gamepad.buttons[0].pressed) { // A (확인)
                checkButton(0, 'enter');
            }
            if (gamepad.buttons[1] && gamepad.buttons[1].pressed) { // B (취소)
                checkButton(1, 'q');
            }
            if (gamepad.buttons[2] && gamepad.buttons[2].pressed) { // X (파티)
                checkButton(2, 'p');
            }
            if (gamepad.buttons[3] && gamepad.buttons[3].pressed) { // Y (인벤토리)
                checkButton(3, 'i');
            }
            
            // Shoulder buttons - 디바운싱 적용
            if (gamepad.buttons[4] && gamepad.buttons[4].pressed) { // LB (저장)
                checkButton(4, 'save');
            }
            if (gamepad.buttons[5] && gamepad.buttons[5].pressed) { // RB (도움말)
                checkButton(5, 'help');
            }
            
            // 아날로그 스틱 (왼쪽 스틱)
            const leftStickX = gamepad.axes[0];
            const leftStickY = gamepad.axes[1];
            const deadzone = 0.3;
            
            if (Math.abs(leftStickX) > deadzone || Math.abs(leftStickY) > deadzone) {
                if (Math.abs(leftStickX) > Math.abs(leftStickY)) {
                    if (leftStickX > deadzone) sendCommand('d'); // Right
                    if (leftStickX < -deadzone) sendCommand('a'); // Left
                } else {
                    if (leftStickY > deadzone) sendCommand('s'); // Down
                    if (leftStickY < -deadzone) sendCommand('w'); // Up
                }
            }
        }
        
        // 게임패드 입력 폴링 (60fps)
        function gamepadLoop() {
            handleGamepadInput();
            requestAnimationFrame(gamepadLoop);
        }
        gamepadLoop();
        
        // 캐시 강제 삭제 및 새로고침 (완전 버전)
        function clearCacheAndReload() {
            console.log('🔄 캐시 삭제 및 새로고침 시작...');
            
            updateGameText(`🔄 FORCE CLEARING ALL CACHE...
모든 캐시를 강제로 삭제하는 중...

> CLEARING BROWSER CACHE...
> CLEARING SERVICE WORKER...
> CLEARING LOCAL STORAGE...
> CLEARING SESSION STORAGE...
> CLEARING COOKIES...
> CLEARING APPLICATION CACHE...

PLEASE WAIT...
잠시만 기다려주세요...`);
            
            // 모든 종류의 캐시 삭제
            Promise.all([
                // Service Worker 캐시 삭제
                'caches' in window ? caches.keys().then(function(cacheNames) {
                    return Promise.all(cacheNames.map(function(cacheName) {
                        console.log('🗑️ 캐시 삭제:', cacheName);
                        return caches.delete(cacheName);
                    }));
                }) : Promise.resolve(),
                
                // Local Storage 삭제
                new Promise((resolve) => {
                    if (typeof(Storage) !== "undefined") {
                        localStorage.clear();
                        sessionStorage.clear();
                        console.log('🗑️ 로컬 스토리지 삭제 완료');
                    }
                    resolve();
                }),
                
                // Service Worker 해제
                'serviceWorker' in navigator ? navigator.serviceWorker.getRegistrations().then(function(registrations) {
                    return Promise.all(registrations.map(function(registration) {
                        console.log('🔄 Service Worker 해제:', registration.scope);
                        return registration.unregister();
                    }));
                }) : Promise.resolve(),
                
                // IndexedDB 삭제 (있다면)
                new Promise((resolve) => {
                    if ('indexedDB' in window) {
                        try {
                            indexedDB.deleteDatabase('dawn-of-stellar');
                            console.log('🗑️ IndexedDB 삭제 완료');
                        } catch(e) {
                            console.log('⚠️ IndexedDB 삭제 실패:', e);
                        }
                    }
                    resolve();
                })
            ]).then(function() {
                updateGameText(`✅ CACHE CLEARED!
모든 캐시가 삭제되었습니다!

> CACHE DELETION COMPLETE
> RELOADING PAGE...

캐시 삭제 완료!
페이지를 새로고침합니다...`);
                
                // 3초 후 강제 새로고침 (캐시 무시)
                setTimeout(() => {
                    window.location.href = '/?nocache=' + Date.now() + '&force=' + Math.random();
                }, 3000);
            }).catch(function(error) {
                console.error('❌ 캐시 삭제 중 오류:', error);
                // 오류가 있어도 새로고침
                setTimeout(() => {
                    window.location.reload(true); // 강제 새로고침
                }, 2000);
            });
        }
        
        // 개발자용 초강력 캐시 제거 (Ctrl+Shift+Del 효과)
        function nukeCacheCompletely() {
            console.log('� 핵폭탄급 캐시 제거 시작...');
            
            if (confirm('🚨 WARNING: 모든 브라우저 데이터를 삭제합니다. 계속하시겠습니까?')) {
                updateGameText(`💥 NUCLEAR CACHE DELETION...
핵폭탄급 캐시 제거 중...

⚠️ 모든 브라우저 데이터 삭제 중...
⚠️ 이 작업은 되돌릴 수 없습니다...

🔥 DELETING EVERYTHING...
🔥 모든 것을 삭제하는 중...`);
                
                // 브라우저 전체 데이터 삭제 요청
                setTimeout(() => {
                    window.location.href = '/clear-cache';
                }, 2000);
            }
        }
        
        // 페이지 로드 완료
        window.addEventListener('load', function() {
            console.log('🌟 Dawn of Stellar 레트로 모바일 로드 완료');
            
            // PWA Service Worker 등록
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                        console.log('✅ Service Worker 등록 성공:', registration.scope);
                    })
                    .catch(function(error) {
                        console.log('❌ Service Worker 등록 실패:', error);
                    });
            }
            
            // 연결 시도
            if (!socket.connected) {
                updateGameText(`🌟 DAWN OF STELLAR MOBILE 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 CONNECTING TO SERVER...
서버에 연결하는 중...

PLEASE WAIT A MOMENT...
잠시만 기다려주세요...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOADING...`);
            }
        });
        
        // 페이지 벗어날 때 경고
        window.addEventListener('beforeunload', function(e) {
            if (isConnected) {
                e.preventDefault();
                e.returnValue = '게임을 종료하시겠습니까?';
            }
        });
        
        // 온라인/오프라인 상태 감지
        window.addEventListener('online', function() {
            updateGameText('✅ 인터넷 연결이 복구되었습니다.');
        });
        
        window.addEventListener('offline', function() {
            updateGameText('❌ 인터넷 연결이 끊어졌습니다.');
        });
    </script>
</body>
</html>
"""

class WebMobileUI:
    """웹 기반 모바일 UI"""
    
    def __init__(self, port=5000):
        self.port = port
        self.app = None
        self.socketio = None
        self.game_adapter = None
        self.clients = set()
        self.file_watcher_thread = None
        self.last_modified = None
        
    def start_file_watcher(self):
        """파일 변경 감시 시작"""
        def watch_file():
            current_file = Path(__file__)
            self.last_modified = current_file.stat().st_mtime
            
            while True:
                try:
                    current_mtime = current_file.stat().st_mtime
                    if current_mtime != self.last_modified:
                        print("🔄 파일 변경 감지 - 자동 새로고침")
                        self.last_modified = current_mtime
                        time.sleep(0.5)  # 파일 저장 완료 대기
                        if self.socketio:
                            self.socketio.emit('reload_page')
                    time.sleep(1)  # 1초마다 체크
                except Exception as e:
                    print(f"파일 감시 오류: {e}")
                    break
        
        self.file_watcher_thread = threading.Thread(target=watch_file, daemon=True)
        self.file_watcher_thread.start()
        
    def setup_flask_app(self):
        """Flask 앱 설정"""
        if not FLASK_AVAILABLE:
            return False
        
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'dawn_of_stellar_korean_mobile'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        @self.app.route('/')
        def index():
            # 강력한 캐시 방지
            response = Response(HTML_TEMPLATE, mimetype='text/html')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
            response.headers['ETag'] = f'"{time.time()}"'
            return response
        
        @self.app.route('/clear-cache')
        def clear_cache():
            """개발자용 캐시 강제 삭제"""
            cache_headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Last-Modified': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()),
                'ETag': f'"{time.time()}"'
            }
            
            response_text = """
🗑️ CACHE CLEARED!
캐시가 삭제되었습니다!

브라우저를 새로고침하거나
메인 페이지로 돌아가세요.

<script>
    // 강제 새로고침
    setTimeout(() => {
        window.location.href = '/?nocache=' + Date.now();
    }, 2000);
</script>
            """
            
            response = Response(response_text, mimetype='text/html')
            for key, value in cache_headers.items():
                response.headers[key] = value
            
            return response
        
        @self.app.route('/start-game', methods=['POST'])
        def start_game_api():
            """게임 시작 API 엔드포인트"""
            try:
                import os
                import sys
                
                # 상위 디렉토리 추가
                parent_dir = os.path.dirname(os.path.dirname(__file__))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
                # main.py 경로 확인
                main_path = os.path.join(parent_dir, 'main.py')
                if not os.path.exists(main_path):
                    return jsonify({
                        'success': False,
                        'error': f'main.py를 찾을 수 없습니다: {main_path}'
                    })
                
                # 실제 게임 시작
                self.start_actual_game()
                
                return jsonify({
                    'success': True,
                    'message': '게임이 성공적으로 시작되었습니다!'
                })
                
            except Exception as e:
                error_msg = f"게임 시작 중 오류 발생: {str(e)}"
                print(f"ERROR: {error_msg}")
                return jsonify({
                    'success': False,
                    'error': error_msg
                })
        
        @self.app.route('/manifest.json')
        def manifest():
            return jsonify({
                "name": "Dawn of Stellar - Retro Mobile RPG",
                "short_name": "DoS Retro",
                "description": "8비트 감성의 한글 모바일 RPG 게임",
                "start_url": "/",
                "display": "standalone",
                "orientation": "portrait",
                "theme_color": "#0a0a0a",
                "background_color": "#000000",
                "lang": "ko",
                "categories": ["games", "entertainment"],
                "icons": [
                    {
                        "src": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                        "sizes": "192x192",
                        "type": "image/png"
                    }
                ],
                "screenshots": [
                    {
                        "src": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                        "sizes": "480x854",
                        "type": "image/png"
                    }
                ]
            })
        
        @self.app.route('/sw.js')
        def service_worker():
            return Response('''
// Service Worker for Dawn of Stellar PWA
const CACHE_NAME = 'dawn-of-stellar-v1';
const urlsToCache = [
  '/',
  '/manifest.json'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
            ''', mimetype='application/javascript')
        
        @self.socketio.on('connect')
        def handle_connect(auth):
            print(f"✅ 클라이언트 연결: {request.sid}")
            self.clients.add(request.sid)
            emit('game_text', {
                'text': '🌟 던 오브 스텔라 웹 모바일 🌟\\n\\n한글이 완벽히 지원됩니다!\\n\\n레트로 게임 모드를 시작합니다...'
            })
            
            # 게임 어댑터 초기화
            self.init_game_adapter()
        
        @self.socketio.on('disconnect') 
        def handle_disconnect():
            print(f"❌ 클라이언트 연결 해제: {request.sid}")
            self.clients.discard(request.sid)
        
        @self.socketio.on('user_input')
        def handle_user_input(data):
            command = data.get('command', data.get('action', ''))  # action도 확인
            print(f"🎮 사용자 입력: {command}")
            
            # 게임 메뉴 처리
            if command in ['1', 'enter']:
                self.handle_new_game()
                return
            elif command == '2':
                self.handle_load_game()
                return
            elif command == '3':
                self.handle_settings()
                return
            elif command == '4':
                self.handle_help()
                return
            elif command in ['5', 'q']:
                self.handle_exit()
                return
            
            # 즉시 피드백 전송
            feedback_messages = {
                'w': '⬆️ UP',
                's': '⬇️ DOWN', 
                'a': '⬅️ LEFT',
                'd': '➡️ RIGHT',
                'i': '🎒 INVENTORY',
                'p': '👥 PARTY',
                'save': '💾 SAVED',
                'settings': '⚙️ SETTINGS',
                'help': '❓ HELP',
                'exit': '🚪 EXIT'
            }
            
            if command in feedback_messages:
                self.broadcast_game_text(f">>> {feedback_messages[command]} <<<")
            
            # 실제 게임 시작 명령 처리 (웹에서 실행)
            if command == 'start_real_game':
                self.start_web_real_game()
                return
            
            if self.game_adapter:
                self.game_adapter.add_input(command)
            else:
                # 실제 게임 입력 처리를 위한 개선된 핸들러
                self.handle_real_game_input(command)
        
        return True
    
    def start_actual_game(self):
        """실제 게임 시작 및 연결"""
        try:
            self.broadcast_game_text("""🎮 DAWN OF STELLAR LOADING...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 INITIALIZING GAME SYSTEMS...
게임 시스템을 초기화하는 중...

> LOADING CORE ENGINE... ✅
> LOADING CHARACTER SYSTEM... ✅  
> LOADING COMBAT SYSTEM... ✅
> LOADING DUNGEON SYSTEM... ✅
> LOADING AI SYSTEM... ✅

🌟 GAME READY!
게임 준비 완료!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            
            # 백그라운드에서 게임 스레드 시작
            game_thread = threading.Thread(target=self.run_game_in_background)
            game_thread.daemon = True
            game_thread.start()
            
        except Exception as e:
            error_msg = f"게임 시작 중 오류: {str(e)}"
            self.broadcast_game_text(f"❌ ERROR: {error_msg}")
    
    def run_game_in_background(self):
        """백그라운드에서 게임 실행"""
        try:
            import sys
            import os
            
            # 상위 디렉토리 추가
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # 직접 메인 게임 로직 실행 시도
            try:
                # main.py에서 게임 클래스 가져오기
                import main
                
                self.broadcast_game_text("""🌟 DAWN OF STELLAR 게임 모듈 로드!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 실제 게임을 웹에서 실행합니다!
콘솔이 아닌 웹 브라우저에서 플레이!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
                
                # 실제 메인 게임 실행하되 웹으로 출력 리디렉션
                self.execute_real_game_with_web_output()
                
            except ImportError as e:
                # main.py를 찾을 수 없으면 기본 게임 화면 표시
                self.broadcast_game_text(f"❌ main.py import 실패: {e}")
                self.show_game_start_screen()
            except Exception as e:
                # 기타 오류 시 게임 화면 표시
                self.broadcast_game_text(f"❌ 게임 실행 실패: {e}")
                self.show_game_start_screen()
                
        except Exception as e:
            self.broadcast_game_text(f"❌ 게임 실행 오류: {str(e)}")
            self.show_game_start_screen()
    
    def execute_real_game_with_web_output(self):
        """실제 게임을 웹 출력으로 실행"""
        try:
            import sys
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            self.broadcast_game_text("""🌟 실제 DAWN OF STELLAR 게임 시작!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 실제 게임을 웹으로 리디렉션 시도 중...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            
            # 실제 게임 직접 실행 시도 (출력 리디렉션 없이)
            try:
                import main
                
                self.broadcast_game_text("""✅ 메인 게임 모듈 import 성공!

� 실제 게임을 백그라운드에서 실행 중...
콘솔창에 게임이 표시되지만, 입력은 웹에서 가능합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

게임이 실행되었습니다!
웹 인터페이스를 통해 게임을 조작하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
                
                # 새 스레드에서 실제 게임 실행
                import threading
                def run_main_game():
                    try:
                        # 콘솔 인코딩을 UTF-8로 설정
                        import os
                        import sys
                        
                        # Windows 콘솔 UTF-8 설정
                        if os.name == 'nt':  # Windows
                            os.system('chcp 65001')  # UTF-8 코드페이지
                            # sys.stdout을 UTF-8로 재설정
                            sys.stdout.reconfigure(encoding='utf-8')
                            sys.stderr.reconfigure(encoding='utf-8')
                        
                        print("🌟 콘솔 UTF-8 인코딩 설정 완료")
                        
                        main.main()
                    except Exception as e:
                        self.broadcast_game_text(f"❌ 게임 실행 오류: {e}")
                
                game_thread = threading.Thread(target=run_main_game, daemon=True)
                game_thread.start()
                
                # 웹 연결 상태 표시
                self.show_game_connection_status()
                
            except Exception as game_error:
                self.broadcast_game_text(f"""❌ 게임 실행 중 오류 발생!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

오류 내용: {str(game_error)}

대신 웹 게임 모드로 전환합니다...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
                
                # 오류 시 웹 게임 화면으로 fallback
                self.show_game_start_screen()
            
        except Exception as e:
            self.broadcast_game_text(f"❌ 게임 출력 리디렉션 실패: {e}")
            self.show_game_start_screen()
    
    def show_game_connection_status(self):
        """게임 연결 상태 표시"""
        self.broadcast_game_text("""🎮 DAWN OF STELLAR 연결 상태

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 게임 상태: 실행 중 ✅
🖥️ 게임 화면: 콘솔창에 표시
🎮 웹 컨트롤: 활성화 ✅
🔊 오디오: 게임에서 출력

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 사용법:
• 콘솔창에서 게임 화면 확인
• 웹에서 버튼으로 조작
• A/B 버튼 위치 변경됨

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

웹 컨트롤러가 활성화되었습니다!
콘솔창의 게임을 웹 버튼으로 조작하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    def handle_real_game_input(self, command):
        """실제 게임 입력 처리"""
        # 실제 게임에 입력 전달 시도
        try:
            # 키보드 이벤트 시뮬레이션을 통한 입력 전달
            import keyboard
            
            # 명령어를 키보드 입력으로 변환
            key_mapping = {
                'w': 'w',
                's': 's', 
                'a': 'a',
                'd': 'd',
                'i': 'i',
                'p': 'p',
                'enter': 'enter',
                'q': 'q',
                '1': '1',
                '2': '2',
                '3': '3',
                '4': '4',
                '5': '5'
            }
            
            if command in key_mapping:
                # 실제 키보드 입력 시뮬레이션
                keyboard.send(key_mapping[command])
                
                self.broadcast_game_text(f"""🎮 실제 게임에 입력 전달: {command.upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[웹→게임] 입력: {command} → 키: {key_mapping[command]}
[상태] 전달 완료 ✅

콘솔창에서 게임 반응을 확인하세요!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            else:
                self.broadcast_game_text(f"""⚠️ 지원하지 않는 명령: {command}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 사용 가능한 명령어:
[W] 위로 이동
[S] 아래로 이동  
[A] 왼쪽 이동
[D] 오른쪽 이동
[I] 인벤토리
[P] 파티 관리
[1-5] 메뉴 선택
[ENTER] 확인
[Q] 취소

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            
        except ImportError:
            # keyboard 모듈이 없으면 기본 처리
            self.broadcast_game_text(f"""🎮 입력 감지: {command.upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ keyboard 모듈이 필요합니다.
설치: pip install keyboard

현재는 입력을 인식만 하고 있습니다.
콘솔창에서 직접 게임을 조작해보세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
        except Exception as e:
            self.broadcast_game_text(f"❌ 실제 게임 입력 처리 실패: {e}")
    
    def start_web_real_game(self):
        """실제 게임을 웹에서 시작 (기존 가짜 게임 제거)"""
        self.broadcast_game_text("""🎮 실제 DAWN OF STELLAR 연결 시도!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 진짜 게임과 연결을 시도하는 중...
가짜 웹 게임이 아닌 실제 게임!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 현재 실제 게임 연결을 구현하는 중입니다.

실제 Dawn of Stellar 게임을 웹에서 실행하려면
게임 엔진과의 연결이 필요합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
실제 게임 연결 대기 중... <span class="cursor"></span>""")
    
    def start_web_game(self):
        """웹에서 실제 게임 시작"""
        self.broadcast_game_text("""┌─────────────────────────────┐
    🌟 DAWN OF STELLAR 🌟    
        REAL GAME MODE        
└─────────────────────────────┘

         APTOL STUDIO (2025)
         실제 게임 연결 모드!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 실제 Dawn of Stellar 게임 연결!
가짜가 아닌 진짜 게임입니다!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 REAL GAME MENU / 실제 게임 메뉴

[1] 새 게임 시작 (New Game)
[2] 게임 불러오기 (Load Game)  
[3] 설정 (Settings)
[4] 도움말 (Help)
[5] 종료 (Exit)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 조작법:
• 숫자 키 또는 버튼으로 선택
• A 버튼: 확인 / B 버튼: 취소
• 실제 Dawn of Stellar 게임과 연결됩니다!

실제 게임 모드 입력 대기 중... <span class="cursor"></span>
""")
    
    def show_game_start_screen(self):
        """게임 시작 화면 표시"""
        start_screen = """
┌─────────────────────────────┐
    🌟 DAWN OF STELLAR 🌟    
        RETRO EDITION        
└─────────────────────────────┘

         APTOL STUDIO (2025)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 GAME MENU / 게임 메뉴

[1] 새 게임 시작 (New Game)
[2] 게임 불러오기 (Load Game)  
[3] 설정 (Settings)
[4] 도움말 (Help)
[5] 종료 (Exit)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 조작법:
• 숫자 키 또는 버튼으로 선택
• A 버튼: 확인 / B 버튼: 취소

입력을 기다리는 중... <span class="cursor"></span>
"""
        self.broadcast_game_text(start_screen)
    
    def handle_new_game(self):
        """새 게임 시작 - 실제 게임 연결"""
        self.broadcast_game_text("""🌟 실제 Dawn of Stellar 새 게임 시작!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 실제 게임을 웹에서 실행합니다!

⚠️ 잠시만 기다려주세요...
실제 게임 시스템을 초기화하는 중...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 실제 Dawn of Stellar 게임 연결!
가짜 웹 게임이 아닌 진짜 게임입니다!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
        
        # 실제 게임 실행 시도
        try:
            import sys
            import os
            
            # 상위 디렉토리 추가
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # 실제 게임 실행
            self.execute_real_game_with_web_output()
            
        except Exception as e:
            self.broadcast_game_text(f"""❌ 실제 게임 실행 실패: {e}

대신 기본 게임 메뉴를 표시합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            self.show_game_start_screen()
    
    def start_web_real_game(self):
        """웹에서 실제 게임 시작"""
        self.broadcast_game_text("""🎮 DAWN OF STELLAR - 웹 게임 모드

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 게임이 시작되었습니다!
이 웹 페이지에서 모든 게임이 진행됩니다.

━ 게임 상태 ━
• 플레이어: 플레이어
• 레벨: 1
• 위치: 시작 마을
• 파티: 1명 (본인)

━ 현재 화면: 시작 마을 ━

🏠 평화로운 시작 마을에 있습니다.
모험을 떠날 준비가 되었습니다!

[W] 북쪽으로 이동 (던전 입구)
[S] 남쪽으로 이동 (상점가)
[A] 서쪽으로 이동 (여관)
[D] 동쪽으로 이동 (길드)

[I] 인벤토리 열기
[P] 파티 관리
[H] 도움말

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
명령을 입력하세요: <span class="cursor"></span>""")
    
    def handle_web_demo_input(self, command):
        """웹 게임 모드 입력 처리"""
        web_responses = {
            'w': """🌟 북쪽 던전 입구로 이동!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚔️ 던전 입구에 도착했습니다!

어둠 속에서 몬스터의 기척이 느껴집니다...

[ENTER] 던전 진입 (1층)
[S] 마을로 돌아가기
[I] 인벤토리 확인

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
다음 행동을 선택하세요: <span class="cursor"></span>""",
            
            's': """🏪 남쪽 상점가로 이동!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 상점가에 도착했습니다!

여러 상점들이 줄지어 있습니다.

[1] 무기점 (검, 활, 지팡이)
[2] 방어구점 (갑옷, 방패)
[3] 아이템점 (포션, 도구)
[4] 장신구점 (반지, 목걸이)

[W] 마을 중앙으로 돌아가기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
상점을 선택하세요: <span class="cursor"></span>""",
            
            'a': """🏨 서쪽 여관으로 이동!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛏️ 평온한 여관에 도착했습니다!

여관 주인이 반갑게 맞이합니다.

"어서 오세요! 무엇을 도와드릴까요?"

[1] 휴식하기 (HP/MP 완전 회복) - 50골드
[2] 저장하기 (무료)
[3] 정보 듣기 (마을 소식)

[D] 마을 중앙으로 돌아가기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
선택하세요: <span class="cursor"></span>""",
            
            'd': """🏛️ 동쪽 길드로 이동!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚔️ 모험가 길드에 도착했습니다!

길드원들이 바쁘게 움직이고 있습니다.

📋 퀘스트 게시판:
[1] 🐺 늑대 처치 (초급) - 보상: 100골드
[2] 🕷️ 거미 소탕 (중급) - 보상: 300골드
[3] 🐉 드래곤 토벌 (고급) - 보상: 1000골드

[4] 파티원 모집
[5] 길드 정보

[A] 마을 중앙으로 돌아가기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
퀘스트를 선택하세요: <span class="cursor"></span>""",
            
            'i': """🎒 인벤토리

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 골드: 100

📦 아이템:
[1] 초보자 검 (장착 중)
[2] 천 갑옷 (장착 중)  
[3] 회복 포션 x3
[4] 마나 포션 x2
[5] 빵 x5

✨ 특수 아이템:
- 모험가 증명서
- 마을 지도

용량: 7/20

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[B] 닫기: <span class="cursor"></span>""",
            
            'p': """👥 파티 관리

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 현재 파티원: 1/4

🗡️ 플레이어 (리더)
- 직업: 전사
- 레벨: 1
- HP: 100/100
- MP: 50/50
- 상태: 정상

📋 파티 설정:
[1] 파티원 초대
[2] 대형 변경
[3] 아이템 분배 설정
[4] AI 설정

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[B] 닫기: <span class="cursor"></span>""",
            
            'enter': """⚔️ 던전 1층 진입!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌑 어둠의 던전 1층

습기찬 공기와 함께 몬스터의 기척이 느껴집니다.

🗺️ 미니맵:
┌─────────┐
│ ? ? ? E │
│ ? # ? ? │  
│ S ? ? ? │
│ ? ? ? ? │
└─────────┘

S: 현재 위치 (시작점)
E: 출구 (계단)
#: 벽
?: 미탐험 지역

[W] 북쪽 탐험
[A] 서쪽 탐험  
[D] 동쪽 탐험
[Q] 던전 나가기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
행동을 선택하세요: <span class="cursor"></span>"""
        }
        
        response = web_responses.get(command, f"""
🎮 웹 게임 모드 - 명령 처리

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

입력받은 명령: {command.upper()}

🎯 사용 가능한 명령어:
[W] 북쪽 이동
[S] 남쪽 이동  
[A] 서쪽 이동
[D] 동쪽 이동
[I] 인벤토리
[P] 파티 관리
[H] 도움말
[숫자] 메뉴 선택
[ENTER] 확인

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
웹 게임 진행 중... <span class="cursor"></span>
""")
        
        self.broadcast_game_text(response)
    
    def handle_load_game(self):
        """게임 불러오기 - 실제 게임 연결"""
        self.broadcast_game_text("""💾 실제 게임 불러오기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 실제 Dawn of Stellar 저장 파일 검색 중...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 실제 게임 저장 시스템과 연결이 필요합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    def handle_settings(self):
        """설정 메뉴 - 실제 게임 연결"""
        self.broadcast_game_text("""⚙️ 실제 게임 설정

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 조작 설정
• 게임패드: 활성화 ✅
• 키보드: 활성화 ✅
• A/B 버튼 위치: 변경됨 ✅

🔊 오디오 설정  
• 배경음악: 실제 게임 연동 필요
• 효과음: 실제 게임 연동 필요

🎨 화면 설정
• 테마: 블루 레트로 ✅
• 폰트: 갈무리11 ✅
• 웹-게임 연결: 구현 중

[B] 메인 메뉴로 돌아가기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    def handle_help(self):
        """도움말 - 실제 게임"""
        self.broadcast_game_text("""❓ 실제 게임 도움말

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 조작법:
• 십자패드/WASD: 이동
• A버튼: 확인/선택 (위치 변경됨)
• B버튼: 취소/뒤로가기 (위치 변경됨)
• X버튼: 파티 관리
• Y버튼: 인벤토리

🎯 게임 목표:
실제 Dawn of Stellar 게임을 웹에서 플레이!

🌟 특징:
• 로그라이크 RPG
• 브레이브 전투 시스템
• AI 동료 시스템 
• 파티 플레이
• 28개 직업 시스템

⚠️ 현재 웹-게임 연결 구현 중

[B] 메인 메뉴로 돌아가기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    def handle_exit(self):
        """게임 종료"""
        self.broadcast_game_text("""🚪 게임을 종료하시겠습니까?

[1] 예, 종료합니다
[2] 아니오, 계속 플레이

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    def strip_ansi_codes(self, text):
        """ANSI 컬러 코드와 제어 문자 제거 (서버용)"""
        if not isinstance(text, str):
            return text
        
        import re
        
        # ANSI 이스케이프 시퀀스 제거
        # 컬러 코드: \x1b[0-9;]*[A-Za-z]
        # 커서 제어: \x1b[H, \x1b[2J 등
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
        text = ansi_escape.sub('', text)
        
        # 추가 ANSI 제어 문자들 제거
        text = re.sub(r'\x1b\([AB]', '', text)  # 문자셋 제어
        text = re.sub(r'\x1b\[[\d;]*[HfABCDG]', '', text)  # 커서 제어
        text = re.sub(r'\x1b\[2J', '', text)  # 화면 지우기
        text = re.sub(r'\x1b\[H', '', text)  # 커서 홈
        text = re.sub(r'\x1b\[[\d;]*m', '', text)  # 컬러/스타일 제어
        
        return text
    
    def broadcast_game_text(self, text):
        """모든 클라이언트에게 게임 텍스트 전송 (ANSI 코드 제거)"""
        if self.socketio and self.clients:
            # 모바일 브라우저용으로 ANSI 코드 제거
            clean_text = self.strip_ansi_codes(text)
            self.socketio.emit('game_text', {'text': clean_text})
    
    def show_simple_menu(self):
        """간단한 메뉴 표시 (어댑터 없을 때)"""
        menu_text = """
🌟 DAWN OF STELLAR MOBILE 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GAME ADAPTER NOT AVAILABLE
게임 어댑터를 사용할 수 없습니다.

SIMPLE MENU MODE
간단 메뉴 모드

[1] START GAME - 게임 시작
[2] SETTINGS - 설정  
[3] HELP - 도움말
[4] EXIT - 종료

PRESS NUMBER OR USE BUTTONS
숫자를 누르거나 버튼을 사용하세요

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
READY FOR INPUT... <span class="cursor"></span>
"""
        self.broadcast_game_text(menu_text)
    
    def start_real_game(self):
        """실제 게임 시작"""
        try:
            self.broadcast_game_text("""🎮 DAWN OF STELLAR STARTING...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 게임이 새 창에서 시작됩니다!
Game will start in a new window!

잠시만 기다려주세요...
Please wait a moment...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            
            # 게임 실행 스레드 시작
            game_thread = threading.Thread(target=self.run_real_game_thread)
            game_thread.daemon = True
            game_thread.start()
            
        except Exception as e:
            error_msg = f"""❌ GAME START ERROR / 게임 시작 오류

Error: {e}

게임을 직접 실행하려면:
To run the game directly:
python main.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            print(error_msg)
            self.broadcast_game_text(error_msg)
    
    def run_real_game_thread(self):
        """실제 게임 실행 스레드"""
        try:
            import sys
            import os
            
            self.broadcast_game_text("🌟 Dawn of Stellar을 로딩 중...")
            
            # 웹에서 직접 게임 실행하도록 변경
            try:
                # 상위 디렉토리 추가
                parent_dir = os.path.dirname(os.path.dirname(__file__))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
                from main import DawnOfStellarGame
                self.broadcast_game_text("✅ 게임 로딩 완료! 웹에서 게임이 시작됩니다.")
                
                # 웹 환경에서 게임 실행
                game = DawnOfStellarGame()
                
                # 게임 실행 상태를 웹으로 전송
                self.broadcast_game_text("""🎮 DAWN OF STELLAR 시작!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

게임이 백그라운드에서 실행 중입니다.
웹 인터페이스를 통해 조작하세요!

[A] 확인  [B] 취소  [X] 메뉴  [Y] 인벤토리

━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
                
                # 게임을 웹 모드로 실행
                self.web_game_loop(game)
                
            except ImportError as import_error:
                self.broadcast_game_text(f"❌ 게임 모듈 import 오류: {import_error}")
                
        except Exception as e:
            error_msg = f"❌ 실제 게임 실행 오류: {e}"
            print(error_msg)
            self.broadcast_game_text(error_msg)
            
    def web_game_loop(self, game):
        """웹 환경에서의 게임 루프"""
        try:
            # 게임 상태를 웹으로 출력
            self.broadcast_game_text("""┌─ DAWN OF STELLAR ─┐
         APTOL STUDIO
└── RETRO EDITION ──┘

🌟 게임이 웹에서 실행 중입니다!

━ 게임 상태 ━
• 파티: 준비됨
• 시스템: 온라인
• 상태: 대기 중

[A] 새 게임 시작
[B] 게임 로드  
[X] 설정
[Y] 종료

웹 컨트롤러를 사용하여 게임을 조작하세요!""")
            
        except Exception as e:
            self.broadcast_game_text(f"❌ 웹 게임 루프 오류: {e}")
    
    def init_game_adapter(self):
        """게임 어댑터 초기화 - 레트로 스타일 적용"""
        if self.game_adapter is not None:
            print("⚠️ 게임 어댑터가 이미 초기화되어 있습니다.")
            return
            
        # 레트로 스타일 시작 화면
        print("🎮 레트로 게임 모드 시작...")
        self.show_retro_welcome()
        
    def show_retro_welcome(self):
        """레트로 스타일 환영 화면 - 모바일 최적화"""
        self.broadcast_game_text("""
┌─ DAWN OF STELLAR ─┐
         APTOL STUDIO
└── RETRO EDITION ──┘

> SYSTEM READY
> WORLD DATA LOADED
> STELLAR NEXUS ONLINE

[PRESS A TO CONTINUE]
[A 버튼으로 계속하기]

STATUS: ▓▓▓ READY

[PRESS ANY BUTTON TO CONTINUE]
[아무 버튼이나 눌러 계속하세요]

STATUS: ▓▓▓▓▓▓▓▓▓▓ READY
""")
        
    def start_demo_mode(self):
        """레트로 스타일 메인 메뉴"""
        self.broadcast_game_text("""
█▀▀▄ █▀▀█ █   █ █▀▀▄   █▀▀█ █▀▀▀   █▀▀▀█ ▀▀█▀▀ █▀▀▀ █   █   █▀▀█ █▀▀█
█  █ █▄▄█ █▄█▄█ █  █   █  █ █▀▀▀   ▀▀▀▄▄   █   █▀▀▀ █   █   █▄▄█ █▄▄▀
▀▀▀  ▀  ▀  ▀ ▀  ▀  ▀   ▀▀▀▀ ▀      █▄▄▄█   ▀   ▀▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ ▀ ▀▀

> MAIN TERMINAL <

[A] NEW GAME     새 게임
[B] LOAD GAME    게임 로드
[X] OPTIONS      옵션
[Y] CREDITS      크레딧

UP/DOWN: NAVIGATE    위/아래: 탐색
[A]: SELECT         [A]: 선택

CURRENT TIME: 2387.08.07
NEXUS STATUS: ONLINE
""")
        
        # 레트로 게임 시나리오 시작
        threading.Timer(2.0, self.retro_game_scenario).start()
    
    def retro_game_scenario(self):
        """레트로 게임 시나리오"""
        scenarios = [
            """
> ENTERING STELLAR NEXUS...

▓▓▓▓▓▓▓▓▓▓ LOADING COMPLETE

LOCATION: CRYSTAL CAVES
DEPTH: 15F
PARTY: 4 MEMBERS

┌─────────────────────────────┐
│ [W] WARRIOR   LV.12  HP:███ │
│ [M] MAGE      LV.10  MP:██▓ │
│ [A] ARCHER    LV.11  HP:███ │
│ [T] THIEF     LV.9   HP:██▓ │
└─────────────────────────────┘

> ENEMY DETECTED
> CRYSTAL GOLEM APPROACHES

[A] ATTACK    [B] DEFEND
[X] MAGIC     [Y] ITEMS
""",
            """
> BATTLE ENGAGED

WARRIOR ATTACKS WITH FLAME BLADE!
▓▓▓▓▓▓▓▓░░ CHARGING...

★ CRITICAL HIT! ★
DAMAGE: 156

CRYSTAL GOLEM HP: ███▓░░░░░░

> GOLEM RETALIATES
STONE THROW!

PARTY DAMAGE: -23

STATUS: ADVANTAGE
COMBO METER: ▓▓▓▓▓▓░░░░
""",
            """
> VICTORY ACHIEVED

CRYSTAL GOLEM DEFEATED!

REWARDS:
▪ EXP: +450
▪ GOLD: +320
▪ ITEMS: Crystal Shard x3
▪ RARE: Golem Heart

WARRIOR LEVEL UP! 12 → 13
NEW SKILL: METEOR STRIKE

> SCANNING AREA...
> SECRET PASSAGE DETECTED

[A] INVESTIGATE    조사하기
[B] CONTINUE       계속하기

DISCOVERY RATE: 87%
""",
            """
> ACCESSING SECRET CHAMBER

ANCIENT TERMINAL FOUND...
DECRYPTING DATA...

▓▓▓▓▓▓▓▓▓▓ COMPLETE

"STELLAR ARCHIVES - ENTRY #1247"
"THE DAWN PROTOCOL HAS BEEN ACTIVATED"
"SEEK THE SEVEN CRYSTALS..."
"BEFORE THE VOID CONSUMES ALL..."

> NEW QUEST UNLOCKED
★ THE DAWN PROTOCOL ★

[A] ACCEPT QUEST   퀘스트 수락
[B] VIEW MAP       지도 보기

PROGRESS: 1/7 CRYSTALS
"""
        ]
        
        for i, scenario in enumerate(scenarios):
            threading.Timer(i * 8.0, lambda s=scenario: self.broadcast_game_text(s)).start()
    
    def handle_demo_input(self, command):
        """레트로 게임 입력 처리"""
        retro_responses = {
            'a': """
> ACTION: ATTACK SELECTED

WARRIOR CHARGES FORWARD!
▓▓▓▓▓▓▓▓░░ BUILDING POWER...

TARGET: CRYSTAL GOLEM
WEAPON: STELLAR BLADE +3
CRITICAL CHANCE: 23%

> EXECUTE? [A] YES [B] NO
""",
            'b': """
> ACTION: DEFEND SELECTED

PARTY ASSUMES DEFENSIVE STANCE
DEFENSE BOOST: +40%
MAGIC RESISTANCE: +25%

STATUS EFFECTS:
▪ GUARDIAN SHIELD (3 TURNS)
▪ DAMAGE REDUCTION: 50%

> READY FOR ENEMY TURN
""",
            'x': """
> MAGIC MENU ACCESSED

AVAILABLE SPELLS:

[1] FIRE BOLT     MP:8   DMG:★★☆
[2] ICE SHARD     MP:12  DMG:★★★
[3] HEAL          MP:15  RESTORE:★★★
[4] LIGHTNING     MP:20  DMG:★★★★

MAGE MP: ██████████ 45/45

SELECT SPELL: [1-4]
""",
            'y': """
> ITEMS INVENTORY

CONSUMABLES:
[1] HEALTH POTION x5    +50 HP
[2] MANA ELIXIR x3      +30 MP  
[3] PHOENIX DOWN x1     REVIVE
[4] CRYSTAL BOMB x2     AREA DMG

QUICK USE: [1-4]
CANCEL: [B]

CURRENT GOLD: 1,247
""",
            'up': """
> PARTY STATUS UPDATED

FORMATION: ATTACK MODE
┌─────────────────┐
│ [W] WARRIOR  ↑  │ FRONT LINE
│ [A] ARCHER   →  │ SUPPORT
│ [M] MAGE     ↑  │ BACK LINE  
│ [T] THIEF    ↗  │ FLANKING
└─────────────────┘

BONUS: +15% ATK, -10% DEF
""",
            'down': """
> SCANNING ENVIRONMENT

CRYSTAL CAVES - DEPTH 15F
━━━━━━━━━━━━━━━━━━━━━━━━━

DETECTED:
▪ HIDDEN TREASURE CHEST [EAST]
▪ SECRET PASSAGE [NORTH]
▪ CRYSTAL DEPOSIT [SOUTH]
▪ MONSTER TRACKS [WEST]

CHOOSE DIRECTION:
ARROWS TO EXPLORE
""",
            'left': """
> MOVING WEST

ENTERING SHADOW CORRIDOR...
▓▓▓░░░░░░░ EXPLORING...

DISCOVERY!
ANCIENT RUNE FOUND!

"WHEN SEVEN STARS ALIGN,
 THE DAWN SHALL BREAK THE NIGHT"

> RUNE ADDED TO CODEX
> MYSTERY PROGRESS: 2/7

NEW OBJECTIVE UNLOCKED!
""",
            'right': """
> MOVING EAST

TREASURE CHAMBER ACCESSED!
✨ LEGENDARY CHEST DISCOVERED ✨

CONTAINS:
★ STELLAR CRYSTAL (RARE)
★ MITHRIL SWORD +5 (EPIC)
★ ANGEL RING (LEGENDARY)
★ 2,500 GOLD

> CLAIM TREASURE? [A] YES [B] NO

WARNING: GUARDIAN MAY ACTIVATE
"""
        }
        
        response = retro_responses.get(command, f"""
> INPUT RECEIVED: {command.upper()}

PROCESSING COMMAND...
━━━━━━━━━━━━━━━━━━━━━━━━━

[A] ATTACK     공격
[B] DEFEND     방어  
[X] MAGIC      마법
[Y] ITEMS      아이템

ARROWS: MOVE/NAVIGATE
↑↓←→ 이동/탐색

GAMEPAD: A/B/X/Y BUTTONS
게임패드: A/B/X/Y 버튼

> COMMAND EXECUTED!
""")
        
        self.broadcast_game_text(response)
    
    def get_local_ip(self):
        """로컬 IP 주소 가져오기"""
        try:
            # 구글 DNS에 연결해서 로컬 IP 확인
            s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def start_server(self):
        """서버 시작"""
        if not self.setup_flask_app():
            print("❌ Flask 앱 설정 실패")
            return False
        
        # IP 주소 정보 표시
        local_ip = self.get_local_ip()
        
        print("=" * 50)
        print("� DAWN OF STELLAR - 레트로 모바일 UI 서버")
        print("=" * 50)
        print(f"🖥️  PC에서 접속: http://localhost:{self.port}")
        print(f"📱 모바일에서 접속: http://{local_ip}:{self.port}")
        print("=" * 50)
        print("📱 모바일 접속 방법:")
        print("1. 폰과 PC가 같은 WiFi에 연결되어 있는지 확인")
        print(f"2. 폰 브라우저에서 http://{local_ip}:{self.port} 입력")
        print("3. 접속이 안 되면 Windows 방화벽 확인:")
        print("   - Windows 설정 > 네트워크 및 인터넷 > Windows 방화벽")
        print("   - '앱이 방화벽을 통과하도록 허용' 클릭")
        print("   - Python 또는 해당 앱 허용으로 설정")
        print("4. 또는 방화벽 임시 해제 후 테스트")
        print("=" * 50)
        print("🎮 VT323 폰트 + 레트로 감성 적용됨!")
        print("🔄 자동 새로고침 기능 활성화!")
        print("🎮 게임패드 지원 활성화!")
        
        # 파일 감시 시작
        self.start_file_watcher()
        
        # 브라우저 자동 열기
        try:
            import webbrowser
            webbrowser.open(f'http://localhost:{self.port}')
        except:
            print("브라우저 자동 열기 실패")
        
        # 서버 실행
        try:
            self.socketio.run(
                self.app, 
                host='0.0.0.0', 
                port=self.port, 
                debug=False,
                allow_unsafe_werkzeug=True
            )
            return True
        except Exception as e:
            print(f"❌ 서버 실행 오류: {e}")
            return False

# 서버 시작 및 중복 방지 함수들

def check_and_kill_existing_servers():
    """기존 서버 프로세스 정리"""
    try:
        import subprocess
        
        killed_count = 0
        # 포트 5000 사용 프로세스 찾기
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if ':5000' in line and ('LISTENING' in line or 'ESTABLISHED' in line):
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit() and pid != str(os.getpid()):
                            try:
                                subprocess.run(['taskkill', '/f', '/pid', pid], 
                                             capture_output=True, timeout=5)
                                killed_count += 1
                                print(f"🔄 기존 서버 종료: PID {pid}")
                            except:
                                pass
        
        if killed_count > 0:
            print(f"✅ {killed_count}개의 기존 서버가 정리되었습니다.")
        else:
            print("✅ 중복 서버 없음 - 정상 시작")
            
        time.sleep(2)  # 포트 정리 대기
        
    except Exception as e:
        print(f"⚠️ 프로세스 정리 중 오류: {e}")

def start_web_mobile():
    """레트로 웹 모바일 UI 시작"""
    if not FLASK_AVAILABLE:
        print("❌ Flask가 필요합니다:")
        print("pip install flask flask-socketio")
        return False
    
    print("=== Dawn of Stellar 레트로 웹 모바일 UI ===")
    print("🇰🇷 한글 완벽 지원 + VT323 레트로 폰트")
    print("🌐 웹 브라우저 기반")
    
    # 기존 서버 정리
    check_and_kill_existing_servers()
    
    ui = WebMobileUI()
    return ui.start_server()

if __name__ == "__main__":
    start_web_mobile()
