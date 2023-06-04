from discord import app_commands
from states import states

class State:
    def __init__(self, code, name):
        self.code = code
        self.name = name

class StateTransformer(app_commands.Transformer):
    async def transform(self, interaction, value):
        return State(states[value], value)

    async def autocomplete(self, interaction, value: str):
        return [app_commands.Choice(name=k, value=k) for k, v in states.items() if value in k.lower()][:25]
