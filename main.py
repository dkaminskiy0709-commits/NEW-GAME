import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from config import BOT_TOKEN, DONATE_LINK, STARS_PRICE
from database import init_db, get_player, create_player, update_player, get_achievements
from game_engine import (
    get_daily_event, apply_event_result, get_stats_text, 
    get_evolution_tree, check_evolution, get_stage_name,
    get_daily_bonus
)
from keyboards import main_menu, event_keyboard

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранилище для активных событий
active_events = {}

@dp.message(F.text == "/start")
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Игрок"
    
    if not get_player(user_id):
        create_player(user_id, username)
    
    await message.answer(
        f"🚀 **Добро пожаловать в Эволюцию!**\n\n"
        f"Ты — {username}. Твой путь от человека до Бога начинается!\n"
        f"📅 В день происходит 1 событие, на которое ты можешь повлиять.\n"
        f"📖 Прокачивай характеристики и проходи эволюцию!\n\n"
        f"🎯 Цель: достичь стадии **Бог** за 60 дней.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(
        "🚀 Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    text = get_stats_text(user_id)
    await callback.message.edit_text(
        text,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "tree")
async def show_tree(callback: CallbackQuery):
    user_id = callback.from_user.id
    text = get_evolution_tree(user_id)
    await callback.message.edit_text(
        text,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "bonus")
async def daily_bonus(callback: CallbackQuery):
    user_id = callback.from_user.id
    result = get_daily_bonus(user_id)
    await callback.message.edit_text(
        result,
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "action")
async def daily_action(callback: CallbackQuery):
    user_id = callback.from_user.id
    player = get_player(user_id)
    
    if not player:
        await callback.answer("Ошибка!")
        return
    
    # Проверяем, не делал ли игрок уже действие сегодня
    last_played = datetime.fromisoformat(player[11])
    if (datetime.now() - last_played).days < 1 and get_completed_events(user_id):
        await callback.message.edit_text(
            "⏳ Ты уже совершил действие сегодня! Приходи завтра.",
            reply_markup=main_menu()
        )
        await callback.answer()
        return
    
    event, bonus = get_daily_event(user_id)
    
    if bonus:
        # Бонусный день
        await callback.message.edit_text(
            bonus,
            reply_markup=main_menu()
        )
        update_player(user_id, last_played=datetime.now().isoformat())
        await callback.answer()
        return
    
    if not event:
        await callback.message.edit_text(
            "🌟 Ты прошел все события! Получаешь супер-бонус +50 ко всем характеристикам!",
            reply_markup=main_menu()
        )
        # Даем финальный бонус
        player = get_player(user_id)
        update_player(
            user_id,
            strength=player[4] + 10,
            intelligence=player[5] + 10,
            endurance=player[6] + 10,
            speed=player[7] + 10,
            luck=player[8] + 10
        )
        await callback.answer()
        return
    
    # Сохраняем событие для обработки
    active_events[user_id] = event
    
    # Показываем событие с кнопками
    text = f"📖 **{event['title']}**\n\n{event['description']}"
    await callback.message.edit_text(
        text,
        reply_markup=event_keyboard(event),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("event_"))
async def handle_event(callback: CallbackQuery):
    user_id = callback.from_user.id
    choice_index = int(callback.data.split("_")[1])
    
    event = active_events.get(user_id)
    if not event:
        await callback.message.edit_text(
            "❌ Событие истекло. Начни заново через /start",
            reply_markup=main_menu()
        )
        await callback.answer()
        return
    
    # Применяем выбор
    result, new_stats = apply_event_result(user_id, event, choice_index)
    
    # Проверяем эволюцию
    player = get_player(user_id)
    new_stage = check_evolution(new_stats, player[2])
    evolution_msg = ""
    
    if new_stage > player[2]:
        update_player(user_id, stage=new_stage)
        evolution_msg = f"\n\n🎉 **ЭВОЛЮЦИЯ!** Ты стал {get_stage_name(new_stage)}!"
    
    # Формируем ответ
    stats_text = f"""
📊 **Результат:**
{result['message']}
{evolution_msg}

Текущие характеристики:
💪 Сила: {new_stats['strength']}
🧠 Интеллект: {new_stats['intelligence']}
🛡️ Выносливость: {new_stats['endurance']}
💨 Скорость: {new_stats['speed']}
🍀 Удача: {new_stats['luck']}
🏦 Ресурсы: {new_stats['resources']}
❤️ Здоровье: {new_stats['health']}%
"""
    
    # Проверяем смерть
    if new_stats['health'] <= 0:
        stats_text += "\n💀 **ТЫ УМЕР!** Следующий день начни с восстановления (-20% ресурсов)."
        update_player(user_id, died=player[15] + 1, health=50, resources=max(0, new_stats['resources'] - 20))
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=main_menu()
    )
    
    # Удаляем событие
    del active_events[user_id]
    await callback.answer()

@dp.callback_query(F.data == "achievements")
async def show_achievements(callback: CallbackQuery):
    user_id = callback.from_user.id
    achievements = get_achievements(user_id)
    
    if not achievements:
        text = "🏆 У тебя пока нет достижений. Играй дальше!"
    else:
        text = "🏆 **Твои достижения:**\n\n" + "\n".join([f"• {ach}" for ach in achievements])
    
    await callback.message.edit_text(
        text,
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "donate")
async def donate_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        f"💎 **Поддержать развитие игры**\n\n"
        f"Твоя помощь поможет добавить новые события и стадии эволюции!\n"
        f"⭐ Цена доната: {STARS_PRICE} Telegram Stars\n\n"
        f"👉 [Поддержать через Boosty]({DONATE_LINK})\n"
        f"👉 [Поддержать через Telegram Stars](tg://resolve?domain=BotFather&start=donate)\n\n"
        f"После доната напиши /donate_{ТВОЙ_АЙДИ} для активации.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(F.text.startswith("/donate_"))
async def process_donate(message: Message):
    user_id = int(message.text.split("_")[1])
    if user_id != message.from_user.id:
        await message.answer("❌ Это не твой код доната!")
        return
    
    update_player(user_id, donates=1)
    await message.answer(
        "⭐ Спасибо за поддержку!\n"
        "Ты получил +30 ко всем характеристикам в знак благодарности!",
        reply_markup=main_menu()
    )
    
    # Даем бонус
    player = get_player(user_id)
    update_player(
        user_id,
        strength=player[4] + 30,
        intelligence=player[5] + 30,
        endurance=player[6] + 30,
        speed=player[7] + 30,
        luck=player[8] + 30
    )

async def main():
    init_db()
    print("🚀 Игра «Эволюция» запущена!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
