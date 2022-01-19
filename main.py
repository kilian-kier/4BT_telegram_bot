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
# chat_id = 1236246295
last_update = ''


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


def get_absence(s_class, check_last_update = True):
    global last_update
    ret = []
    site = requests.get('https://www.fallmerayer.it/screen/parseToJson.php', headers=headers).content
    page = json.loads(site)
    date = page['updateDate']
    if date == last_update and check_last_update:
        return ret
    else:
        last_update = date
        content = page['supplenzen']
        for i in content:
            for j in i['supplenzen']:
                for k in j['uebernahmen']:
                    if k['classroom'] == s_class:
                        ret.append({'str': find_weekday(i['day']) + ' ' + i['day'] + ' : ' + k['hour'] + ". Stunde - " + k[
                            'teacher'] + ' stott ' + j['missingTeacher'], 'date': datetime.datetime.strptime(i['day'] + k['hour'], '%d.%m.%Y%H')})
    return ret


def check_absence():
    global send
    while True:
        now = datetime.datetime.now()
        for s in send:
            if now.date() > s['date'].date():
                send.remove(s)
            elif now.date() == s['date'].date():
                bot.send_message(chat_id, s['str'])
                send.remove(s)

        ret = get_absence(klasse)
        for absence in ret:
            if absence['date'] > now:
                found = False
                for s in send:
                    if s['date'] == absence['date']:
                        found = True
                if not found:
                    bot.send_message(chat_id, absence['str'])
                    send.append(absence)
        time.sleep(3600)


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


@bot.route("/supplenz ?(.*)")
@bot.route("/spulenz ?(.*)")
def start(message, cmd: str):
    global klasse
    responseID = message['chat']['id']
    if cmd == '':
        ret = get_absence(klasse)
    else:
        cmd = cmd.upper()
        ret = get_absence(cmd, False)
    if ret != []:
        for absence in ret:
            bot.send_message(responseID, absence['str'])
    else:
        bot.send_message(responseID, 'Koane Supplenz')


if __name__ == '__main__':
    bot.config["api_key"] = token
    _thread.start_new_thread(check_absence, ())
    bot.poll(debug=True)
