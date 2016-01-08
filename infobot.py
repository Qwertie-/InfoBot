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

    def add_info(self, nickname, channel, reply_to, info):
        #Send server a whois to check that a user is authenticated with NickServ
        self.send_raw("whois " + nickname)
        self.send(reply_to, "Set info: " + info)
        self.r.set(nickname.lower(), info)
    
    def get_info(self, nickname, channel, reply_to, name_raw):
        name = name_raw.strip()
        info = self.r.get(name.lower())
        if info is None:
            self.send(reply_to, "No info found for " + name + ".")
            return
        self.send(reply_to, name + ": " + info.decode('utf-8'))

    def prompt(input_form, output_form):
        def output_func(nick, chan, reply_to, **args):
            self.send(reply_to, str.format(output_form, **args)) 
       	return (parse.compile(input_form), output_func)

    def on_message(self, message, nickname, channel, is_query):

        #Checks if message was from a PM or channel
        if is_query:
            reply_to = nickname
        else:
            reply_to = channel
        commands = [
                    (parse.compile(".add {info}"), self.add_info), 
                    (parse.compile(".info {name_raw}"), self.get_info),
                    prompt(".add", "Usage: '.add some info about yourself here'"),
                    prompt(".info", "Usage: '.info username'")
                   ]
        for parser, func in commands:
            attempt = parser.parse(message.strip()) #stripping the message here
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
