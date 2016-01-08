from pyrcb import IRCBot
import redis
import parse

import config

class InfoBot(IRCBot):
    def __init__(self, *args, **kwargs):
        self.r = redis.StrictRedis(host=config.REDIS_HOST,
                                   port=config.REDIS_PORT,
                                   db=config.REDIS_DB,
                                   password=config.REDIS_PASS)

        super().__init__(*args, **kwargs)

    def add_info(self, nick, channel, reply_to, info):
        #Send server a whois to check that a user is authenticated with NickServ
        self.send_raw("whois " + nickname)

        if info: # aka, info != ""
            self.send(reply_to, "Set info: " + info)
            self.r.set(nickname.lower(), info)
        else:
            self.send(reply_to, "Usage: '.add some info about yourself here'")
    
    def get_info(self, nick, channel, reply_to, name):
        if name: #aka, name != ""
            info = self.r.get(name.lower())
            if info is None:
                self.send(reply_to, "No info found for " + name + ".")
                return
            self.send(reply_to, name + ": " + info.decode('utf-8'))
        else:
            self.send(reply_to, "Usage: '.info username'")

    def on_message(self, message, nickname, channel, is_query):

        #Checks if message was from a PM or channel
        if is_query:
            reply_to = nickname
        else:
            reply_to = channel
        commands = [
                    (parse.compile(".add {info}"), self.add_info), 
                    (parse.compile(".info {name}"), self.get_info)
                   ]
        for parser, func in commands:
            attempt = parser.parse(message)
            if attempt != None:
                return func(nickname, channel, reply_to, **attempt.named)

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
