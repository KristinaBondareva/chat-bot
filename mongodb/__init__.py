class MongodbHelper:

    MAX_MESSAGES_PER_CHAT = 10 - 1

    @staticmethod
    def __get_database():
        from pymongo import MongoClient
        from os import getenv
        from dotenv import load_dotenv
        load_dotenv(override=True)

        CONNECTION_STRING = ("mongodb://" +
                             getenv('DB_USERNAME') + ":" +
                             getenv('DB_PASS') + "@" +
                             getenv('DB_ADDRESS') + ":" +
                             getenv('DB_PORT'))

        client = MongoClient(CONNECTION_STRING)

        return client[getenv('DB_NAME')]

    def initialize_collection_for_chat(self, id):
        import utils

        db = self.__get_database()
        collection_user = db["user_tg_" + str(id) + "_chat"]
        collection_bot = db["bot_tg_" + str(id) + "_chat"]
        collection_user.drop()
        collection_bot.drop()

        message_objects_bot = [
                {"_id": 0,
                 "message": utils.load_string("bot_prompt_message_1")
                 },
                {"_id": 1,
                 "message": utils.load_string("bot_prompt_message_2")
                 },
                {"_id": 2,
                 "message": utils.load_string("bot_prompt_message_3")
                 }]
        collection_bot.insert_many(message_objects_bot)

        message_objects_user = [
                {"_id": 0,
                 "message": utils.load_string("user_prompt_message_1")
                 },
                {"_id": 1,
                 "message": utils.load_string("user_prompt_message_2")
                 }]
        collection_user.insert_many(message_objects_user)

        db.client.close()

        return True

    def insert_message(self, id, message, if_user):
        db = self.__get_database()
        if if_user is True:
            who = "user"
        elif if_user is False:
            who = "bot"
        else:
            raise ValueError("'if_user' must be True (user) or Flase (bot)")

        message = str(message)
        collection_name = db[who + "_tg_" + str(id) + "_chat"]
        latest_message = collection_name.find_one(sort=[('_id', -1)])

        message_object = {
                "_id": None,
                "message": None
                }

        if latest_message is None:
            raise MemoryError("Initialize collection for the chat first")

        elif int(latest_message["_id"]) < self.MAX_MESSAGES_PER_CHAT:
            message_object = {
                "_id": int(latest_message["_id"]) + 1,
                "message": message
                }
            collection_name.insert_one(message_object)

        else:
            all_messages = list(collection_name.find())
            del all_messages[0]
            collection_name.delete_many({})

            for i in all_messages:
                i["_id"] = i["_id"] - 1

            collection_name.insert_many(all_messages)

            message_object = {
                "_id": self.MAX_MESSAGES_PER_CHAT,
                "message": message
                }

            collection_name.insert_one(message_object)

        db.client.close()

        return True

    def get_all_messages_for_chat(self, id):
        db = self.__get_database()
        collection_user = db["user_tg_" + str(id) + "_chat"]
        collection_bot = db["bot_tg_" + str(id) + "_chat"]

        bot_messages = list(collection_bot.find())
        user_messages = list(collection_user.find())

        if bot_messages == [] or user_messages == []:
            raise MemoryError(
                "Chat not initialized, call initialize_collection_for_chat(id) for that id first")
        else:
            bot_messages_list = []
            for i in bot_messages:
                bot_messages_list.append(i["message"])
            user_messages_list = []
            for i in user_messages:
                user_messages_list.append(i["message"])
            db.client.close()
            return(bot_messages_list, user_messages_list)
