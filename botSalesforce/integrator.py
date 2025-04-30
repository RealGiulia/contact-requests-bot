from openai import OpenAI
import re


class GPT:

    def __init__(self, key: str):
        self.client = OpenAI(api_key=key)


    def get_gpt_answer(self, message: str) -> dict:
        """Method to send question for GPT and get its answer.
            Params:
                message(str): Message to send for GPT
            Return:
                response(dict): Dictionary containing the status of the request and the content
                                of the message returned from GPT. """

        try:
            description = """A empresa é composta por 4 áreas, das quais:
                                O financeiro é responsável por todas as questões envolvendo reembolso, emissão de documentos fiscais e negociação de preços.
                                A área de Logística é responsável por cuidar de todas as questões envolvendo atraso de pedidos, pedidos enviados erroneamente e devolução de pedidos com avarias. 
                                A área jurídica é responsável por lidar com todas as questões envolvendo renovação de contratos, criação de contratos para novos negócios feitos pela empresa e emissão de contratos para serviços.
                                A área de Product Care é responsável por lidar com toda a assistência técnica solicitada por usuários. Seja sobre defeitos nos eletrõnicos, problemas de software de dispositivos e afins."""
            
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Voc~e é um assitente muito prestativo."},
                    {
                        "role": "user",
                        "content": f"Olá chat, por favor: a Empresa electrohub é uma empresa de eletronicos. {description}. {message}. Escreva a área entre dois asteriscos, por favor"
                    }
                ]
            )

            pattern = r'\*\*(.*?)\*\*'
            message =  completion.choices[0].message.content
            matches = re.findall(pattern, message)
            response = {"status": "OK", "message": matches[0]}

        except Exception as error: 
            print(error)
            response =  {"status": "FAILED", "message": f"Could not get response from GPT API. Error -->> {error}"}

        finally:
            return response
