import tgbot
# import vkbot
import pairs

if __name__ == "__main__":
    # Connect to DB
    # Start VK & TG bots
    database = pairs.PSDB(fname="pairs.db")
    tgbot.tgbot_start(database)