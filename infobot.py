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
        #Send server a whois to check that a user is authenticated with NickServ # Whois not doing anything??
        # self.send_raw("whois " + nickname)
        #Assumes * is not allowed at the start of nicknames
        info_meta = self.r.get("*" + nickname.lower())
        if info_meta != None: info_meta = info_meta.decode("utf-8")
        if info_meta == "frozen":
            if channel in self.nicklist and nickname in self.nicklist[channel] and self.nicklist[channel][nickname].is_op:
                self.r.set(nickname.lower(), info)
                self.send(reply_to, "Set info: " + info)
            else:
                self.send(reply_to, "Only mods can do this.")
        else:
            self.r.set(nickname.lower(), info)
            self.send(reply_to, "Set info: " + info)

    def get_info(self, nickname, channel, reply_to, name_raw):
        name = name_raw.strip()
        if name.startswith("*"):
            self.send(reply_to, "No info found for " + name + ".")
        else:
            info = self.r.get(name.lower())
            if info is None:
                self.send(reply_to, "No info found for " + name + ".")
            else:
                self.send(reply_to, name + ": " + info.decode('utf-8'))

    def delete_info(self, nickname, channel, reply_to, name_raw):
        name = name_raw.strip()
        if channel in self.nicklist and nickname in self.nicklist[channel] and self.nicklist[channel][nickname].is_op:
            self.send(reply_to, "Deleted info for " + name + ".")
            self.r.delete(name.lower()) # does not delete freezing!!
        else:
            self.send(reply_to, "Only mods can do this.")

    def freeze_info(self, nickname, channel, reply_to, name_raw):
        name = name_raw.strip()
        if channel in self.nicklist and nickname in self.nicklist[channel] and self.nicklist[channel][nickname].is_op:
            self.send(reply_to, "Froze info for " + name + ".")
            self.r.set("*" + name.lower(), "frozen")
        else:
            self.send(reply_to, "Only mods can do this.")

    def unfreeze_info(self, nickname, channel, reply_to, name_raw):
        name = name_raw.strip()
        if channel in self.nicklist and nickname in self.nicklist[channel] and self.nicklist[channel][nickname].is_op:
            self.send(reply_to, "Unfroze info for " + name + ".")
            self.r.set("*" + name.lower(), "")
        else:
            self.send(reply_to, "Only mods can do this.")

    def force_info(self, nickname, channel, reply_to, name_raw, info):
        name = name_raw.strip()
        if channel in self.nicklist and nickname in self.nicklist[channel] and self.nicklist[channel][nickname].is_op:
            self.send(reply_to, "Forced info for " + name + ".")
            self.r.set(name.lower(), info)
        else:
            self.send(reply_to, "Only mods can do this.")


    def prompt(self, input_form, output_form):
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
                    (parse.compile(".delete {name_raw}"), self.delete_info),
                    (parse.compile(".freeze {name_raw}"), self.freeze_info),
                    (parse.compile(".unfreeze {name_raw}"), self.unfreeze_info),
                    (parse.compile(".force {name_raw:S} {info}"), self.force_info),
                    self.prompt(".add", "Usage: '.add some info about yourself here'"),
                    self.prompt(".info", "Usage: '.info username'"),
                    self.prompt(".delete", "Mod only command"),
                    self.prompt(".freeze", "Mod only command"),
                    self.prompt(".unfreeze", "Mod only command"),
                    self.prompt(".force", "Mod only command")
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
