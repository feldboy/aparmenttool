"""
Stub for telegram package to support tests without real network calls.
"""

class Bot:
    def __init__(self, token):
        self.token = token

    async def get_me(self):
        """
        Return a dummy bot info object with basic attributes.
        """
        class BotInfo:
            def __init__(self):
                self.first_name = "TestBot"
                self.username = "testbot"
                self.id = 123456

        return BotInfo()
