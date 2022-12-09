from pyrogram import Client, filters
import configparser
import os

conf = configparser.ConfigParser()
conf.read('conf.ini')
app = Client(**conf['TELEGRAM'])


@app.on_message(filters.text)
def main(client, msg):
    pass




if __name__ == '__main__':
    app.run()