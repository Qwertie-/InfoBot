from pyrcb import IRCBot
import redis

class InfoBot(IRCBot):
    def on_message(self, message, nickname, channel, is_query):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        command = message.split(" ") #Split the message

        #Checks if message was from a PM or channel
        if is_query:
            reply_to = nickname
        else:
            reply_to = channel

        if command[0] == ".add":
            if len(command) >= 2:
                self.send(reply_to, "Set info: " + ' '.join(command[1:]))
                r.set(nickname.lower(), ' '.join(command[1:]))
            else:
                self.send(reply_to, "Usage '.set some info about yourself here'")

        if command[0] == ".info":
            if len(command) >= 2:
                self.send(reply_to, "Info for " + command[1] + ": " + r.get(command[1].lower()).decode('utf-8'))
            else:
                self.send(reply_to, "Usage '.enable username'")

def main():  #TODO: Move config to its own file
    bot = InfoBot()
    bot.connect("host", 6667)
    bot.register("InfoBot")
    bot.join("#channel")
    bot.listen()


if __name__ == "__main__":
    main()
