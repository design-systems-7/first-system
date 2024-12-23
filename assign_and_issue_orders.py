import random
import threading
import requests
import uuid
import time


executor_ids = [
    '27232c32-e007-4d42-bc51-e03bc7f18601',
    'fe281ddb-5d58-49f1-9011-548c3a5aae17',
    '8398aa41-d383-4994-9a5a-fb16625c813c',
    '60c82c8e-bbf1-4fee-a035-a4b31ab5a70d'
]
locale = 'ru'


def assign_order(executer_id, sleep_time):
    while True:
        # Генерация случайных UUID для order_id и executer_id
        order_id = str(uuid.uuid4())

        # URL для назначения заказа
        url = f"http://127.0.0.1:8000/api/v1/assign_order?order_id={order_id}&executer_id={executer_id}&locale=ru"
        headers = {"accept": "application/json"}

        try:
            # Отправка POST-запроса
            response = requests.post(url, headers=headers, data={})
            assigned_order_id = response.json()['assigned_order_id']
            print(f"[ASSIGN] Response: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"[ASSIGN] Error: {e}")
            return

        if random.randint(1, 10) >= 3:
            # URL для отмены заказа
            url = f"http://127.0.0.1:8000/api/v1/cancel_order?assigned_order_id={assigned_order_id}"
            headers = {"accept": "application/json"}

            try:
                # Отправка POST-запроса
                response = requests.post(url, headers=headers, data={})
                print(f"[CANCEL] Response: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"[CANCEL] Error: {e}")
                return

        # Задержка для уменьшения нагрузки
        time.sleep(sleep_time)


def issue_order(executer_id, sleep_time):
    # URL для получения заказа
    url = f"http://127.0.0.1:8001/api/v1/issue_order/issue_order?executer_id={executer_id}"
    headers = {"accept": "application/json"}

    while True:
        try:
            # Отправка POST-запроса
            response = requests.post(url, headers=headers, data={})
            new_order_id = response.json()['assign_order_id']
            print(f"[ISSUE] Response: {response.status_code}, {response.text}")
            # ждем первого заказа
            break
        except Exception as e:
            print(f"[ISSUE Startup] Error: {e}")

    while True:
        time.sleep(sleep_time)

        # URL для получения заказа
        url = f"http://127.0.0.1:8001/api/v1/issue_order/issue_order?executer_id={executer_id}&last_taken_order_id={new_order_id}"
        headers = {"accept": "application/json"}

        try:
            # Отправка POST-запроса
            response = requests.post(url, headers=headers, data={})
            if 'assign_order_id' in response:
                new_order_id = response.json()['assign_order_id']
            print(f"[ISSUE] Response: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"[ISSUE] Error: {e}")
            return


# Создание потоков
if __name__ == "__main__":
    # Очень быстрый исполнитель, все делает
    assign_thread_1 = threading.Thread(target=assign_order, args=(executor_ids[0], 5))
    issue_thread_1 = threading.Thread(target=issue_order, args=(executor_ids[0], 1))

    # Исполнитель не успевает
    assign_thread_2 = threading.Thread(target=assign_order, args=(executor_ids[1], 8))
    issue_thread_2 = threading.Thread(target=issue_order, args=(executor_ids[1], 9))

    # Просто успевающий исполнитель
    assign_thread_3 = threading.Thread(target=assign_order, args=(executor_ids[2], 10))
    issue_thread_3 = threading.Thread(target=issue_order, args=(executor_ids[2], 9))

    # Почти нет заказов
    assign_thread_4 = threading.Thread(target=assign_order, args=(executor_ids[3], 100))
    issue_thread_4 = threading.Thread(target=issue_order, args=(executor_ids[3], 10))

    assign_threads = [assign_thread_1, assign_thread_2, assign_thread_3, assign_thread_4]
    issue_threads = [issue_thread_1, issue_thread_2, issue_thread_3, issue_thread_4]

    # Запуск потоков
    for thread in assign_threads:
        thread.start()

    # Запуск потоков
    for thread in issue_threads:
        thread.start()
