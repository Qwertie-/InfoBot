from pyrcb import IRCBot
import redis

import config

class InfoBot(IRCBot):
    def __init__(self, *args, **kwargs):
        self.r = redis.StrictRedis(host=config.REDIS_HOST,
                                   port=config.REDIS_PORT,
                                   db=config.REDIS_DB,
                                   password=config.REDIS_PASS)

        super().__init__(*args, **kwargs)

    def on_message(self, message, nickname, channel, is_query):
        command = message.split(" ") #Split the message

        #Checks if message was from a PM or channel
        if is_query:
            reply_to = nickname
        else:
            reply_to = channel

        if command[0] == ".add":
            #Send server a whois to check that a user is authenticated with NickServ
            self.send_raw("whois " + nickname)

            if len(command) >= 2:
                self.send(reply_to, "Set info: " + ' '.join(command[1:]))
                self.r.set(nickname.lower(), ' '.join(command[1:]))
            else:
                self.send(reply_to, "Usage: '.add some info about yourself here'")

        if command[0] == ".info":
            if len(command) >= 2:
                info = self.r.get(command[1].lower())
                if info is None:
                    self.send(reply_to, "No info found for " + command[1] + ".")
                    return
                self.send(reply_to, command[1] + ": " + info.decode('utf-8'))
            else:
                self.send(reply_to, "Usage: '.info username'")

    #TODO: Check for whois from server
    def on_raw(self, nickname, command, args):
        pass


def main():
    bot = InfoBot()
    bot.connect(config.IRC_HOST, config.IRC_PORT)
    bot.register(config.IRC_USER)
    bot.join(config.IRC_CHAN)
    bot.listen()


if __name__ == "__main__":
    main()
