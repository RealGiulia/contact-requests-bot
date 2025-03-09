"""
WARNING:

Please make sure you install the bot dependencies with `pip install --upgrade -r requirements.txt`
in order to get all the dependencies on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the dependencies.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at
https://documentation.botcity.dev/tutorials/python-automations/desktop/
"""

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *

import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    # load_dotenv()
    # login = os.environ.get('LOGIN')
    # key = os.environ.get('KEY')
    # server = os.environ.get('SERVER')

    # maestro.login(
    # server=server, 
    # login=login, 
    # key=key)

    # execution.task_id = 7227581

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    # Consumindo itens do Datapool
    datapool = maestro.get_datapool(label="teste-processados")
    
    casos = []
    while datapool.has_next():
        # Buscar o próximo item do Datapool
        item = datapool.next(task_id=execution.task_id)
        if item is None:
            # O item pode ser None se outro processo o consumiu antes
            break
        
        caso = item['identificador']
        area = item['categoria']
        caso_info = {'ID': caso, 'Business Unit': area}
        casos.append(caso_info)

        # Finalizando como 'DONE' após processamento
        item.report_done()
    
    data = datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    pd.DataFrame(casos).to_csv(f'casos-{data}.csv', index=False)
    file = f'casos-{data}.csv'

    maestro.post_artifact(
        task_id=execution.task_id,
        artifact_name=f'relatorio-casos-{data}',
        filepath=file)



    # Implement here your logic...
    ...

    # Uncomment to mark this task as finished on BotMaestro
    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task Finished OK.",
        total_items=0,
        processed_items=0,
        failed_items=0
    )

def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()