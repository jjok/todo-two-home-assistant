
from homeassistant.helpers.entity import Entity

from todo_two import get_all_tasks

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([TaskCountSensor()])


class TaskCountSensor(Entity):
    """Keeps track of the number of tasks that need to be done."""

    def __init__(self):
        self._count = 0

    @property
    def name(self):
        return 'task_count'

    @property
    def state(self):
        return self._count

    def update(self):
        get_all_tasks()
        self._count = 0
