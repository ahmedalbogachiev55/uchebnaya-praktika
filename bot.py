import requests
import time
import json
import matplotlib.pyplot as plt
import io
from datetime import date, datetime
from db_handler import DatabaseHandler
from analyzer import Analyzer
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

TOKEN = '8746988647:AAFksZQrqQeY6ul0pDh6Q8t2Bs3aLYVSb98'
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

plt.switch_backend('Agg')

db = DatabaseHandler()

user_states = {}

def send_message(chat_id, text, reply_markup=None):
    """Отправить текстовое сообщение"""
    url = API_URL + "sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=data, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки: {e}")
    return None

def send_photo(chat_id, photo_data, caption=""):
    """Отправить фото"""
    url = API_URL + "sendPhoto"
    try:
        files = {'photo': photo_data}
        data = {'chat_id': chat_id, 'caption': caption}
        response = requests.post(url, files=files, data=data, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки фото: {e}")
    return None

def send_main_menu(chat_id):
    """Отправить главное меню с кнопками"""
    keyboard = {
        'keyboard': [
            [{'text': '➕ Записать день'}],
            [{'text': '📊 Статистика'}, {'text': '🔍 Мои инсайты'}],
            [{'text': '📜 История'}, {'text': '📉 График'}],
            [{'text': '❌ Очистить данные'}]
        ],
        'resize_keyboard': True
    }
    send_message(chat_id, "🌟 **Привет! Я трекер настроения и продуктивности!** 🌟\n\nВыбери действие:", reply_markup=keyboard)

def send_mood_keyboard(chat_id):
    """Отправить кнопки выбора настроения"""
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '1 😞', 'callback_data': 'mood_1'},
                {'text': '2 😐', 'callback_data': 'mood_2'},
                {'text': '3 🙂', 'callback_data': 'mood_3'},
                {'text': '4 😊', 'callback_data': 'mood_4'},
                {'text': '5 🤩', 'callback_data': 'mood_5'}
            ]
        ]
    }
    send_message(chat_id, "🎭 **Оцени своё настроение сегодня:**", reply_markup=keyboard)

