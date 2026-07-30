import json
import random
from datetime import datetime, timedelta
from database import get_player, update_player, get_completed_events, add_event_to_history, add_achievement
from events import get_event_for_stage, process_event

def get_stage_name(stage):
    stages = ["🧬 Человек", "💪 Сверхчеловек", "⚙️ Киборг", "🤖 Машина", "👑 Бог"]
    return stages[stage] if stage < len(stages) else "👑 Бог"

def get_stat_sum(stats):
    return sum([stats.get("strength", 0), stats.get("intelligence", 0),
                stats.get("endurance", 0), stats.get("speed", 0),
                stats.get("luck", 0)])

def check_evolution(stats, stage):
    """Проверяет, может ли игрок эволюционировать"""
    total = get_stat_sum(stats)
    thresholds = [100, 200, 350, 550, 800]  # Сумма для каждой стадии
    
    for i in range(stage+1, len(thresholds)):
        if total >= thresholds[i]:
            return i
    return -1

def get_daily_event(user_id):
    """Генерирует дневное событие для игрока"""
    player = get_player(user_id)
    if not player:
        return None, None
    
    # Парсим данные
    stats = {
        "strength": player[4],
        "intelligence": player[5],
        "endurance": player[6],
        "speed": player[7],
        "luck": player[8],
        "resources": player[9]
    }
    
    completed_ids = get_completed_events(user_id)
    event = get_event_for_stage(player[2], completed_ids)
    
    if not event:
        # Если все события пройдены - бонусный день
        bonus = random.randint(10, 30)
        return None, f"🌟 Вы прошли все события! Получите бонус +{bonus} ко всем характеристикам!"
    
    return event, None

def apply_event_result(user_id, event, choice_index):
    """Применяет результат события и обновляет БД"""
    player = get_player(user_id)
    stats = {
        "strength": player[4],
        "intelligence": player[5],
        "endurance": player[6],
        "speed": player[7],
        "luck": player[8],
        "resources": player[9],
        "health": player[12]
    }
    
    result = process_event(stats, event, choice_index)
    
    # Обновляем характеристики
    new_stats = stats.copy()
    for stat, change in result["stats_change"].items():
        if stat in new_stats:
            new_stats[stat] = max(0, new_stats[stat] + change)
    
    new_stats["resources"] = max(0, new_stats["resources"] + result["resources_change"])
    new_stats["health"] = max(0, min(100, new_stats["health"] + result["health_change"]))
    
    # Сохраняем в БД
    update_player(
        user_id,
        strength=new_stats["strength"],
        intelligence=new_stats["intelligence"],
        endurance=new_stats["endurance"],
        speed=new_stats["speed"],
        luck=new_stats["luck"],
        resources=new_stats["resources"],
        health=new_stats["health"],
        day=player[3] + 1
    )
    
    # Добавляем в историю
    completed_ids = get_completed_events(user_id)
    completed_ids.append(event["id"])
    update_player(user_id, completed_events=json.dumps(completed_ids))
    add_event_to_history(user_id, event["id"], result["message"])
    
    # Проверяем достижения
    check_achievements(user_id, new_stats)
    
    return result, new_stats

def check_achievements(user_id, stats):
    """Проверяет и выдает достижения"""
    achievements = [
        {"name": "💪 Силач", "check": stats["strength"] >= 50},
        {"name": "🧠 Гений", "check": stats["intelligence"] >= 50},
        {"name": "🏃 Спринтер", "check": stats["speed"] >= 50},
        {"name": "🍀 Удачливый", "check": stats["luck"] >= 50},
        {"name": "📚 Эрудит", "check": stats["intelligence"] >= 30 and stats["strength"] >= 30},
        {"name": "👑 Полубог", "check": sum(stats.values()) >= 300},
        {"name": "🌌 Космический", "check": sum(stats.values()) >= 500},
        {"name": "💎 Магнат", "check": stats["resources"] >= 500},
        {"name": "🦾 Кибер-воин", "check": stats["strength"] >= 80 and stats["endurance"] >= 80},
        {"name": "🧬 Эволюционер", "check": sum(stats.values()) >= 800}
    ]
    
    for ach in achievements:
        if ach["check"]:
            add_achievement(user_id, ach["name"])

def get_daily_bonus(user_id):
    """Ежедневный бонус за вход"""
    player = get_player(user_id)
    if not player:
        return "Ошибка"
    
    last_bonus = datetime.fromisoformat(player[14])
    if (datetime.now() - last_bonus).days >= 1:
        bonus = random.randint(5, 15)
        update_player(
            user_id,
            resources=player[9] + bonus,
            daily_bonus=datetime.now().isoformat(),
            day=player[3] + 1
        )
        return f"🎁 Дневной бонус: +{bonus} ресурсов!"
    return "⏳ Бонус уже получен сегодня!"

def get_stats_text(user_id):
    """Формирует красивую статистику игрока"""
    player = get_player(user_id)
    if not player:
        return "Игрок не найден"
    
    stage_name = get_stage_name(player[2])
    total_stats = player[4] + player[5] + player[6] + player[7] + player[8]
    
    return f"""
👤 **{player[1] or 'Аноним'}**

🧬 Стадия: {stage_name}
📅 День: {player[3]}

📊 **Характеристики:**
💪 Сила: {player[4]}
🧠 Интеллект: {player[5]}
🛡️ Выносливость: {player[6]}
💨 Скорость: {player[7]}
🍀 Удача: {player[8]}
🏦 Ресурсы: {player[9]}

❤️ Здоровье: {player[12]}/{player[13]}
⚡ Сумма статов: {total_stats}

🏆 Достижений: {len(get_achievements(user_id))}
💀 Смертей: {player[15]}
⭐ Донатов: {player[16]}
"""

def get_evolution_tree(user_id):
    """Древо эволюции с прогрессом"""
    player = get_player(user_id)
    if not player:
        return "Ошибка"
    
    total = player[4] + player[5] + player[6] + player[7] + player[8]
    current_stage = player[2]
    
    stages = [
        {"name": "🧬 Человек", "need": 0},
        {"name": "💪 Сверхчеловек", "need": 100},
        {"name": "⚙️ Киборг", "need": 200},
        {"name": "🤖 Машина", "need": 350},
        {"name": "👑 Бог", "need": 550}
    ]
    
    tree = "🌳 **Древо Эволюции**\n\n"
    for i, stage in enumerate(stages):
        if i <= current_stage:
            tree += f"✅ {stage['name']} (достигнуто)\n"
        elif i == current_stage + 1:
            progress = min(100, int((total - stages[current_stage]['need']) / 
                                   (stage['need'] - stages[current_stage]['need']) * 100))
            tree += f"🔄 {stage['name']} — {progress}%\n"
        else:
            tree += f"⬜ {stage['name']}\n"
    
    tree += f"\n📊 Сумма статов: {total}"
    return tree
