from pyrcb import IRCBot
import redis


class InfoBot(IRCBot):
    def on_message(self, message, nickname, channel, is_query):
        command = message.split(" ") #Split the message
        if command[0] == ".set":
            self.send(channel, "Set info: " + str(command[1:]))

        if command[0] == ".enable":
            pass


def main():
    bot = InfoBot()
    bot.connect("host", 6667)
    bot.register("InfoBot")
    bot.join("#channel")
    bot.listen()

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

if __name__ == "__main__":
    main()
