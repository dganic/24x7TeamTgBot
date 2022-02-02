from aiogram.dispatcher.filters.state import State, StatesGroup


class CurrentIncidents(StatesGroup):
    state_current_inc = State()


class CurrentTasks(StatesGroup):
    state_current_tas = State()


class IncidentsBotState(StatesGroup):
    data = State()


class IncidentsUserState(StatesGroup):
    data = State()
