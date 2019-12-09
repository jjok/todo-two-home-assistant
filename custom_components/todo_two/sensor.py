
from homeassistant.helpers.entity import Entity


def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([new TaskCountSensor()])


class TaskCountSensor(Entity):
    """Keeps track of the number of tasks that need to be done."""

    def __init__(self):
        self._count = 0

    def name(self):
        return 'task_count'

    def state(self):
        return self._count

    def update(self):
        self._count = 0
