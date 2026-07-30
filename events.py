import random

# Все события разделены по стадиям и сложности
EVENTS = {
    # Ранние события (стадия 0-1)
    "easy": [
        {
            "id": 1,
            "title": "🌿 Находка в лесу",
            "description": "Вы нашли странный светящийся гриб. Что делать?",
            "options": [
                {"text": "Съесть", "check": "luck", "threshold": 15, 
                 "success": "🍄 Гриб дал +5 к Интеллекту!", 
                 "fail": "🤢 Отравление! -10 здоровья"},
                {"text": "Продать", "check": "resources", "threshold": 20,
                 "success": "💰 +30 ресурсов", 
                 "fail": "Никто не купил :("}
            ]
        },
        {
            "id": 2,
            "title": "🐺 Стая волков",
            "description": "На вас напала стая диких волков!",
            "options": [
                {"text": "Сражаться", "check": "strength", "threshold": 20,
                 "success": "⚔️ Победа! +10 Силы", 
                 "fail": "🩸 Поражение! -25 здоровья, -5 ресурсов"},
                {"text": "Убежать", "check": "speed", "threshold": 15,
                 "success": "💨 Успели! +5 Скорости", 
                 "fail": "🏃 Не хватило скорости! -15 здоровья"}
            ]
        },
        {
            "id": 3,
            "title": "📜 Древние руны",
            "description": "Вы нашли пещеру с рунами на стенах.",
            "options": [
                {"text": "Изучить", "check": "intelligence", "threshold": 18,
                 "success": "🔮 Вы открыли тайну! +15 Интеллекта", 
                 "fail": "🤔 Слишком сложно. -5 ресурсов"},
                {"text": "Срисовать", "check": "luck", "threshold": 10,
                 "success": "🎨 Продали рисунок за +20 ресурсов", 
                 "fail": "❌ Ничего не вышло"}
            ]
        }
    ],
    
    # Средние события (стадия 1-2)
    "medium": [
        {
            "id": 4,
            "title": "🏭 Заброшенный завод",
            "description": "Вы нашли старый кибернетический завод.",
            "options": [
                {"text": "Разобрать на запчасти", "check": "strength", "threshold": 35,
                 "success": "⚙️ Нашли +50 ресурсов и очки киборга!", 
                 "fail": "💥 Авария! -20 здоровья"},
                {"text": "Починить", "check": "intelligence", "threshold": 30,
                 "success": "🦾 Починили! +15 Интеллекта", 
                 "fail": "🔧 Сломали окончательно"}
            ]
        },
        {
            "id": 5,
            "title": "👽 Инопланетный артефакт",
            "description": "С неба упал странный артефакт!",
            "options": [
                {"text": "Активировать", "check": "luck", "threshold": 25,
                 "success": "✨ +20 ко всем характеристикам!", 
                 "fail": "💀 Взрыв! -30 здоровья"},
                {"text": "Изучить", "check": "intelligence", "threshold": 35,
                 "success": "🧠 Новая технология! +20 Интеллекта", 
                 "fail": "🤯 Ничего не поняли"}
            ]
        }
    ],
    
    # Сложные события (стадия 2-3)
    "hard": [
        {
            "id": 6,
            "title": "🤖 Восстание машин",
            "description": "ИИ взбунтовался и атакует город!",
            "options": [
                {"text": "Взять командование", "check": "intelligence", "threshold": 50,
                 "success": "🧠 Вы перехватили управление! +30 Интеллекта", 
                 "fail": "💻 Система перегружена! -50 ресурсов"},
                {"text": "Физический бой", "check": "strength", "threshold": 45,
                 "success": "💪 Уничтожили ИИ! +30 Силы", 
                 "fail": "⚡ Поражение! -40 здоровья"}
            ]
        },
        {
            "id": 7,
            "title": "🌌 Космический шторм",
            "description": "Пространство искажается из-за гравитационной аномалии!",
            "options": [
                {"text": "Пройти сквозь", "check": "endurance", "threshold": 40,
                 "success": "🌀 Вы выжили! +25 Выносливости", 
                 "fail": "💫 Потеря сознания! -35 здоровья"},
                {"text": "Использовать технологии", "check": "intelligence", "threshold": 45,
                 "success": "🚀 Открыли новый способ перемещения!", 
                 "fail": "⚡ Сбой! -30 ресурсов"}
            ]
        }
    ],
    
    # Эпические события (стадия 3-4)
    "epic": [
        {
            "id": 8,
            "title": "👑 Испытание Богов",
            "description": "Вы вызваны на суд к создателям вселенной!",
            "options": [
                {"text": "Принять вызов", "check": "strength", "threshold": 70,
                 "success": "⚡ Вы доказали свою силу! +40 ко всем характеристикам", 
                 "fail": "🌩️ Боги разгневаны! -50 здоровья"},
                {"text": "Обмануть богов", "check": "intelligence", "threshold": 75,
                 "success": "🧠 Боги впечатлены вашим умом! +50 Интеллекта", 
                 "fail": "🔮 Проклятие! -50 ресурсов"}
            ]
        }
    ]
}

