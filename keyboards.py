from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
         InlineKeyboardButton(text="🌳 Древо", callback_data="tree")],
        [InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus"),
         InlineKeyboardButton(text="⚡ Действие", callback_data="action")],
        [InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements"),
         InlineKeyboardButton(text="💎 Донат", callback_data="donate")]
    ])

def event_keyboard(event):
    """Создает клавиатуру для события"""
    kb = InlineKeyboardMarkup()
    for i, option in enumerate(event["options"]):
        kb.add(InlineKeyboardButton(text=option["text"], callback_data=f"event_{i}"))
    return kb

def action_after_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back")]
    ])
