import telebot
from telebot import types
import openai
import datetime
import json

from data.commands import commands  # Справочник команд
from data.schedule_upper_week import upper_schedule_text  # Расписание верхней недели
from data.schedule_lower_week import lower_schedule_text  # Расписание нижней недели


with open("keys/PMRhelper_API", 'r') as TOKEN:
    bot = telebot.TeleBot(token=TOKEN.read())


with open("keys/ChatGPT_API", 'r') as KEY:
    openai.api_key = KEY.read()


with open('keys\whitelist.json', 'r') as f:
    whitelist = json.loads(f.read())


with open('keys\whitelist_admin.json', 'r') as f:
    admin_whitelist = json.loads(f.read())


check_whitelist = lambda message: message.chat.id in whitelist
check_admin = lambda message: message.chat.id in admin_whitelist


@bot.message_handler(commands=['chat_id'])
def check_id(message):
    """Выводит id чата"""
    bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(commands=['start'], func=check_whitelist)
def starter_bot(message):
    """Стартовое сообщение и кнопка начать"""
    mess = 'Приветствую!\n\n' \
           'Я - бот-помощник студентов группы ПМР\n\n' \
           'Я стараюсь быть полезным для моих пользователей предоставляя им различный функционал\n\n' \
           'Админ - @olider_db'

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton('Начало')
    keyboard.add(start_button)

    bot.send_message(message.chat.id, mess, reply_markup=keyboard)


