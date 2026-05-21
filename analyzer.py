class Analyzer:
    @staticmethod
    def get_insights(entries):
        """Генерация персонализированных инсайтов"""
        if len(entries) < 5:
            return [" Накопите больше данных (минимум 5 дней) для точных выводов!"]
        
        total_mood = 0
        total_sleep = 0
        total_work = 0
        good_days = 0
        bad_days = 0
        
        for entry in entries:
            total_mood += entry['mood_score']
            total_sleep += entry['sleep_hours']
            total_work += entry['productive_hours']
            if entry['mood_score'] >= 4:
                good_days += 1
            elif entry['mood_score'] <= 2:
                bad_days += 1
        
        avg_mood = total_mood / len(entries)
        avg_sleep = total_sleep / len(entries)
        avg_work = total_work / len(entries)
        
        insights = []
        insights.append(f"\n📊 **Ваши средние показатели за {len(entries)} дней:**")
        insights.append(f"• Настроение: {round(avg_mood, 1)}/5")
        insights.append(f"• Сон: {round(avg_sleep, 1)} часов")
        insights.append(f"• Учёба/работа: {round(avg_work, 1)} часов")
        insights.append(f"• Хороших дней (4-5): {good_days}")
        insights.append(f"• Плохих дней (1-2): {bad_days}")
        
        
        if avg_sleep < 6:
            insights.append("\n⚠️ **Инсайт:** Вы мало спите (менее 6 часов). Постарайтесь спать 7-8 часов!")
        elif avg_sleep > 9:
            insights.append("\n⚠️ **Инсайт:** Вы много спите. Возможно, стоит сократить сон до 7-8 часов.")
        elif 7 <= avg_sleep <= 8:
            insights.append("\n✅ **Отлично!** Ваша норма сна в пределах рекомендаций (7-8 часов).")
        
        if avg_work > 8:
            insights.append("\n⚠️ **Инсайт:** Вы много работаете/учитесь (более 8 часов). Не забывайте отдыхать!")
        
        if good_days > len(entries) // 2:
            insights.append("\n😊 **Поздравляю!** У вас больше хороших дней, чем плохих! Так держать!")
        
        return insights
    
    @staticmethod
    def get_weekly_stats(entries):
        """Статистика за неделю"""
        if not entries:
            return {'total_days': 0, 'avg_mood': 0, 'avg_productivity': 0, 'avg_sleep': 0, 'best_mood': 0, 'worst_mood': 0}
        
        total_mood = 0
        total_sleep = 0
        total_work = 0
        best_mood = 0
        worst_mood = 5
        
        for entry in entries:
            total_mood += entry['mood_score']
            total_sleep += entry['sleep_hours']
            total_work += entry['productive_hours']
            best_mood = max(best_mood, entry['mood_score'])
            worst_mood = min(worst_mood, entry['mood_score'])
        
        return {
            'total_days': len(entries),
            'avg_mood': round(total_mood / len(entries), 1),
            'avg_productivity': round(total_work / len(entries), 1),
            'avg_sleep': round(total_sleep / len(entries), 1),
            'best_mood': best_mood,
            'worst_mood': worst_mood
        }
    
    @staticmethod
    def get_monthly_stats(entries):
        """Статистика за месяц"""
        if not entries:
            return {'total_days': 0, 'avg_mood': 0, 'avg_productivity': 0, 'avg_sleep': 0}
        
        total_mood = 0
        total_sleep = 0
        total_work = 0
        
        for entry in entries:
            total_mood += entry['mood_score']
            total_sleep += entry['sleep_hours']
            total_work += entry['productive_hours']
        
        return {
            'total_days': len(entries),
            'avg_mood': round(total_mood / len(entries), 1),
            'avg_productivity': round(total_work / len(entries), 1),
            'avg_sleep': round(total_sleep / len(entries), 1)
        }