def send_productive_keyboard(chat_id):
    """Отправить кнопки выбора часов работы"""
    keyboard = {
        'keyboard': [
            [{'text': '1'}, {'text': '2'}, {'text': '4'}],
            [{'text': '6'}, {'text': '8'}, {'text': 'Другое'}]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    send_message(chat_id, "💼 **Сколько часов ты потратил на работу/учёбу?**\n(можно ввести дробное число, например 2.5)", reply_markup=keyboard)

def send_sleep_keyboard(chat_id):
    """Отправить кнопки выбора часов сна"""
    keyboard = {
        'keyboard': [
            [{'text': '6'}, {'text': '7'}, {'text': '8'}],
            [{'text': '9'}, {'text': '10'}, {'text': 'Другое'}]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    send_message(chat_id, "😴 **Сколько часов ты спал?**\n(можно ввести дробное число, например 7.5)", reply_markup=keyboard)

def generate_mood_chart(entries):
    """Создание графика настроения"""
    if len(entries) < 2:
        return None
    
 
    dates = []
    moods = []
    productive = []
    sleep = []
    
    for entry in sorted(entries, key=lambda x: x['entry_date']):
        dates.append(entry['entry_date'])
        moods.append(entry['mood_score'])
        productive.append(entry['productive_hours'])
        sleep.append(entry['sleep_hours'])
  
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
 
    axes[0].plot(dates, moods, 'o-', color='#4CAF50', linewidth=2, markersize=8)
    axes[0].fill_between(dates, moods, alpha=0.3, color='#4CAF50')
    axes[0].set_ylim(0.5, 5.5)
    axes[0].set_yticks([1, 2, 3, 4, 5])
    axes[0].set_yticklabels(['1 😞', '2 😐', '3 🙂', '4 😊', '5 🤩'])
    axes[0].set_title('📈 Динамика настроения', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Настроение', fontsize=12)
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)

    axes[1].plot(dates, productive, 'o-', color='#2196F3', linewidth=2, markersize=8)
    axes[1].fill_between(dates, productive, alpha=0.3, color='#2196F3')
    axes[1].set_title('💪 Динамика продуктивности', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Часы работы/учебы', fontsize=12)
    axes[1].set_ylim(0, max(productive) + 2 if productive else 10)
    axes[1].grid(True, alpha=0.3)
    axes[1].tick_params(axis='x', rotation=45)
    
    
    axes[2].plot(dates, sleep, 'o-', color='#FF9800', linewidth=2, markersize=8)
    axes[2].fill_between(dates, sleep, alpha=0.3, color='#FF9800')
    axes[2].set_title('😴 Динамика сна', fontsize=14, fontweight='bold')
    axes[2].set_ylabel('Часы сна', fontsize=12)
    axes[2].set_ylim(0, max(sleep) + 2 if sleep else 12)
    axes[2].grid(True, alpha=0.3)
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

def handle_message(chat_id, text):
    """Обработка текстовых сообщений"""
    state = user_states.get(chat_id, {})
    step = state.get('step')
    
    print(f"[DEBUG] chat_id={chat_id}, step={step}, text={text}")
    
  
    if text == '/start':
        db.register_user(chat_id, None, None, None)
        send_main_menu(chat_id)
        user_states[chat_id] = {}
        return
    

    if text == '➕ Записать день':
        if db.has_entry_today(chat_id):
            send_message(chat_id, "⚠️ Запись за сегодня уже существует!\nТы можешь изменить её завтра.")
            return
        send_mood_keyboard(chat_id)
        user_states[chat_id] = {'step': 'mood'}
        return
  
    if text == '📊 Статистика':
        keyboard = {
            'inline_keyboard': [
                [{'text': '📅 За неделю', 'callback_data': 'stats_week'}],
                [{'text': '🗓 За месяц', 'callback_data': 'stats_month'}],
                [{'text': '🔍 Мои инсайты', 'callback_data': 'stats_insights'}]
            ]
        }
        send_message(chat_id, "📊 **Что хочешь узнать?**", reply_markup=keyboard)
        return
    
   
    if text == '🔍 Мои инсайты':
        entries = db.get_all_entries(chat_id)
        insights = Analyzer.get_insights(entries)
        msg = "🔍 **Твои персональные инсайты** 🔍\n\n" + "\n".join(insights)
        send_message(chat_id, msg)
        return

    if text == '📜 История':
        entries = db.get_entries_for_period(chat_id, days=30)
        if not entries:
            send_message(chat_id, "📭 История пуста. Добавь первую запись!")
            return
        msg = "📜 **История записей (последние 30 дней)**\n\n"
        for entry in entries[:10]:
            emoji = ['😞', '😐', '🙂', '😊', '🤩'][entry['mood_score'] - 1]
            msg += f"📅 {entry['entry_date']}: {emoji} Настроение {entry['mood_score']}/5 | 💪 {entry['productive_hours']}ч | 😴 {entry['sleep_hours']}ч\n"
        if len(entries) > 10:
            msg += f"\n... и ещё {len(entries) - 10} записей"
        send_message(chat_id, msg)
        return

    if text == '📉 График':
        entries = db.get_all_entries(chat_id)
        if len(entries) < 2:
            send_message(chat_id, "📊 Недостаточно данных для построения графика (нужно минимум 2 дня)")
            return
       
        chart = generate_mood_chart(entries)
        if chart:
            send_photo(chat_id, chart, caption="📈 Графики настроения, продуктивности и сна")
        else:
            send_message(chat_id, "❌ Ошибка при создании графика")
        return
 
    if text == '❌ Очистить данные':
        keyboard = {
            'inline_keyboard': [
                [{'text': '✅ Да, очистить всё', 'callback_data': 'confirm_clear'}],
                [{'text': '❌ Нет, отмена', 'callback_data': 'cancel_clear'}]
            ]
        }
        send_message(chat_id, "⚠️ **ВНИМАНИЕ!** Ты уверен, что хочешь удалить ВСЕ свои данные?\nЭто действие необратимо.", reply_markup=keyboard)
        return
    
    if step == 'productive':
        try:
            if text == 'Другое':
                send_message(chat_id, "Введи количество часов (например, 3.5):")
                return
            hours = float(text.replace(',', '.'))
            if 0 <= hours <= 24:
                user_states[chat_id]['productive_hours'] = hours
                user_states[chat_id]['step'] = 'sleep'
                send_sleep_keyboard(chat_id)
            else:
                send_message(chat_id, "❌ Введи число от 0 до 24!")
        except:
            send_message(chat_id, "❌ Введи число! (например: 5 или 2.5)")
        return
    

    if step == 'sleep':
        try:
            if text == 'Другое':
                send_message(chat_id, "Введи количество часов сна (например, 7.5):")
                return
            hours = float(text.replace(',', '.'))
            if 0 <= hours <= 24:
                mood = user_states[chat_id].get('mood', 3)
                productive = user_states[chat_id].get('productive_hours', 0)
                
                db.save_entry(
                    user_id=chat_id,
                    entry_date=date.today().isoformat(),
                    mood_score=mood,
                    productive_hours=productive,
                    sleep_hours=hours,
                    comment=None
                )
                
                mood_emoji = ['😞', '😐', '🙂', '😊', '🤩'][mood-1] if 1 <= mood <= 5 else '🙂'
                
                result = f"✅ **Запись сохранена!**\n\n"
                result += f"{mood_emoji} Настроение: {mood}/5\n"
                result += f"💪 Продуктивность: {productive} ч\n"
                result += f"😴 Сон: {hours} ч\n\n"
                result += f"Отличная работа! Продолжай в том же духе! 🎉"
                
                send_message(chat_id, result)
                send_main_menu(chat_id)
                del user_states[chat_id]
            else:
                send_message(chat_id, "❌ Введи число от 0 до 24!")
        except:
            send_message(chat_id, "❌ Введи число! (например: 8 или 7.5)")
        return

def handle_callback(chat_id, callback_data, message_id):
    """Обработка нажатий на инлайн-кнопки"""
    print(f"[DEBUG] Callback: {callback_data}")
    
    url = API_URL + "editMessageReplyMarkup"
    requests.post(url, json={'chat_id': chat_id, 'message_id': message_id, 'reply_markup': None})
    
    if callback_data.startswith('mood_'):
        mood = int(callback_data.split('_')[1])
        if chat_id not in user_states:
            user_states[chat_id] = {}
        user_states[chat_id]['mood'] = mood
        user_states[chat_id]['step'] = 'productive'
        
        mood_texts = ['', '😞 ужасно', '😐 плохо', '🙂 нормально', '😊 хорошо', '🤩 отлично']
        send_message(chat_id, f"Выбрано настроение: {mood} {mood_texts[mood]}")
        send_productive_keyboard(chat_id)
    
    elif callback_data == 'stats_week':
        entries = db.get_entries_for_period(chat_id, days=7)
        stats = Analyzer.get_weekly_stats(entries)
        if stats['total_days'] == 0:
            msg = "📊 Нет данных за неделю. Добавь несколько записей!"
        else:
            msg = f"📊 **Статистика за неделю**\n\n"
            msg += f"📅 Дней с записями: {stats['total_days']}\n"
            msg += f"😊 Среднее настроение: {stats['avg_mood']}/5\n"
            msg += f"💪 Средняя продуктивность: {stats['avg_productivity']} ч/день\n"
            msg += f"😴 Средний сон: {stats['avg_sleep']} ч/день\n"
            msg += f"📈 Лучшее настроение: {stats['best_mood']}/5\n"
            msg += f"📉 Худшее настроение: {stats['worst_mood']}/5"
        send_message(chat_id, msg)
    
    elif callback_data == 'stats_month':
        entries = db.get_entries_for_period(chat_id, days=30)
        stats = Analyzer.get_monthly_stats(entries)
        if stats['total_days'] == 0:
            msg = "📊 Нет данных за месяц. Добавь несколько записей!"
        else:
            msg = f"📊 **Статистика за месяц**\n\n"
            msg += f"📅 Дней с записями: {stats['total_days']}\n"
            msg += f"😊 Среднее настроение: {stats['avg_mood']}/5\n"
            msg += f"💪 Средняя продуктивность: {stats['avg_productivity']} ч/день\n"
            msg += f"😴 Средний сон: {stats['avg_sleep']} ч/день"
        send_message(chat_id, msg)
    
    elif callback_data == 'stats_insights':
        entries = db.get_all_entries(chat_id)
        insights = Analyzer.get_insights(entries)
        msg = "🔍 **Твои персональные инсайты** 🔍\n\n" + "\n".join(insights)
        send_message(chat_id, msg)
    
    elif callback_data == 'confirm_clear':
        db.delete_all_entries(chat_id)
        if chat_id in user_states:
            del user_states[chat_id]
        send_message(chat_id, "✅ Все твои данные успешно очищены!")
    
    elif callback_data == 'cancel_clear':
        send_message(chat_id, "❌ Очистка отменена. Данные сохранены.")

def main():
    print("=" * 50)
    print("🤖 Трекер настроения и продуктивности (с графиками)")
    print("=" * 50)
    print("Бот запущен! Отправь /start в Telegram")
    print("=" * 50)
    
    last_update_id = 0
    
    while True:
        try:
            url = API_URL + "getUpdates"
            params = {'timeout': 10, 'offset': last_update_id + 1}
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    last_update_id = update['update_id']
                    
                    if 'message' in update:
                        msg = update['message']
                        chat_id = msg['chat']['id']
                        text = msg.get('text', '')
                        print(f"📨 Сообщение: {text}")
                        handle_message(chat_id, text)
                    
                    elif 'callback_query' in update:
                        callback = update['callback_query']
                        chat_id = callback['message']['chat']['id']
                        message_id = callback['message']['message_id']
                        callback_data = callback['data']
                        print(f"🔘 Кнопка: {callback_data}")
                        handle_callback(chat_id, callback_data, message_id)
                        
                        answer_url = API_URL + "answerCallbackQuery"
                        requests.post(answer_url, json={'callback_query_id': callback['id']})
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()