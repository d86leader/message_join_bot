#!/usr/bin/env python3

from typing import *

"""
Description: routines with joining messages and keeping track of what to put
where.
"""

# a complex key for our table
UID = NamedTuple("UID", [("chat_id", int)
                        ,("from_id", int)
                        ])
MessageInfo = NamedTuple("MessageInfo",
        [("message_id",   int)
        ,("current_text", str)
        ])
UserCollection = Dict[UID, MessageInfo]


class Action:
    pass
class SendMessage(Action):
    def __init__(self, chat_id : int, text : str) -> None:
        self.chat_id = chat_id
        self.text = text
class EditMessage(Action):
    def __init__(self, chat_id : int
                     , message_id : int
                     , text : str
                ) -> None:
        self.chat_id = chat_id
        self.message_id = message_id
        self.text = text


class Joiner:
    def __init__(self, base_messages : UserCollection = {}) -> None:
        self.bases = base_messages

    def join(self, messages) -> Action:
        message = messages[0]
#         messages.sort(key = lambda x: x.date)
        messages = map(lambda x: x.text, messages)

        chat_id = message.chat.id
        from_id = message.from_user.id
        # throws something when fields not present
        user_id = UID(chat_id=chat_id, from_id=from_id)

        if user_id not in self.bases:
            author = message.from_user.first_name
            if message.from_user.last_name:
                author += " " + message.from_user.last_name

            text = f"{author} says:\n"
            text += "\n".join(messages)

            self.bases[user_id] = MessageInfo(message_id=None
                                             ,current_text=text
                                             )
            return SendMessage(chat_id, text)
        else:
            message_id, text = self.bases[user_id]
            assert message_id is not None

            text += "\n" + "\n".join(messages)
            self.bases[user_id] = (message_id, text)
            return EditMessage(chat_id, message_id, text)


    # cleanup when the first unification message was sent
    def sent_message(self, user_message, bot_message) -> None:
        chat_id = user_message.chat.id
        from_id = user_message.from_user.id
        # throws something when fields not present
        user_id = UID(chat_id=chat_id, from_id=from_id)

        # insert the missing message_id which is used fo editing further
        old_mid, text = self.bases[user_id]
        self.bases[user_id] = MessageInfo(message_id=bot_message.message_id
                                         ,current_text=text
                                         )


    # when user no longer needs joining, cleanup their data from collection
    def cleanup(self, message) -> None:
        chat_id = message.chat.id
        from_id = message.from_user.id
        # throws something when fields not present
        user_id = UID(chat_id=chat_id, from_id=from_id)

        if user_id not in self.bases:
            return

        del self.bases[user_id]