def get_event_for_stage(stage, completed_ids):
    """Выбирает случайное событие, которое игрок еще не проходил"""
    available = []
    
    if stage <= 1:
        available.extend(EVENTS["easy"])
    if stage >= 1 and stage <= 2:
        available.extend(EVENTS["medium"])
    if stage >= 2 and stage <= 3:
        available.extend(EVENTS["hard"])
    if stage >= 3:
        available.extend(EVENTS["epic"])
    
    # Фильтруем пройденные
    available = [e for e in available if e["id"] not in completed_ids]
    
    # Если все события пройдены - генерируем случайное с бонусом
    if not available:
        return None
    
    return random.choice(available)

def process_event(user_stats, event, choice_index):
    """Обрабатывает выбор игрока и возвращает результат"""
    option = event["options"][choice_index]
    check_stat = option["check"]
    threshold = option["threshold"]
    stat_value = user_stats.get(check_stat, 0)
    
    success = stat_value >= threshold
    
    result = {
        "success": success,
        "message": "",
        "stats_change": {},
        "resources_change": 0,
        "health_change": 0
    }
    
    if success:
        # Успешный исход
        if "success" in option:
            result["message"] = option["success"]
        # Парсим изменения из сообщения успеха
        import re
        numbers = re.findall(r'[+-]?\d+', option["success"])
        changes = [int(n) for n in numbers if n]
        
        # Распределяем изменения по характеристикам (упрощенная логика)
        if "Силы" in option["success"]:
            result["stats_change"]["strength"] = changes[0] if changes else 5
        elif "Интеллекта" in option["success"]:
            result["stats_change"]["intelligence"] = changes[0] if changes else 5
        elif "Выносливости" in option["success"]:
            result["stats_change"]["endurance"] = changes[0] if changes else 5
        elif "Скорости" in option["success"]:
            result["stats_change"]["speed"] = changes[0] if changes else 5
        elif "ресурсов" in option["success"]:
            result["resources_change"] = changes[0] if changes else 20
        elif "здоровья" in option["success"]:
            result["health_change"] = changes[0] if changes else 10
    else:
        # Провал
        if "fail" in option:
            result["message"] = option["fail"]
        import re
        numbers = re.findall(r'[+-]?\d+', option["fail"])
        changes = [int(n) for n in numbers if n]
        
        if "здоровья" in option["fail"]:
            result["health_change"] = changes[0] if changes else -10
        elif "ресурсов" in option["fail"]:
            result["resources_change"] = changes[0] if changes else -10
        elif "Силы" in option["fail"]:
            result["stats_change"]["strength"] = changes[0] if changes else -5
        elif "Интеллекта" in option["fail"]:
            result["stats_change"]["intelligence"] = changes[0] if changes else -5
    
    return result
