
import requests

#from requests.exceptions import HTTPError


#LOGGER = logging.getLogger(__name__)

API = 'http://localhost:8000'

def get_all_users():
    response = requests.get(url=f'{API}/users')
    json = response.json()
    return json['data']

def tasks_that_need_to_be_done():
    tasks = get_all_tasks()
    return list(filter(not_low_priority, tasks))

def get_all_tasks():
    response = requests.get(url=f'{API}/tasks')
    json = response.json()
    return json['data']

def not_low_priority(task):
    return task['currentPriority'] != 'low'

#def complete_task(taskId, userId):
#    LOGGER.info(f'Completing Task: taskId={taskId}, userId={userId}')
#
#    try:
#        response = requests.post(
#            f'{API}/tasks/{taskId}/complete',
#            json={'user': userId},
#            headers={'Content-Type': 'application/json'}
#        )
#
#        LOGGER.debug(response.headers)
#        LOGGER.debug(response.status_code)
#
#        response.raise_for_status()
#    except HTTPError as http_err:
#        LOGGER.error(f'HTTP error occurred: {http_err}')
#    except Exception as err:
#        LOGGER.error(f'Other error occurred: {err}')
#    else:
#        LOGGER.info('Success!')
