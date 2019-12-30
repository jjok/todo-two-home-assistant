"""Integration with Todo Two task application."""

from datetime import datetime
import logging
import random
import requests
import uuid

from requests.exceptions import HTTPError
from homeassistant.util import slugify

from .todo_two import API
from .todo_two import tasks_that_need_to_be_done

DOMAIN = "todo_two"

LOGGER = logging.getLogger(__name__)

#API = 'http://localhost:8000'

class TodoTwo(object):

    def __init__(self, hass, logger):
        self.hass = hass
        self.logger = logger

    def refresh_tasks(self, number_of_tasks: int):
        tasks_to_be_done = tasks_that_need_to_be_done()
        selected_tasks = select_tasks(number_of_tasks, tasks_to_be_done)
        number_of_selected_tasks = len(selected_tasks)

        self.hass.states.set(f'{DOMAIN}.tasks_to_be_done', len(tasks_to_be_done))

        for i in range(0, number_of_tasks):
            if i < number_of_selected_tasks:
                self.hass.states.set(
                    f'{DOMAIN}.task_{i + 1}',
                    selected_tasks[i]['name'],
                    format_task_as_attributes(selected_tasks[i]))
            else:
                self.hass.states.remove(f'{DOMAIN}.task_{i + 1}')

    def complete_selected_task(self, task_index: int):
        self.logger.info(f'Completing stored task {task_index}')
        task_data = self.hass.states.get(f'{DOMAIN}.task_{task_index}')
        current_user = self.hass.states.get(f'{DOMAIN}.current_user')
        self.logger.info(current_user)
        task_id = task_data.attributes['id']
        user_id = current_user.state

        self.hass.services.call(DOMAIN, 'complete', {'taskId': task_id, 'userId': user_id})
        self.hass.services.call(DOMAIN, 'refresh')


    def complete_task(self, taskId: str, userId: str):
        self.logger.info(f'Completing Task: taskId={taskId}, userId={userId}')

        try:
            response = requests.post(
                f'{API}/tasks/{taskId}/complete',
                json={'user':userId},
                headers={'Content-Type': 'application/json'}
            )

    #        self.logger.info(response.headers)
    #        self.logger.info(response.status_code)

            response.raise_for_status()
        except HTTPError as http_err:
            self.logger.info(f'HTTP error occurred: {http_err}')
        except Exception as err:
            self.logger.info(f'Other error occurred: {err}')
        else:
            self.hass.bus.fire(f'{DOMAIN}_task_was_completed', {
                'id': taskId
            })
            self.logger.info('Success!')

    def add_task(self, id, name, priority):
        self.logger.info(f'Adding Task: id={id}, name={name}, priority={priority}')

        try:
            response = requests.put(
                f'{API}/tasks/{id}',
                json={'name':name, 'priority':priority},
                headers={'Content-Type': 'application/json'}
            )

            self.logger.info(response.headers)
            self.logger.info(response.status_code)

            response.raise_for_status()
        except HTTPError as http_err:
            self.logger.info(f'HTTP error occurred: {http_err}')
        except Exception as err:
            self.logger.info(f'Other error occurred: {err}')
        else:
            self.logger.info('Success!')

def setup(hass, config):
    number_of_tasks = config[DOMAIN].get('select', 3)
    #TODO Get this from config somewhere
    hass.states.set(f'{DOMAIN}.current_user', '00e0c19f-f5bc-4718-b368-d157bb3a98c5')

    todo_two = TodoTwo(hass, LOGGER)

    def refresh_tasks(call):
        todo_two.refresh_tasks(number_of_tasks)

    def complete_selected_task(call):
        task_index = int(call.data.get('task'))

        todo_two.complete_selected_task(task_index)

    def complete_task(call):
        task_id = call.data.get('taskId')
        user_id = call.data.get('userId')

        todo_two.complete_task(task_id, user_id)

    def add_task(call):
        id = str(uuid.uuid4())
        name = call.data.get('name')
        priority = call.data.get('priority', 50)

        todo_two.add_task(id, name, priority)

    def update_task(call):
        LOGGER.info(f'Updating task is not yet implemented.')

    hass.services.register(DOMAIN, 'refresh', refresh_tasks)
    hass.services.register(DOMAIN, 'add', add_task)
    hass.services.register(DOMAIN, 'update', update_task)
    hass.services.register(DOMAIN, 'complete', complete_task)
    hass.services.register(DOMAIN, 'complete_selected_task', complete_selected_task)

    hass.services.call(DOMAIN, 'refresh')

    return True

def select_tasks(number_of_tasks_required: int, tasks_that_need_to_be_done):
    number_of_tasks_that_need_to_be_done = len(tasks_that_need_to_be_done)
    top_fifteen = tasks_that_need_to_be_done[0:16]

    if(number_of_tasks_that_need_to_be_done > number_of_tasks_required):
        return random.sample(top_fifteen, number_of_tasks_required)

    return tasks_that_need_to_be_done

def format_task_as_attributes(task):
    name = task['name']
    formatted_date = datetime.utcfromtimestamp(int(task['lastCompletedAt'])).strftime('%Y-%m-%d %H:%M:%S')
    return {
        'friendly_name': name,
        'icon': 'mdi:broom',
        'id': task['id'],
        'last_completed_at': formatted_date,
#        'last_completed_by': task['lastCompletedBy'],
        'current_priority': task['currentPriority']}
