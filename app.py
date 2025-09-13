#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask сервер для локальной игры Vortex
Заменяет все внешние API запросы мок данными
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import random
import time
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Глобальные переменные для состояния игры
game_state = {
    'balance': 99999900,
    'current_round': None,
    'game_history': []
}

@app.route('/')
def serve_index():
    """Отдаем главную страницу"""
    return send_from_directory('.', 'index.html')

@app.route('/no-sw')
def serve_index_no_sw():
    """Отдаем главную страницу без Service Worker"""
    return send_from_directory('.', 'index_no_sw.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Отдаем статические файлы"""
    return send_from_directory('.', filename)

@app.route('/css2')
def serve_css2():
    """Отдаем CSS файл"""
    return send_from_directory('.', 'css2', mimetype='text/css')

# ==================== API ENDPOINTS ====================

@app.route('/api/common/profile', methods=['POST'])
def profile():
    """Профиль пользователя"""
    # Создаем простой JWT-подобный токен
    import base64
    import json
    
    token_payload = {
        "id": 123456,
        "nickname": "LocalVortex",
        "balance": game_state['balance'],
        "sub": "local-demo",  # Изменяем sub для соответствия Service Worker
        "exp": int(time.time()) + 3600,  # Токен действителен 1 час
        "iat": int(time.time())
    }
    
    # Создаем правильный JWT токен
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(token_payload).encode()).decode().rstrip('=')
    fake_jwt = f"{header_b64}.{payload_b64}.fake-signature"
    
    return jsonify({
        "id": 123456,
        "playerName": "LocalVortex",          # важно: именно playerName, не nickname
        "balance": game_state['balance'],
        "currency": "FUN",                    # игра ждёт строку валюты
        "currencySign": "F",
        "rounding": 2,
        "freebetsVerified": True,
        "sub": "local-demo",
        "token": fake_jwt,
        # Добавляем поля, которые может ожидать игра
        "nickname": "LocalVortex",
        "email": "local@vortex.com",
        "avatar": None,
        "level": 1,
        "experience": 0,
        "achievements": [],
        "settings": {},
        "permissions": [],
        "roles": ["player"],
        "status": "active",
        "createdAt": "2024-01-01T00:00:00Z",
        "lastLogin": datetime.now().isoformat(),
        # Дополнительные поля, которые может ожидать игра
        "games": [],
        "bets": [],
        "transactions": [],
        "bonuses": [],
        "friends": [],
        "notifications": [],
        "messages": [],
        "history": [],
        "statistics": {},
        "preferences": {},
        "limits": {},
        "restrictions": [],
        "verification": {
            "email": True,
            "phone": False,
            "identity": False
        },
        "kyc": {
            "status": "pending",
            "documents": []
        }
    })

@app.route('/api/common/settings', methods=['GET'])
def settings():
    """Настройки игры"""
    return jsonify({
        "success": True,
        "data": {
            "availableTranslations": ["en", "ru"],
            "forceDemoAvailable": True,
            "gameSettings": {
                "minBet": 100,
                "maxBet": 1000000,
                "elements": ["fire", "earth", "water"],
                "multipliers": {
                    "fire": [1.2, 1.5, 2.0, 3.0, 5.0],
                    "earth": [1.1, 1.3, 1.8, 2.5, 4.0],
                    "water": [1.0, 1.2, 1.6, 2.2, 3.5]
                }
            }
        }
    })

@app.route('/api/games/settings', methods=['GET'])
@app.route('/v2/api/games/settings', methods=['GET'])
def game_settings():
    """Настройки конкретной игры - соответствует MSW мокам"""
    return jsonify({
        "gameId": "vortex",
        "version": "1.0",
        "minBet": 100,
        "maxBet": 1000000,
        "defaultBet": 1000,
        "currency": "FUN",
        "currencySign": "F",
        "rounding": 2,
        "Symbol1": [3.9, 5.2, 7.7, 12.5, 18.0, 24.0, 32.0, 44.0, 60.0, 80.0, 110.0, 150.0],
        "Symbol2": [1.2, 1.6, 2.1, 3.2, 4.85, 7.0, 9.0, 12.0, 16.0, 20.0, 24.0, 30.0],
        "Symbol3": [1.1, 1.3, 1.55, 2.0, 3.0, 5.0, 7.0, 10.0, 12.5, 15.0, 20.0, 25.0],
        "elements": ["fire", "earth", "water"],
        "multipliers": {
            "fire": [1.2, 1.5, 2.0, 3.0, 5.0],
            "earth": [1.1, 1.3, 1.8, 2.5, 4.0],
            "water": [1.0, 1.2, 1.6, 2.2, 3.5]
        }
    })

