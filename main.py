import telebot
import requests
import json
import calendar
import datetime
import _thread
import time

token = "1995503555:AAEcv6ZRJ3nkOsMpfeUhUlLmKBlp07ayE_g"
bot = telebot.TeleBot(token)
headers = {'cookie': 'pass=fallmerayer'}
klasse = "4BT"
send = []
chat_id = -1001207755479


def find_weekday(date):
    weekday = calendar.day_name[datetime.datetime.strptime(date, '%d.%m.%Y').weekday()]
    if weekday == 'Monday':
        ret = 'Montag'
    elif weekday == 'Tuesday':
        ret = 'Dienstag'
    elif weekday == 'Wednesday':
        ret = 'Mittwoch'
    elif weekday == 'Thursday':
        ret = 'Donnerstag'
    elif weekday == 'Friday':
        ret = 'Freitag'
    return ret


def get_absence():
    ret = []
    site = requests.get('https://www.fallmerayer.it/screen/parseToJson.php', headers=headers).content
    page = json.loads(site)
    content = page['supplenzen']
    for i in content:
        for j in i['supplenzen']:
            for k in j['uebernahmen']:
                if k['classroom'] == klasse:
                    ret.append(find_weekday(i['day']) + ' ' + i['day'] + ' : ' + k['hour'] + ". Stunde - " + k[
                        'teacher'] + ' stott ' + j['missingTeacher'])
    return ret


def check_absence():
    while True:
        ret = get_absence()
        for absence in ret:
            if absence not in send:
                bot.send_message(chat_id, absence)
                send.append(absence)
        time.sleep(2)


@bot.route("/start")
def start(message):
    chat_dest = message['chat']['id']
    msg = "Hoi Servus"

    bot.send_message(chat_dest, msg)


@bot.route("/class ?(.*)")
def start(message, cmd: str):
    global klasse
    chat_dest = message['chat']['id']
    if chat_dest == chat_id:
        cmd = cmd.upper()
        msg = "i schick donn iatz olbm die Supplenzen von do {}".format(cmd)
        bot.send_message(chat_dest, msg)
        klasse = cmd
        send.clear()


if __name__ == '__main__':
    bot.config["api_key"] = token
    _thread.start_new_thread(check_absence, ())
    bot.poll(debug=True)
