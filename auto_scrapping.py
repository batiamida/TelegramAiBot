from pyrogram import Client
import configparser
import psycopg2 as pg
import os
from config_creation import create_config
import re

def my_filter(message):
    if message is None:
        return None
    elif message.startswith('https') or message.startswith('http'):
        return None
    else:
        return message

def prep_msg(msg):
    # to_replace = ["'", '"', '#']
    # for repl in to_replace:
    #     msg = msg.replace(repl, repl*2, msg)
    msg = msg.replace("'", "''")
    msg = msg.replace('"', '""')
    msg = msg.replace('#', '')
    msg = msg.replace('@', '')
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)
    msg = re.sub(emoj, '', msg)
    # print(msg)
    return msg

async def main(lines, conn, cur):
    conn.autocommit = True
    async with app:
        for channel in lines:
            ch, l, code, propaganda = channel.strip().split()
            propaganda = bool(propaganda)
            # ls = await app.get_chat_history(ch, limit=int(l))
            # print(ls)
            async for msg in app.get_chat_history(ch, limit=int(l)):
                # print(msg)
                msg = my_filter(msg.text)
                non_counter = 0
                try:
                    if msg is not None:
                        msg = prep_msg(msg)
                        cur.execute("INSERT INTO dataset_u_new(parsed_text, propaganda, language_code) VALUES"
                                    f"('{msg}', {propaganda}, '{code}')")
                        # print("insert")
                        # conn.commit()
                    else:
                        non_counter += 1

                except Exception as e:
                    print(e)
                    continue
    conn.close()


if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read('conf.ini')
    conn = pg.connect(**conf['DATABASE'])
    cur = conn.cursor()
    app = Client(**conf['TELEGRAM'])

    with open('auto_channeles.txt', encoding='UTF-8') as f:
        app.run(main(f.readlines(), conn, cur))