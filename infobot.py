from pyrcb import IRCBot


class InfoBot(IRCBot):
    def on_message(self, message, nickname, channel, is_query):
        command = message.split(" ")
        if command[0] == ".set":
            self.send(channel, "Set info:" + str(command[1:]))

        if command[0] == ".enable":
            pass




def main():
    bot = InfoBot()
    bot.connect("host", 6667)
    bot.register("InfoBot")
    bot.join("#channel")
    bot.listen()

if __name__ == "__main__":
    main()
