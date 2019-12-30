
from homeassistant.helpers.entity import Entity

from .todo_two import tasks_that_need_to_be_done

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([TaskCountSensor()])


class TaskCountSensor(Entity):
    """Keeps track of the number of tasks that need to be done."""

    def __init__(self) -> None:
        self._count = 0

    @property
    def name(self) -> str:
        return 'task_count'

    @property
    def state(self) -> int:
        return self._count

    def update(self) -> None:
        self._count = len(tasks_that_need_to_be_done())
