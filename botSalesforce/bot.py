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
https://documentation.botcity.dev/tutorials/python-automations/web/
"""


# Import for the Web Bot
from botcity.web import WebBot, Browser, By

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *
from dotenv import load_dotenv
from integrator import GPT
import os

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False
maestro = BotMaestroSDK.from_sys_args()
execution = maestro.get_execution()

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    ## Fetch the BotExecution with details from the task, including parameters

    load_dotenv()
    login = os.environ.get('LOGIN')
    key = os.environ.get('KEY')
    server = os.environ.get('SERVER')

    maestro.login(
    server=server, 
    login=login, 
    key=key)

    execution.task_id = 7227581

    maestro.alert(
        task_id=execution.task_id,
        title="SalesBot - Alerta de Início",
        message="[INICIADO] Bot para extração de informações do Salesforce",
        alert_type=AlertType.INFO
    )

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    # Carregando as informações do ambiente
    url = maestro.get_credential(label="salesforce", key="url")
    username = maestro.get_credential(label="salesforce", key="username")
    password = maestro.get_credential(label="salesforce", key="password")
    key = maestro.get_credential(label="salesforce", key="key")

    bot = WebBot()
    gpt = GPT(key)

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.FIREFOX

    # Uncomment to set the WebDriver path
    bot.driver_path = bot.get_resource_abspath("geckodriver.exe")

    # Opens the BotCity website.
    bot.browse(url)

    login_salesforce(bot, username, password)

    # Extraindo informações:

    tabela_casos =  bot.find_element(".slds-table > tbody:nth-child(3)",By.CSS_SELECTOR)

    casos = tabela_casos.find_elements(By.TAG_NAME,"tr")
    processados = 0
    erros = 0
    
    for caso in casos:
        try:
            identificador = caso.find_element(By.TAG_NAME, "th").text
            requisitante = caso.find_elements(By.TAG_NAME,"td")[2].text
            titulo = caso.find_elements(By.TAG_NAME,"td")[3].text
            print(f"Identificador: {identificador} - Requisitante: {requisitante} - Título: {titulo}")

            mensagem = f"Com base nas áreas da empresa, me diga, de forma simples  e direta qual é a área que deve tratar o caso: {titulo}"
            resposta = gpt.get_gpt_answer(mensagem)
            print(resposta)
            area_responsavel = resposta['message']

            #Adiciona entrada no log
            maestro.new_log_entry(
                activity_label="registros-salesforce",
                values={
                    "id_caso": identificador,
                    "status": "Informações coletadas com Sucessso"
                }
            )

            #Registra no Datapool
            new_item = DataPoolEntry(
            values={
                    "identificador": identificador,
                    "titulo": titulo,
                    "categoria": area_responsavel
                }
            )

            # Obtendo a referência do Datapool
            datapool = maestro.get_datapool(label="contatos-processados")

            # Adicionando um novo item
            datapool.create_entry(new_item)

            processados += 1

        except Exception as error:
            mensagem = f"Erro ao extrair informações do caso: {error}"
            maestro.error(task_id=execution.task_id, exception=mensagem, screenshot="error.png")
            maestro.new_log_entry(
                activity_label="registros-salesforce",
                values={
                    "id_caso": identificador,
                    "status": "ERRO - Não foi possível extrair informações. Verifique o registro de Erros"
                }
            )
            erros += 1

    total = processados + erros

    # Wait 3 seconds before closing
    bot.wait(3000)

    # Finish and clean up the Web Browser
    # You MUST invoke the stop_browser to avoid
    # leaving instances of the webdriver open
    bot.stop_browser()

    if erros == 0:

        maestro.alert(
            task_id=execution.task_id,
            title="SalesBot [FINALIZADO COM SUCESSO]",
            message="O bot foi finalizado com sucesso.",
            alert_type=AlertType.INFO
        )
    
        # Uncomment to mark this task as finished on BotMaestro
        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message="Bot Finalizado OK.",
            total_items=total,
            processed_items=processados,
            failed_items=erros
        )

    elif processados == 0:
        emails = ["giulia.real@botcity.dev"]
        users=[]
        subject = "SalesBot - Finalizado com Erros"
        body = f"O bot foi finalizado com {erros} erros. Verifique o log e erros gerados para mais informações."
        maestro.message(emails, users, subject, body, MessageType.TEXT)

        maestro.alert(
            task_id=execution.task_id,
            title="SalesBot [FINALIZADO COM ERROS]",
            message="O bot foi finalizado com {erros}.",
            alert_type=AlertType.ERROR
            
        )

        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.FAILED,
            message="Bot Finalizado com Erros.",
            total_items=total,
            processed_items=processados,
            failed_items=erros
        )

    else:
        maestro.alert(
            task_id=execution.task_id,
            title="SalesBot [FINALIZADO PARCIALMENTE COM SUCESSO]",
            message="O bot foi finalizado com {erros} itens com erro e {processados} itens processados com sucesso.",
            alert_type=AlertType.INFO
        )

        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.PARTIALLY_COMPLETED,
            message="Bot Finalizado OK.",
            total_items=total,
            processed_items=processados,
            failed_items=erros
        )
    

def not_found(label):
    print(f"Element not found: {label}")


def login_salesforce(bot, username, password):
    try:
    
        login_field = bot.find_element("#username", By.CSS_SELECTOR)
        login_field.send_keys(username)

        password_field = bot.find_element("#password", By.CSS_SELECTOR)
        password_field.send_keys(password)

        login_button = bot.find_element("#Login", By.CSS_SELECTOR)
        login_button.click()
        bot.wait(3000)

    except Exception as error:
        maestro.error(task_id=execution.task_id, exception=error)



if __name__ == '__main__':
    main()