@bot.message_handler(commands=['начало', 'start_menu'], func=check_whitelist)
def start_message(message):
    """Команда Начало. Начальное меню бота"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    schedule_button = types.KeyboardButton('Расписание')
    help_button = types.KeyboardButton('Что ты можешь?')
    question_button = types.KeyboardButton('Задать вопрос ChatGPT')

    keyboard.add(schedule_button, question_button, help_button)

    bot.send_message(message.chat.id, 'Приступим к работе', reply_markup=keyboard)


@bot.message_handler(commands=['помощь', 'help'], func=check_whitelist)
def help_message(message):
    """Команда Помощь. Доступные команды"""
    bot.send_message(message.chat.id, f'Вот команды, которые я знаю:\n\n{commands}')


def up_low_week():
    """Определяет, верхняя или нижняя неделя"""
    # Нечетные - верхние, четные нижние
    number_of_week = datetime.datetime.today().isocalendar()[1]
    if number_of_week % 2 == 0:
        return 0  # Четная - нижняя
    else:
        return 1  # Нечетная - верхняя


commands_for_schedules = ['неделя', 'week',
                          'понедельник', 'пн', 'monday',
                          'вторник', 'вт', 'tuesday',
                          'среда', 'ср', 'wednesday',
                          'четверг', 'чт', 'thursday',
                          'пятница', 'пт', 'friday']


@bot.message_handler(commands=commands_for_schedules, func=check_whitelist)
def schedules(message):
    """Расписание на неделю и на все дни по отдельности"""

    if up_low_week():
        week_text = upper_schedule_text
    else:
        week_text = lower_schedule_text

    week = week_text.split('split_element')

    values = {'неделя': "".join(week), 'week': "".join(week),
              'понедельник': week[0], 'пн': week[0], 'monday': week[0],
              'вторник': week[1], 'вт': week[1], 'tuesday': week[1],
              'среда': week[2], 'ср': week[2], 'wednesday': week[2],
              'четверг': week[3], 'чт': week[3], 'thursday': week[3],
              'пятница': week[4], 'пт': week[4], 'friday': week[4]}

    key = message.text[1:].split()[0]
    if key[-len(bot.get_me().username) - 1::] == f'@{bot.get_me().username}':
        key = key[:-len(bot.get_me().username) - 1]

    bot.send_message(message.chat.id, f'Выбранное расписание:\n'
                                      f'{values[key]}')


@bot.message_handler(commands=['фото_расписания', 'фр', 'photo_schedule'], func=check_whitelist)
def photo_schedule(message):
    """Фотка расписания"""
    bot.send_message(message.chat.id, 'Фотка расписания:\n')
    with open('data/schedule.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo=photo)


def reply_ChatGPT(message: telebot):
    """Ответ ChatGPT"""
    messages = []

    user_message = message.text[2:].lstrip()

    if user_message != '':

        messages.append({"role": "user", "content": user_message})

        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

        reply = chat.choices[0].message.content

        answer = f"<b><i>ChatGPT:\n</i></b>{reply}"

    else:
        answer = 'Вы ввели пустую строку :(\nПожалуйста, введите текст для ChatGPT'

    return answer


@bot.message_handler(commands=['?', 'q'], func=check_whitelist)
def question_for_chatgpt(message):
    """Общение с ChatGPT"""
    reply = reply_ChatGPT(message)
    bot.send_message(message.chat.id, reply, parse_mode='html')


@bot.message_handler(commands=['позиция', 'поз', 'position'], func=check_whitelist)
def week_position(message):
    """Верхняя или нижняя неделя"""
    if up_low_week():
        bot.send_message(message.chat.id, 'Сейчас верхняя неделя')
    else:
        bot.send_message(message.chat.id, 'Сейчас нижняя неделя')


@bot.message_handler(commands=['верхняя_неделя', 'вн', 'upper_week'])
def print_upper_week(message):
    """Выводит верхнюю неделю"""
    upper_schedule = ''.join(upper_schedule_text.split('split_element'))
    bot.send_message(message.chat.id, upper_schedule)


@bot.message_handler(commands=['нижняя_неделя', 'нн', 'lower_week'])
def print_lower_week(message):
    """Выводит нижнюю неделю"""
    lower_schedule = ''.join(lower_schedule_text.split('split_element'))
    bot.send_message(message.chat.id, lower_schedule)


@bot.message_handler(commands=['admin'], func=check_admin)
def administration(message):
    """Панель администратора"""
    bot.send_message(message.chat.id, 'Здесь должна быть админская панель')


'''    
    if message.chat.id not in admin_whitelist:
        bot.send_message(message.chat.id, 'А зачем вам эта команды? :)')

    add_whitelist_button = types.KeyboardButton('/add_chatid_to_whitelist')
    remove_whitelist_button = types.KeyboardButton('/remove_chatid_from_whitelist')
    print_whitelist_button = types.KeyboardButton('/print_whitelist')

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(add_whitelist_button, remove_whitelist_button, print_whitelist_button)

    bot.send_message(message.chat.id, 'Действия:', reply_markup=keyboard)


@bot.message_handler(commands=['add_chatid_to_whitelist'], func=check_admin)
def add_chatid_to_whitelist(message):
    """Добавляет id чата в белый список"""
    if message.chat.id in whitelist:
        bot.send_message(message.chat.id, 'id is whitelisted')
    else:
        whitelist[message.chat.id] = bot.get_chat(message.chat.id).title
        bot.send_message(message.chat.id, 'id is added')


@bot.message_handler(commands=['remove_chatid_from_whitelist'], func=check_admin)
def remove_chatid_from_whitelist(message):
    """Удаляет id чата из белого списка"""
    if message.chat.id in whitelist:
        del whitelist[message.chat.id]
        bot.send_message(message.chat.id, 'id is removed')
    else:
        bot.send_message(message.chat.id, "id isn't whitelisted")


@bot.message_handler(commands=['print_whitelist'], func=check_admin)
def print_whitelist(message):
    """Выводит whitelist"""
    bot.send_message(message.chat.id, str(whitelist))
'''


@bot.message_handler(content_types=['text'], func=check_whitelist)
def handler_message(message):
    """Обработчик сообщений"""

    if message.text == 'Начало':

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        schedule_button = types.KeyboardButton('Расписание')
        help_button = types.KeyboardButton('Что ты можешь?')
        question_button = types.KeyboardButton('Задать вопрос ChatGPT')

        keyboard.add(schedule_button, question_button, help_button)

        bot.send_message(message.chat.id, 'Приступим к работе', reply_markup=keyboard)

    elif message.text == 'Что ты можешь?':
        bot.send_message(message.chat.id, f'Вот команды, которые я знаю:\n\n{commands}')

    elif message.text == 'Расписание':

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        monday = types.InlineKeyboardButton('Понедельник', callback_data='monday')
        tuesday = types.InlineKeyboardButton('Вторник', callback_data='tuesday')
        wednesday = types.InlineKeyboardButton('Среда', callback_data='wednesday')
        thursday = types.InlineKeyboardButton('Четверг', callback_data='thursday')
        friday = types.InlineKeyboardButton('Пятница', callback_data='friday')
        week = types.InlineKeyboardButton('Вся неделя', callback_data='week')
        upper_week_button = types.InlineKeyboardButton('Верхняя неделя', callback_data='upper_week')
        lowe_week_button = types.InlineKeyboardButton('Нижняя неделя', callback_data='lower_week')
        photo_schedule = types.InlineKeyboardButton('Фотка расписания', callback_data='photo_schedule')
        week_position = types.InlineKeyboardButton('Какая сейчас неделя?', callback_data='week_position')

        keyboard.add(monday, tuesday, wednesday, thursday, friday, week,
                     upper_week_button, lowe_week_button, photo_schedule, week_position)

        bot.send_message(message.chat.id, 'Выберите расписание:', reply_markup=keyboard)

    elif message.text == 'Задать вопрос ChatGPT':
        bot.send_message(message.chat.id, 'Чтобы написать вопрос ChatGPT напишите "/?" и свой вопрос\n')

    elif message.text[:2] == '??':  # почему-то эта штука работает ток в лс, я хз че делать в группе
        reply = reply_ChatGPT(message)
        bot.send_message(message.chat.id, reply, parse_mode='html')

    else:
        bot.send_message(message.chat.id, 'Неизвестная команда :(')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Обработка нажатия кнопок inline клавиатуры"""
    try:
        if call.message:

            if up_low_week():
                week_text = upper_schedule_text
            else:
                week_text = lower_schedule_text

            week = week_text.split('split_element')
            monday = week[0][14:]
            tuesday = week[1][10:]
            wednesday = week[2][7:]
            thursday = week[3][9:]
            friday = week[4][9:]

            if call.data == 'monday':
                bot.send_message(call.message.chat.id, 'Расписание на понедельник:\n'
                                                       f'{monday}')
            elif call.data == 'tuesday':
                bot.send_message(call.message.chat.id, 'Расписание на вторник:\n'
                                                       f'{tuesday}')
            if call.data == 'wednesday':
                bot.send_message(call.message.chat.id, 'Расписание на среду:\n'
                                                       f'{wednesday}')
            elif call.data == 'thursday':
                bot.send_message(call.message.chat.id, 'Расписание на четверг:\n'
                                                       f'{thursday}')
            elif call.data == 'friday':
                bot.send_message(call.message.chat.id, 'Расписание на пятницу:\n'
                                                       f'{friday}')
            elif call.data == 'week':
                bot.send_message(call.message.chat.id, 'Расписание на всю неделю:\n'
                                                       f'{"".join(week)}')
            elif call.data == 'photo_schedule':
                bot.send_message(call.message.chat.id, 'Фотка расписания:\n')
                with open('data/schedule.jpg', 'rb') as photo:
                    bot.send_photo(call.message.chat.id, photo=photo)
            elif call.data == 'week_position':
                if up_low_week():
                    bot.send_message(call.message.chat.id, 'Сейчас верхняя неделя')
                else:
                    bot.send_message(call.message.chat.id, 'Сейчас нижняя неделя')
            elif call.data == 'upper_week':
                upper_schedule = ''.join(upper_schedule_text.split('split_element'))
                bot.send_message(call.message.chat.id, upper_schedule)
            elif call.data == 'lower_week':
                lower_schedule = ''.join(lower_schedule_text.split('split_element'))
                bot.send_message(call.message.chat.id, lower_schedule)

    except Exception as e:
        print(repr(e))


BotCommands = [
    types.BotCommand('start', 'Запуск бота'),
    types.BotCommand('start_menu', 'Открывает начальное меню'),
    types.BotCommand('week', 'Выводит расписание на неделю'),
    types.BotCommand('monday', 'Выводит расписание на понедельник'),
    types.BotCommand('tuesday', 'Выводит расписание на вторник'),
    types.BotCommand('wednesday', 'Выводит расписание на среду'),
    types.BotCommand('thursday', 'Выводит расписание на четверг'),
    types.BotCommand('friday', 'Выводит расписание на пятницу'),
    types.BotCommand('photo_schedule', 'Выводит фотку расписания'),
    types.BotCommand('position', 'Определяет, верхняя или нижняя неделя'),
    types.BotCommand('upper_week', 'Выводит верхнюю неделю'),
    types.BotCommand('lower_week', 'Выводит нижнюю неделю'),
    types.BotCommand('q', 'Позволяет написать сообщение ChatGPT боту и получить на него ответ')
]
bot.set_my_commands(BotCommands)


bot.polling(none_stop=True)
