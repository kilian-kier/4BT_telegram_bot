import functools
import traceback
import types

import pickle
import telebot
import requests
import json
import calendar
import datetime
import _thread
import time

token = "1995503555:AAEcv6ZRJ3nkOsMpfeUhUlLmKBlp07ayE_g"  # Main
# token = "1986718544:AAF1bIPY28zjfP-I2yAwgJ7zeMtnJ6Ooego" # Martin Gamper
headers = {'cookie': 'pass=fallmerayer'}
klasse = "4BT"
send = []
bot = telebot.TeleBot(token)
chat_id = -1001207755479  # Main
# chat_id = 1236246295
# chat_id = -761716183 # Martin Gamper
last_update = ''
debug = False
save_file = "save.txt"

teamlehrer = [("Torggler Michael", "Gostner Günther"), ("Mutschlechner Michael", "Hvala Maximilian")]


def send_message(id, message):
    if (id == None):
        id = chat_id
    message = str(message)
    if (debug == False):
        bot.send_message(id, message)
    elif (debug == True):
        bot.send_message(id, message)
        print(message)


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


def in_teamlehrer(teacher1, teacher2):
    for t1, t2 in teamlehrer:
        if ((t1 == teacher1 and t2 == teacher2) or (t2 == teacher2 and t1 == teacher1)):
            return True
        else:
            pass
    return False


def get_absence(s_class, check_last_update=True):
    global last_update
    ret = []

    success = False

    while (not success):
        try:
            site = requests.get('https://www.fallmerayer.it/screen/parseToJson.php', headers=headers).content
            success = True
        except Exception as ex:
            if hasattr(ex, 'message'):
                print(ex.message)
            else:
                print(ex)
            print("Try Again in 1 Minute")
            time.sleep(2)

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
                        teacher = k['teacher']
                        missingTeacher = j['missingTeacher']
                        if (not in_teamlehrer(teacher, missingTeacher)):
                            ret.append(
                                {'str': find_weekday(i['day']) + ' ' + i['day'] + ' : ' + k[
                                    'hour'] + ". Stunde - " + teacher + ' stott ' + missingTeacher,
                                 'date': datetime.datetime.strptime(i['day'] + k['hour'], '%d.%m.%Y%H')})
    return ret


def store():
    file = open(save_file, "wb")
    temp = dict()
    temp["send"] = send
    temp["last_update"] = last_update
    temp["teams"] = teamlehrer
    pickle.dump(temp, file)
    file.close()


def load():
    try:
        file = open(save_file, "rb")
        global send
        global last_update
        global teamlehrer
        temp = pickle.load(file)
        send = temp["send"]
        last_update = temp["last_update"]
        teamlehrer = temp["teams"]
        file.close()
    except:
        pass


def check_absence():
    global send
    while True:
        now = datetime.datetime.now()

        for s in send:
            if now.date() > s['date'].date():
                send.remove(s)
            elif now.date() == s['date'].date():
                send_message(chat_id, s['str'])
                send.append(s)

        ret = get_absence(klasse)
        for absence in ret:
            if absence['date'] > now:
                found = False
                for s in send:
                    if s['date'] == absence['date']:
                        found = True
                        break
                if not found:
                    send_message(chat_id, absence['str'])
                    send.append(absence)
        store()
        time.sleep(2)


def start(message):
    chat_dest = message['chat']['id']
    msg = "Hoi Servus"
    send_message(chat_dest, msg)


def change_class(message, cmd: str):
    global klasse
    chat_dest = message['chat']['id']
    if chat_dest == chat_id:
        cmd = cmd.upper()
        msg = "i schick donn iatz olbm die Supplenzen von do {}".format(cmd)
        send_message(chat_dest, msg)
        klasse = cmd
        send.clear()


def supplenz(message, cmd: str):
    global klasse
    responseID = message['chat']['id']
    if cmd == '':
        ret = get_absence(klasse)
    else:
        cmd = cmd.upper()
        ret = get_absence(cmd, False)
    if ret != []:
        for absence in ret:
            if (not debug):
                send_message(responseID, absence['str'])
            if (debug):
                send_message(responseID, absence)
    else:
        send_message(responseID, 'Koane Supplenz')


def settings(message, cmd=""):
    global debug
    global send
    global last_update
    responseID = message['chat']['id']
    if (cmd == "" or cmd == None):
        send_message(responseID, "To Few Arguments")
        return

    cmd_arr = cmd.split(" ")
    cmd_arr = [i for i in cmd_arr if i != ""]
    cmd1 = cmd_arr[0]

    cmd2 = ""
    if (len(cmd_arr) >= 2):
        cmd2 = cmd_arr[1]

    if (cmd1 == "var"):
        if (cmd2 != ""):
            try:
                cmd2 = cmd2.replace("\\", "__")
                send_message(responseID, globals()[cmd2])
            except:
                send_message(responseID, "Variable " + cmd2 + " Does Not Exist")
        else:
            allglobals = globals()
            notcallable = [i for i in allglobals if not isinstance(globals()[i], (
                types.FunctionType, types.BuiltinFunctionType, functools.partial))]
            send_message(responseID, "Global Variables")
            send_message(responseID, notcallable)
    elif (cmd1 == "fun"):
        send_message(responseID, "Not Implemented/Probably Too Unsecure")
    elif (cmd1 == "off"):
        send_message(responseID, "Debugging Off")
        debug = False
    elif (cmd1 == "on"):
        send_message(responseID, "Debugging On")
        debug = True
    elif (cmd1 == "clear"):
        send.clear()
        last_update = 0
        send_message(responseID, "Send Cleared")
    elif (cmd1 == "getteams"):
        ret = ""
        for i in teamlehrer:
            ret += i[0] + "\t-\t" + i[1] + "\n"
        send_message(responseID, ret)
    elif (cmd1 == "addteam"):
        if (len(cmd_arr) >= 5):
            teamlehrer.append((cmd_arr[1] + " " + cmd_arr[2], cmd_arr[3] + " " + cmd_arr[4]))
            send_message(responseID, "Team Added")
            store()
        else:
            send_message(responseID, "To Few Arguments")
    elif (cmd1 == "rmteam"):
        if (len(cmd_arr) >= 5):
            try:
                teamlehrer.remove((cmd_arr[1] + " " + cmd_arr[2], cmd_arr[3] + " " + cmd_arr[4]))
                send_message(responseID, "Team Removed")
                store()
            except:
                send_message(responseID, "Team Not Found")
        else:
            send_message(responseID, "To Few Arguments")
    else:
        send_message(responseID, "No Debug Case Found")


def newBot():
    global change_class
    global start
    global supplenz
    global bot
    global settings
    bot = telebot.TeleBot(token)
    bot.config["api_key"] = token
    start = bot.route("/supplenz")(start)
    change_class = bot.route("/class ?(.*)")(change_class)
    supplenz = bot.route("/supplenz ?(.*)")(supplenz)
    supplenz = bot.route("/spulenz ?(.*)")(supplenz)
    settings = ((bot.route("/settings( .*)+"))(settings))


if __name__ == '__main__':
    load()
    _thread.start_new_thread(check_absence, ())
    while (1):
        try:
            newBot()
            bot.poll(debug=True)
        except Exception as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