@app.route('/api/games/create', methods=['POST'])
@app.route('/v2/api/games/create', methods=['POST'])
def create_game():
    """Создание нового раунда игры"""
    round_id = f"round-{int(time.time() * 1000)}"
    game_state['current_round'] = {
        'id': round_id,
        'state': 'created',
        'salt': f"fake-salt-{uuid.uuid4().hex[:16]}",
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({
        "roundId": round_id,
        "state": {
            "initial": True,
            "collection": [0, 0, 0],
            "bonusWin": 0,
            "superBonus": False,
            "symbol": "SymbolNeutral",
            "cashable": False
        }
    })

@app.route('/api/games/retrieve', methods=['POST'])
def retrieve_game():
    """Получение информации о текущем раунде"""
    if game_state['current_round']:
        return jsonify({
            "success": True,
            "data": game_state['current_round']
        })
    else:
        return jsonify({
            "success": False,
            "error": "No active games"
        }), 404

@app.route('/api/bets/place', methods=['POST'])
@app.route('/v2/api/bets/place', methods=['POST'])
def place_bet():
    """Размещение ставки - соответствует MSW мокам"""
    data = request.get_json()
    
    # Списываем ставку с баланса
    amount = data.get('amount', 100)
    game_state['balance'] -= amount
    
    # Генерируем результат игры (как в MSW)
    symbols = ["Symbol1", "Symbol2", "Symbol3"]
    result_symbol = random.choice(symbols)
    
    # Определяем выигрыш
    multipliers = {
        "Symbol1": [3.9, 5.2, 7.7, 12.5, 18.0, 24.0, 32.0, 44.0, 60.0, 80.0, 110.0, 150.0],
        "Symbol2": [1.2, 1.6, 2.1, 3.2, 4.85, 7.0, 9.0, 12.0, 16.0, 20.0, 24.0, 30.0],
        "Symbol3": [1.1, 1.3, 1.55, 2.0, 3.0, 5.0, 7.0, 10.0, 12.5, 15.0, 20.0, 25.0]
    }
    
    # 80% шанс на выигрыш
    if random.random() < 0.8:
        coefficient = random.choice(multipliers[result_symbol])
        payout = amount * coefficient
        result = 'won'
        autocashout = random.random() < 0.3  # 30% шанс на автокешаут
    else:
        coefficient = 0
        payout = 0
        result = 'lost'
        autocashout = False
    
    # Если автокешаут - сразу зачисляем выигрыш
    if autocashout:
        game_state['balance'] += payout
    
    # Генерируем состояние игры
    collection = [0, 0, 0]
    if result_symbol == "Symbol1":
        collection[2] = 1  # blue
    elif result_symbol == "Symbol2":
        collection[1] = 1  # green
    elif result_symbol == "Symbol3":
        collection[0] = 1  # red
    
    game_state = {
        'initial': False,
        'collection': collection,
        'bonusWin': 0,
        'superBonus': False,
        'symbol': result_symbol,
        'cashable': payout > 0
    }
    
    round_id = f"round-{int(time.time() * 1000)}"
    
    return jsonify({
        "state": game_state,
        "result": result,
        "payout": payout,
        "coefficient": coefficient,
        "autocashout": autocashout,
        "roundId": round_id
    })

@app.route('/api/bets/cashout', methods=['POST'])
@app.route('/v2/api/bets/cashout', methods=['POST'])
def cashout():
    """Кешаут ставки - соответствует MSW мокам"""
    # Зачисляем payout в баланс
    payout = random.uniform(1, 4)  # Случайный выигрыш 1-4
    game_state['balance'] += payout
    
    # Возвращаем обнуленное состояние (как в MSW)
    new_state = {
        'initial': True,
        'collection': [0, 0, 0],
        'bonusWin': 0,
        'superBonus': False,
        'symbol': 'SymbolNeutral',
        'cashable': False
    }
    
    round_id = f"round-{int(time.time() * 1000)}"
    
    return jsonify({
        "state": new_state,
        "result": "won",
        "payout": payout,
        "coefficient": random.uniform(1, 3),
        "roundId": round_id
    })

@app.route('/api/games/freebets/interrupt', methods=['POST'])
def interrupt_freebets():
    """Прерывание бесплатных ставок"""
    return jsonify({
        "success": True,
        "data": {
            "message": "Freebets interrupted"
        }
    })

@app.route('/api/common/tournaments/my', methods=['GET'])
def my_tournaments():
    """Мои турниры"""
    return jsonify({
        "success": True,
        "data": []
    })

@app.route('/api/translates/<project_id>/latest/<locale>', methods=['GET'])
def get_translations(project_id, locale):
    """Переводы"""
    translations = {
        "COMMON.PLEASE_LOGIN": "PLEASE LOGIN",
        "GAME.SPIN": "SPIN",
        "GAME.CASHOUT": "CASHOUT",
        "GAME.BET": "BET",
        "GAME.BALANCE": "BALANCE",
        "GAME.WIN": "WIN",
        "GAME.LOSE": "LOSE",
        "ELEMENTS.FIRE": "FIRE",
        "ELEMENTS.EARTH": "EARTH",
        "ELEMENTS.WATER": "WATER"
    }
    return jsonify(translations)

@app.route('/api/translates/<project_id>/latest/<locale>/<key>', methods=['GET'])
def get_translations_with_key(project_id, locale, key):
    """Переводы с ключом"""
    translations = {
        "COMMON.PLEASE_LOGIN": "PLEASE LOGIN",
        "GAME.SPIN": "SPIN",
        "GAME.CASHOUT": "CASHOUT",
        "GAME.BET": "BET",
        "GAME.BALANCE": "BALANCE",
        "GAME.WIN": "WIN",
        "GAME.LOSE": "LOSE",
        "ELEMENTS.FIRE": "FIRE",
        "ELEMENTS.EARTH": "EARTH",
        "ELEMENTS.WATER": "WATER"
    }
    return jsonify(translations)

@app.route('/api/games/history', methods=['GET'])
def game_history():
    """История игр"""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    history = game_state['game_history'][offset:offset + limit]
    
    return jsonify({
        "success": True,
        "data": {
            "history": history,
            "total": len(game_state['game_history']),
            "limit": limit,
            "offset": offset
        }
    })

@app.route('/api/player/statistics', methods=['POST'])
def player_statistics():
    """Статистика игрока"""
    return jsonify({
        "success": True,
        "data": {
            "totalBets": len(game_state['game_history']),
            "totalWins": len([h for h in game_state['game_history'] if h['result'] == 'win']),
            "totalLosses": len([h for h in game_state['game_history'] if h['result'] == 'lose']),
            "winRate": 0.7,
            "totalWagered": sum([h.get('amount', 100) for h in game_state['game_history']]),
            "totalWon": sum([h['payout'] for h in game_state['game_history'] if h['result'] == 'win'])
        }
    })

@app.route('/api/limits', methods=['GET'])
def get_limits():
    """Лимиты ставок"""
    return jsonify({
        "success": True,
        "data": {
            "minBet": 100,
            "maxBet": 1000000,
            "dailyLimit": 10000000,
            "currency": "FUN"
        }
    })

@app.route('/api/rates', methods=['GET'])
def get_rates():
    """Курсы валют"""
    return jsonify({
        "success": True,
        "data": {
            "FUN": {
                "rate": 1.0,
                "symbol": "FUN"
            }
        }
    })

@app.route('/api/player', methods=['PUT'])
def update_player():
    """Обновление данных игрока"""
    data = request.get_json()
    return jsonify({
        "success": True,
        "data": {
            "message": "Player updated successfully",
            "nickname": data.get('nickname', 'LocalVortex')
        }
    })

@app.route('/api/bets/<bet_id>', methods=['GET'])
def get_bet(bet_id):
    """Получение информации о ставке"""
    bet = next((h for h in game_state['game_history'] if h['id'] == bet_id), None)
    if bet:
        return jsonify({
            "success": True,
            "data": bet
        })
    else:
        return jsonify({
            "success": False,
            "error": "Bet not found"
        }), 404


# ==================== WEBSOCKET MOCK ====================

@app.route('/connection/websocket', methods=['GET'])
def websocket_mock():
    """Мок WebSocket соединения"""
    return jsonify({
        "success": True,
        "data": {
            "message": "WebSocket connection mocked",
            "status": "connected"
        }
    })

# Дополнительные endpoints для исправления ошибок
@app.route('/api/common/limits', methods=['GET'])
def common_limits():
    """Общие лимиты"""
    return jsonify({
        "success": True,
        "data": {
            "minBet": 100,
            "maxBet": 1000000,
            "currency": "FUN"
        }
    })

@app.route('/api/common/rates', methods=['GET'])
def common_rates():
    """Общие курсы"""
    return jsonify({
        "success": True,
        "data": {
            "FUN": {
                "rate": 1.0,
                "symbol": "FUN",
                "name": "Fun Coins"
            }
        }
    })

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Получение профиля"""
    return jsonify({
        "success": True,
        "data": {
            "id": 123456,
            "nickname": "LocalVortex",
            "balance": game_state['balance'],
            "currency": {
                "iso": "FUN",
                "rate": 1,
                "min_in": 100,
                "min_out": 100,
                "symbol": "FUN",
                "name": "Fun Coins"
            }
        }
    })

@app.route('/api/profile', methods=['POST'])
def update_profile():
    """Обновление профиля"""
    return jsonify({
        "success": True,
        "data": {
            "message": "Profile updated successfully"
        }
    })

if __name__ == '__main__':
    print("🚀 Запуск локального сервера Vortex...")
    print("📱 Игра будет доступна по адресу: http://localhost:8000")
    print("🎮 Все API запросы заменены на мок данные")
    print("🌐 Игра работает полностью автономно!")
    
    app.run(host='0.0.0.0', port=8000, debug=True)