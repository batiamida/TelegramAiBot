from pyrogram import Client
import configparser
import psycopg2 as pg
import os
from config_creation import create_config


def my_filter(message):
    if message is None:
        return None
    elif message.startswith('https') or message.startswith('http'):
        return None
    else:
        return message


async def main(lines, conn, cur):
    conn.autocommit = True
    async with app:
        for channel in lines:
            ch, l = channel.strip().split()
            async for msg in app.get_chat_history(ch, limit=int(l)):
                msg = my_filter(msg.text)
                if msg is not None:
                    cur.execute("INSERT INTO dataset(parsed_text, propaganda) VALUES"
                                f"('{msg}', NULL)")

    conn.close()




if __name__ == "__main__":
    if 'conf.ini' not in os.listdir():
        create_config()

    conf = configparser.ConfigParser()
    conf.read('conf.ini')
    conn = pg.connect(**conf['DATABASE'])
    cur = conn.cursor()
    app = Client(**conf['TELEGRAM'])

    with open('channeles.txt', encoding='UTF-8') as f:
        app.run(main(f.readlines(), conn, cur))

