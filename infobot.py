from pyrcb import IRCBot
import redis


class InfoBot(IRCBot):
    def on_message(self, message, nickname, channel, is_query):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        command = message.split(" ") #Split the message
        if is_query:
            reply_to = nickname
        else:
            reply_to = channel

        if command[0] == ".set":
            self.send(reply_to, "Set info: " + str(command[1:]))
            r.set(nickname, str(command[1:]))

        if command[0] == ".enable":
            self.send(reply_to, "Info for " + command[1] + str(r.get(command[1])))

def main():
    bot = InfoBot()
    bot.connect("host", 6667)
    bot.register("InfoBot")
    bot.join("#channel")
    bot.listen()


if __name__ == "__main__":
    main()
