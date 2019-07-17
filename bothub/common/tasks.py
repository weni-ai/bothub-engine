import json

import requests
from celery import shared_task

from bothub.api.v1.serializers import NewRepositoryExampleEntitySerializer
from bothub.common.models import RepositoryExample, Repository


@shared_task
def migrate_repository_wit(repository, auth_token):
    print('dasdasdas')

    # request = requests.get(
    #     url='https://api.wit.ai/export',
    #     headers={
    #         'Authorization': 'Bearer {}'.format(auth_token)
    #     }
    # )

    json_dump = {
    "data": [
        {
            "text": "Bom dia poderia me enviar a segunda via do boleto?",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 43,
                    "end": 49
                },
                {
                    "entity": "servicos",
                    "value": "segunda via",
                    "start": 28,
                    "end": 39
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Compras",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "Financeiro",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "vendas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "Poderia me enviar a segunda via do boleto?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segunda via",
                    "start": 20,
                    "end": 31
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 35,
                    "end": 41
                }
            ]
        },
        {
            "text": "Posi\u00e7\u00e3o Financeira",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "posicaofinanceira",
                    "start": 0,
                    "end": 18
                }
            ]
        },
        {
            "text": "Quero consultar uma parcela",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "consulta",
                    "start": 6,
                    "end": 15
                }
            ]
        },
        {
            "text": "Quero saber a minha posi\u00e7\u00e3o financeira",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "posicaofinanceira",
                    "start": 20,
                    "end": 38
                }
            ]
        },
        {
            "text": "Suporte",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 0,
                    "end": 7
                }
            ]
        },
        {
            "text": "Vendas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "a internet n\u00e3o t\u00e1 funcionando",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 2,
                    "end": 10
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 11,
                    "end": 29
                }
            ]
        },
        {
            "text": "a internet t\u00e1 caindo muito",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 2,
                    "end": 10
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 11,
                    "end": 26
                }
            ]
        },
        {
            "text": "a internet t\u00e1 muito lenta",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 2,
                    "end": 10
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 20,
                    "end": 25
                }
            ]
        },
        {
            "text": "abatimento de minha d\u00edvida",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "abatimento",
                    "start": 0,
                    "end": 10
                }
            ]
        },
        {
            "text": "acessar \u00e1rea do assinante",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "area_assinante",
                    "start": 8,
                    "end": 25
                }
            ]
        },
        {
            "text": "alterar data de vencimento da fatura?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 16,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 30,
                    "end": 36
                }
            ]
        },
        {
            "text": "alterar velocidade do plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 8,
                    "end": 18
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 22,
                    "end": 27
                }
            ]
        },
        {
            "text": "alterar vencimento da fatura",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 0,
                    "end": 7
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 8,
                    "end": 18
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 22,
                    "end": 28
                }
            ]
        },
        {
            "text": "boleto",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 0,
                    "end": 6
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "cancelamento",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 0,
                    "end": 12
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "cancelamento da internet",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 0,
                    "end": 12
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 16,
                    "end": 24
                }
            ]
        },
        {
            "text": "quero cancelar o plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 17,
                    "end": 22
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                }
            ]
        },
        {
            "text": "quero cancelar a internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 17,
                    "end": 25
                }
            ]
        },
        {
            "text": "quero cancelamento de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 18
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 22,
                    "end": 30
                }
            ]
        },
        {
            "text": "cancelar",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 0,
                    "end": 8
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "como cancelar plano?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 5,
                    "end": 13
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 14,
                    "end": 19
                }
            ]
        },
        {
            "text": "como est\u00e1 o meu cr\u00e9dito?",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "credito",
                    "start": 16,
                    "end": 23
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "como eu acesso a p\u00e1gina do assinante?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "como eu fa\u00e7o para alterar a velocidade da internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 28,
                    "end": 38
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 42,
                    "end": 50
                }
            ]
        },
        {
            "text": "como eu fa\u00e7o para mudar a velocidade do plano?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 26,
                    "end": 36
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 40,
                    "end": 45
                }
            ]
        },
        {
            "text": "como eu posso cancelar a internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 14,
                    "end": 22
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 25,
                    "end": 33
                }
            ]
        },
        {
            "text": "como eu posso cancelar?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 14,
                    "end": 22
                }
            ]
        },
        {
            "text": "como fa\u00e7o para voc\u00eas liberarem a internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 33,
                    "end": 41
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 21,
                    "end": 30
                }
            ]
        },
        {
            "text": "paguei a internet, libera ae",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 9,
                    "end": 17
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 19,
                    "end": 25
                }
            ]
        },
        {
            "text": "como pago a internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 12,
                    "end": 20
                }
            ]
        },
        {
            "text": "como posso acessar a \u00e1rea do assinante?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "area_assinante",
                    "start": 21,
                    "end": 38
                }
            ]
        },
        {
            "text": "como posso cancelar a internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 11,
                    "end": 19
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 22,
                    "end": 30
                }
            ]
        },
        {
            "text": "consulta parcela",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "consulta",
                    "start": 0,
                    "end": 8
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "contratar plano na minha casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 25,
                    "end": 29
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                }
            ]
        },
        {
            "text": "dar informa\u00e7\u00f5es t\u00e9cnicas iniciais",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "estou com problemas",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 10,
                    "end": 19
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "estou com problemas de internet em casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 10,
                    "end": 19
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 23,
                    "end": 31
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 35,
                    "end": 39
                }
            ]
        },
        {
            "text": "estou interessado em um apto de voc\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "estou precisando da internet, pf, liberem",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 20,
                    "end": 28
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 34,
                    "end": 41
                }
            ]
        },
        {
            "text": "financeiro",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "gerar 2\u00aa via de conta",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 6,
                    "end": 12
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 16,
                    "end": 21
                }
            ]
        },
        {
            "text": "gerar segunda via de conta",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 6,
                    "end": 17
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 21,
                    "end": 26
                }
            ]
        },
        {
            "text": "gostaria de imprimir a primeira via do boleto",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 39,
                    "end": 45
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 12,
                    "end": 20
                }
            ]
        },
        {
            "text": "imprimir fatura",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 8
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 9,
                    "end": 15
                }
            ]
        },
        {
            "text": "imprimir parcela",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 8
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 9,
                    "end": 16
                }
            ]
        },
        {
            "text": "informar como acessar \u00e1rea do assinante",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "area_assinante",
                    "start": 22,
                    "end": 39
                }
            ]
        },
        {
            "text": "liberar internet",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 0,
                    "end": 6
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 8,
                    "end": 16
                }
            ]
        },
        {
            "text": "liberem a internet pois eu irei pagar o boleto",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 0,
                    "end": 7
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 40,
                    "end": 46
                }
            ]
        },
        {
            "text": "meu cachorro comeu a conta de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 21,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 30,
                    "end": 38
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 4,
                    "end": 18
                }
            ]
        },
        {
            "text": "minha conta de internet ragou",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 15,
                    "end": 23
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 24,
                    "end": 29
                }
            ]
        },
        {
            "text": "negociar parcelas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 9,
                    "end": 16
                },
                {
                    "entity": "servicos",
                    "value": "negociacao",
                    "start": 0,
                    "end": 8
                }
            ]
        },
        {
            "text": "n\u00e3o efetuei o pagamento da fatura",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 27,
                    "end": 33
                }
            ]
        },
        {
            "text": "n\u00e3o recebi a minha fatura",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 19,
                    "end": 25
                }
            ]
        },
        {
            "text": "n\u00e3o uso mais a internet, quero cancelar",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 15,
                    "end": 23
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 31,
                    "end": 39
                }
            ]
        },
        {
            "text": "o fio da internet pocou",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 9,
                    "end": 17
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 18,
                    "end": 23
                }
            ]
        },
        {
            "text": "o roteador quebrou",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 11,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "o roteador queimou. tem como algu\u00e9m de suporte vir aqui em casa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 39,
                    "end": 46
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 59,
                    "end": 63
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 11,
                    "end": 18
                }
            ]
        },
        {
            "text": "ola meu boletos estao atrasados",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 8,
                    "end": 15
                }
            ]
        },
        {
            "text": "ol\u00e1, meu nome \u00e9 Peter, e eu estou precisando da segunda via da internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 48,
                    "end": 59
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 63,
                    "end": 71
                }
            ]
        },
        {
            "text": "onde eu vou para contratar um plano de internete empresa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 17,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 30,
                    "end": 35
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 39,
                    "end": 48
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 49,
                    "end": 56
                }
            ]
        },
        {
            "text": "pagar",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "paguei a conta de internet, voc\u00eas podem liberar?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 9,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 18,
                    "end": 26
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 40,
                    "end": 47
                }
            ]
        },
        {
            "text": "paguei um boleto e quero saber se o mesmo j\u00e1 foi compensado",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 10,
                    "end": 16
                }
            ]
        },
        {
            "text": "paguei uma letra e quero saber se j\u00e1 foi debitada",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "perdi a minha segunda via",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 14,
                    "end": 25
                }
            ]
        },
        {
            "text": "pode mandar algu\u00e9m resolver o problema de internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 30,
                    "end": 38
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 42,
                    "end": 50
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 19,
                    "end": 27
                }
            ]
        },
        {
            "text": "pode mudar a rapidez da internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 24,
                    "end": 32
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 13,
                    "end": 20
                }
            ]
        },
        {
            "text": "posi\u00e7\u00e3o financeira",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "posicaofinanceira",
                    "start": 0,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "posso alterar a velocidade da internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 16,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 30,
                    "end": 38
                }
            ]
        },
        {
            "text": "posso aumentar a internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 17,
                    "end": 25
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 14
                }
            ]
        },
        {
            "text": "posso cancelar a internet no m\u00eas que vem?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 17,
                    "end": 25
                }
            ]
        },
        {
            "text": "posso imprimir 2 via da conta de internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 24,
                    "end": 29
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 33,
                    "end": 41
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 15,
                    "end": 20
                }
            ]
        },
        {
            "text": "posso mudar a data de validade da fatura?",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 22,
                    "end": 30
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 34,
                    "end": 40
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                }
            ]
        },
        {
            "text": "posso mudar de plano?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 15,
                    "end": 20
                }
            ]
        },
        {
            "text": "posso mudar o plano?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 14,
                    "end": 19
                }
            ]
        },
        {
            "text": "preciso de internet para empresas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 11,
                    "end": 19
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 25,
                    "end": 33
                }
            ]
        },
        {
            "text": "preciso de internet para as empresas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 11,
                    "end": 19
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 28,
                    "end": 36
                }
            ]
        },
        {
            "text": "t\u00f4 querendo contratar plano empresarial",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 12,
                    "end": 21
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 22,
                    "end": 27
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 28,
                    "end": 39
                }
            ]
        },
        {
            "text": "preciso de internet para minhas empresas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 11,
                    "end": 19
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 32,
                    "end": 40
                }
            ]
        },
        {
            "text": "preciso de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 11,
                    "end": 19
                }
            ]
        },
        {
            "text": "preciso de internet para comprar ",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 11,
                    "end": 19
                }
            ]
        },
        {
            "text": "preciso de internet na minha casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 11,
                    "end": 19
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 29,
                    "end": 33
                }
            ]
        },
        {
            "text": "quero contratar os servi\u00e7os de internet de vo\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 31,
                    "end": 39
                }
            ]
        },
        {
            "text": "contratar",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "contratar plano",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                }
            ]
        },
        {
            "text": "contrata\u00e7\u00e3o de plano de internet",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 15,
                    "end": 20
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 24,
                    "end": 32
                }
            ]
        },
        {
            "text": "quais os planos e os pre\u00e7os da internet de voc\u00eas, t\u00f4 querendo por aqui em casa",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 9,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 31,
                    "end": 39
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 74,
                    "end": 78
                },
                {
                    "entity": "servicos",
                    "value": "tabela_precos",
                    "start": 21,
                    "end": 27
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quais os pre\u00e7os dos planos para empresa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "tabela_precos",
                    "start": 9,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 20,
                    "end": 26
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 32,
                    "end": 39
                }
            ]
        },
        {
            "text": "quais os pre\u00e7os e planos de voc\u00cas?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "tabela_precos",
                    "start": 9,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 18,
                    "end": 24
                }
            ]
        },
        {
            "text": "quais s\u00e3o os planos de internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 13,
                    "end": 19
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 23,
                    "end": 31
                }
            ]
        },
        {
            "text": "quais s\u00e3o os planos de voc\u00eas?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 13,
                    "end": 19
                }
            ]
        },
        {
            "text": "qual o plano para internet empresarial",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 18,
                    "end": 26
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 27,
                    "end": 38
                }
            ]
        },
        {
            "text": "quanto custa a instala\u00e7\u00e3o aqui em casa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "tabela_precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 15,
                    "end": 25
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 34,
                    "end": 38
                }
            ]
        },
        {
            "text": "quanto custa a instala\u00e7\u00e3o aqui na empresa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "tabela_precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 15,
                    "end": 25
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 34,
                    "end": 41
                }
            ]
        },
        {
            "text": "quanto custa a instala\u00e7\u00e3o na minha casa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "tabela_precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 15,
                    "end": 25
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 35,
                    "end": 39
                }
            ]
        },
        {
            "text": "quais os pre\u00e7os dos planos?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 9,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 20,
                    "end": 26
                }
            ]
        },
        {
            "text": "quanto custa a instala\u00e7\u00e3o?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 15,
                    "end": 25
                }
            ]
        },
        {
            "text": "quanto custa a taxa de instala\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 15,
                    "end": 19
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 23,
                    "end": 33
                }
            ]
        },
        {
            "text": "quanto custa o plano b\u00e1sico?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 15,
                    "end": 20
                }
            ]
        },
        {
            "text": "quanto custa os planos de internet para casa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 16,
                    "end": 22
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 26,
                    "end": 34
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 40,
                    "end": 44
                }
            ]
        },
        {
            "text": "quanto custa para contratar internet aqui em casa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 18,
                    "end": 27
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 28,
                    "end": 36
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 45,
                    "end": 49
                }
            ]
        },
        {
            "text": "quanto custa pra botar net aqui em casa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 35,
                    "end": 39
                }
            ]
        },
        {
            "text": "quanto custo os planos, to afim de contratar",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 16,
                    "end": 22
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 35,
                    "end": 44
                }
            ]
        },
        {
            "text": "quanto pode ser o abatimento da meu d\u00e9bito",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "abatimento",
                    "start": 18,
                    "end": 28
                }
            ]
        },
        {
            "text": "quanto vou pagar pela instala\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 22,
                    "end": 32
                }
            ]
        },
        {
            "text": "quanto \u00e9 para instalar internet aqui?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 23,
                    "end": 31
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 14,
                    "end": 22
                }
            ]
        },
        {
            "text": "quanto \u00e9 pra pagar a instala\u00e7\u00e3o?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 21,
                    "end": 31
                }
            ]
        },
        {
            "text": "quanto \u00e9 pra pagar pela instala\u00e7\u00e3o?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 24,
                    "end": 34
                }
            ]
        },
        {
            "text": "quer contratar plano na minha casa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 5,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 15,
                    "end": 20
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 30,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero abater metade da minha d\u00edvida",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "abatimento",
                    "start": 6,
                    "end": 12
                }
            ]
        },
        {
            "text": "quero acessar a \u00e1rea do assinante da minha empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "area_assinante",
                    "start": 16,
                    "end": 33
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 43,
                    "end": 50
                }
            ]
        },
        {
            "text": "quero alterar a data de vencimento da fatura da empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 38,
                    "end": 44
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 48,
                    "end": 55
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 16,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero alterar a velocidade da internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 16,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 30,
                    "end": 38
                }
            ]
        },
        {
            "text": "quero alterar a velocidade da internet daqui de casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 16,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 30,
                    "end": 38
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 48,
                    "end": 52
                }
            ]
        },
        {
            "text": "quero alterar velocidade da internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 14,
                    "end": 24
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 28,
                    "end": 36
                }
            ]
        },
        {
            "text": "quero anular o plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 12
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 15,
                    "end": 20
                }
            ]
        },
        {
            "text": "quero assinar um plano de internet de voc\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 17,
                    "end": 22
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 26,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero aumentar a velocidade da net",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 17,
                    "end": 27
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 31,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero aumentar a velocidade do plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 17,
                    "end": 27
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 31,
                    "end": 36
                }
            ]
        },
        {
            "text": "quero aumentar minha internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 21,
                    "end": 29
                }
            ]
        },
        {
            "text": "quero cancelar meu pacote de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 29,
                    "end": 37
                }
            ]
        },
        {
            "text": "quero cancelar o meu plano de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 21,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 30,
                    "end": 38
                }
            ]
        },
        {
            "text": "quero cancelar o plano de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 17,
                    "end": 22
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 26,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero cancelar plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 15,
                    "end": 20
                }
            ]
        },
        {
            "text": "quero colocar internet aqui em casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 14,
                    "end": 22
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 31,
                    "end": 35
                }
            ]
        },
        {
            "text": "quero colocar internet em casa?",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 14,
                    "end": 22
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 26,
                    "end": 30
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quero come\u00e7ar um plano de internet na empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 17,
                    "end": 22
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 26,
                    "end": 34
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 38,
                    "end": 45
                }
            ]
        },
        {
            "text": "quero comprar um apto",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quero confirmar se uma parcela foi paga",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 23,
                    "end": 30
                }
            ]
        },
        {
            "text": "quero consultar a area do assinante",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "consulta",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "servicos",
                    "value": "area_assinante",
                    "start": 18,
                    "end": 35
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "quero consultar parcela",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "consulta",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 16,
                    "end": 23
                }
            ]
        },
        {
            "text": "quero contratar um plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 19,
                    "end": 24
                }
            ]
        },
        {
            "text": "quero contratar voc\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 15
                }
            ]
        },
        {
            "text": "quero encerrar o plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 17,
                    "end": 22
                }
            ]
        },
        {
            "text": "quero entrar em uma negocia\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "negociacao",
                    "start": 20,
                    "end": 30
                }
            ]
        },
        {
            "text": "quero fazer um cancelamento",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 15,
                    "end": 27
                }
            ]
        },
        {
            "text": "quero gerar 2 via de boleto da empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 12,
                    "end": 17
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 21,
                    "end": 27
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 31,
                    "end": 38
                }
            ]
        },
        {
            "text": "quero gerar 2 via do boleto",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 12,
                    "end": 17
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 21,
                    "end": 27
                }
            ]
        },
        {
            "text": "quero gerar a segunda via",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 14,
                    "end": 25
                }
            ]
        },
        {
            "text": "quero gerar segunda via da conta",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 12,
                    "end": 23
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 27,
                    "end": 32
                }
            ]
        },
        {
            "text": "quero gerar segunda via da conta de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 12,
                    "end": 23
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 27,
                    "end": 32
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 36,
                    "end": 44
                }
            ]
        },
        {
            "text": "quero gerar segunda via de conta",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 12,
                    "end": 23
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 27,
                    "end": 32
                }
            ]
        },
        {
            "text": "quero gerar segunda via de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 12,
                    "end": 23
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 27,
                    "end": 35
                }
            ]
        },
        {
            "text": "quero imprimir a conta de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 17,
                    "end": 22
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 26,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero imprimir boleto",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 15,
                    "end": 21
                }
            ]
        },
        {
            "text": "quero imprimir boleto da internet de casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 15,
                    "end": 21
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 25,
                    "end": 33
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 37,
                    "end": 41
                }
            ]
        },
        {
            "text": "quero imprimir o boleto da segunda via",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 17,
                    "end": 23
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 27,
                    "end": 38
                }
            ]
        },
        {
            "text": "quero informa\u00e7\u00e3o sobre a \u00e1rea do assinante",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "area_assinante",
                    "start": 25,
                    "end": 42
                }
            ]
        },
        {
            "text": "quero liberar internet por confian\u00e7a",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 14,
                    "end": 22
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 27,
                    "end": 36
                }
            ]
        },
        {
            "text": "quero migrar de plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 12
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 16,
                    "end": 21
                }
            ]
        },
        {
            "text": "quero mudar a data de vencimento da fatura",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 14,
                    "end": 32
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 36,
                    "end": 42
                }
            ]
        },
        {
            "text": "quero mudar a data que vence a fatura",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 31,
                    "end": 37
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 23,
                    "end": 28
                }
            ]
        },
        {
            "text": "quero mudar o vencimento da fatura",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 14,
                    "end": 24
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 28,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero mudar o vencimento do boleto",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 14,
                    "end": 24
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 28,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero negociar",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "negociacao",
                    "start": 6,
                    "end": 14
                }
            ]
        },
        {
            "text": "quero negociar umas parcelas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "negociacao",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 20,
                    "end": 28
                }
            ]
        },
        {
            "text": "quero pagar a conta da empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 14,
                    "end": 19
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 23,
                    "end": 30
                }
            ]
        },
        {
            "text": "quero pagar a conta de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 14,
                    "end": 19
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 23,
                    "end": 31
                }
            ]
        },
        {
            "text": "quero pagar a conta de internet da minha casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 14,
                    "end": 19
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 23,
                    "end": 31
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 41,
                    "end": 45
                }
            ]
        },
        {
            "text": "quero pagar a conta desse m\u00eas, mas meu cachorro comeu a conta",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 14,
                    "end": 19
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 39,
                    "end": 53
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 56,
                    "end": 61
                }
            ]
        },
        {
            "text": "quero pagar a conta, mas a msm ragou",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 14,
                    "end": 19
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 31,
                    "end": 36
                }
            ]
        },
        {
            "text": "quero pagar a insala\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 14,
                    "end": 23
                }
            ]
        },
        {
            "text": "quero pagar a instal\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 14,
                    "end": 23
                }
            ]
        },
        {
            "text": "quero pagar a internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 14,
                    "end": 22
                }
            ]
        },
        {
            "text": "quero pagar a taxa de instala\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 14,
                    "end": 18
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 22,
                    "end": 32
                }
            ]
        },
        {
            "text": "quanto \u00e9 a taxa de instala\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 11,
                    "end": 15
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 19,
                    "end": 29
                }
            ]
        },
        {
            "text": "quero pagar pela instala\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 17,
                    "end": 27
                }
            ]
        },
        {
            "text": "quero por internet aqui em casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 27,
                    "end": 31
                }
            ]
        },
        {
            "text": "quero por internet como pessoa f\u00edsica",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 24,
                    "end": 37
                }
            ]
        },
        {
            "text": "quero por internet na empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 22,
                    "end": 29
                }
            ]
        },
        {
            "text": "quero por internet na minha casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 28,
                    "end": 32
                }
            ]
        },
        {
            "text": "quero por internet no meu cafofo",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 26,
                    "end": 32
                }
            ]
        },
        {
            "text": "quero por internet no meu emprego",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 26,
                    "end": 33
                }
            ]
        },
        {
            "text": "quero por internet no meu lar",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 26,
                    "end": 29
                }
            ]
        },
        {
            "text": "quero por internet no meu trabalho",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 26,
                    "end": 34
                }
            ]
        },
        {
            "text": "quero saber como est\u00e1 o meu d\u00e9bito",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "quero saber os pre\u00e7os dos planos empresariais",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 15,
                    "end": 21
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 26,
                    "end": 32
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 33,
                    "end": 45
                }
            ]
        },
        {
            "text": "quero saber se a minha parcela j\u00e1 foi abatida",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 23,
                    "end": 30
                },
                {
                    "entity": "servicos",
                    "value": "abatimento",
                    "start": 38,
                    "end": 45
                }
            ]
        },
        {
            "text": "quero segunda via da conta de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 6,
                    "end": 17
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 21,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 30,
                    "end": 38
                }
            ]
        },
        {
            "text": "quero solicitar suporte",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 6,
                    "end": 23
                }
            ]
        },
        {
            "text": "quero tirar minha segunda via de boleot",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 18,
                    "end": 29
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 33,
                    "end": 39
                }
            ]
        },
        {
            "text": "quero tratar de parcelas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 16,
                    "end": 24
                }
            ]
        },
        {
            "text": "quero um plano maior",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 9,
                    "end": 14
                }
            ]
        },
        {
            "text": "quero trocar data de vencimento da fatura",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 12
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 35,
                    "end": 41
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 13,
                    "end": 31
                }
            ]
        },
        {
            "text": "quero ver minha situa\u00e7\u00e3o financeira",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "posicaofinanceira",
                    "start": 16,
                    "end": 35
                }
            ]
        },
        {
            "text": "se eu pagar a conta, voc\u00eas liberam a internet em quantos dias?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 14,
                    "end": 19
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 27,
                    "end": 33
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 37,
                    "end": 45
                }
            ]
        },
        {
            "text": "se eu pagar o boleto voc\u00eas liberam a internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 14,
                    "end": 20
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 37,
                    "end": 45
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 27,
                    "end": 34
                }
            ]
        },
        {
            "text": "segunda via",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "segunda via da fatura",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 15,
                    "end": 21
                }
            ]
        },
        {
            "text": "tem como algu\u00e9m vir aqui resolver o problema de internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 25,
                    "end": 33
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 36,
                    "end": 44
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 48,
                    "end": 56
                }
            ]
        },
        {
            "text": "tem como mandar algu\u00e9m consertar a internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 35,
                    "end": 43
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 9,
                    "end": 22
                }
            ]
        },
        {
            "text": "tenho parcelas atrasadas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 6,
                    "end": 14
                }
            ]
        },
        {
            "text": "tenho quantas parcelas em aberta?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 14,
                    "end": 22
                }
            ]
        },
        {
            "text": "t\u00f4 afim de mudar a velocidade da internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 11,
                    "end": 16
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 19,
                    "end": 29
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 33,
                    "end": 41
                }
            ]
        },
        {
            "text": "t\u00f4 precisando contratar um plano empresarial",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 14,
                    "end": 23
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 27,
                    "end": 32
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 33,
                    "end": 44
                }
            ]
        },
        {
            "text": "t\u00f4 querendo negociar minha d\u00edvida",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "negociacao",
                    "start": 12,
                    "end": 20
                }
            ]
        },
        {
            "text": "venham resolver a pexte bulbonica dessa internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 7,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 40,
                    "end": 48
                }
            ]
        },
        {
            "text": "voc\u00eas alteram a data de vencimento da internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 16,
                    "end": 34
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 38,
                    "end": 46
                }
            ]
        },
        {
            "text": "voc\u00eas poderiam por gentileza liberar a internet?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 29,
                    "end": 36
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 39,
                    "end": 47
                }
            ]
        },
        {
            "text": "voc\u00eas trocam a data de vencimento do boleto?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 15,
                    "end": 33
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 37,
                    "end": 43
                }
            ]
        },
        {
            "text": "meu aparelho quebrou",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 13,
                    "end": 20
                }
            ]
        },
        {
            "text": "meu roteador queimou",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 13,
                    "end": 20
                }
            ]
        },
        {
            "text": "meu roteador queimo",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 13,
                    "end": 19
                }
            ]
        },
        {
            "text": "eu quero mudar a data de vencimento da fatura",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 9,
                    "end": 14
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 17,
                    "end": 35
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 39,
                    "end": 45
                }
            ]
        },
        {
            "text": "quero contratar a internet de voc\u00eas",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 18,
                    "end": 26
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "Como posso imprimir a segunda via do boleto?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 11,
                    "end": 19
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 22,
                    "end": 33
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 37,
                    "end": 43
                }
            ]
        },
        {
            "text": "onde fica o escrit\u00f3rio de voc\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "informacao"
                },
                {
                    "entity": "objeto",
                    "value": "escritorio",
                    "start": 12,
                    "end": 22
                }
            ]
        },
        {
            "text": "como encontro algum escrit\u00f3rio de voc\u00eas?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "informacao"
                },
                {
                    "entity": "objeto",
                    "value": "escritorio",
                    "start": 20,
                    "end": 30
                }
            ]
        },
        {
            "text": "qual o bairro do escrit\u00f3rio de voc\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "informacao"
                },
                {
                    "entity": "objeto",
                    "value": "escritorio",
                    "start": 17,
                    "end": 27
                }
            ]
        },
        {
            "text": "qual o n\u00famero de voc\u00eas que eu posso ligar agora?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "informacao"
                }
            ]
        },
        {
            "text": "qual o telefone que eu posso ligar para voc\u00eas?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "informacao"
                },
                {
                    "entity": "objeto",
                    "value": "telefone",
                    "start": 7,
                    "end": 15
                }
            ]
        },
        {
            "text": "quero ligar para voc\u00eas. Qual o n\u00famero de telefone?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "informacao"
                },
                {
                    "entity": "objeto",
                    "value": "telefone",
                    "start": 41,
                    "end": 49
                }
            ]
        },
        {
            "text": "qual o endere\u00e7o dos escrit\u00f3rios?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "informacao"
                },
                {
                    "entity": "objeto",
                    "value": "escritorio",
                    "start": 20,
                    "end": 31
                }
            ]
        },
        {
            "text": "mudar vencimento",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 6,
                    "end": 16
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 0,
                    "end": 5
                }
            ]
        },
        {
            "text": "mudar minnha velocidade de internet",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 0,
                    "end": 5
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 13,
                    "end": 23
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 27,
                    "end": 35
                }
            ]
        },
        {
            "text": "alterar",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 0,
                    "end": 7
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "vencimento",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 0,
                    "end": 10
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Financeiro \ud83d\udcc4",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Vendas \ud83d\udcb0",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "velocidadee",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 0,
                    "end": 10
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "vellocidade",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "vellocida",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 0,
                    "end": 9
                }
            ]
        },
        {
            "text": "vellocidadee",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "quero contratar plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 16,
                    "end": 21
                }
            ]
        },
        {
            "text": "quantos \u00e9 a taxa de instala\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 20,
                    "end": 30
                },
                {
                    "entity": "objeto",
                    "value": "taxa",
                    "start": 12,
                    "end": 16
                }
            ]
        },
        {
            "text": "quanto fica as taxas de instala\u00e7\u00f5es",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "taxa",
                    "start": 15,
                    "end": 19
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 24,
                    "end": 35
                }
            ]
        },
        {
            "text": "instalacao",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 0,
                    "end": 10
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "a internet de voc\u00eas pega aqui no barro duro",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 2,
                    "end": 10
                },
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 20,
                    "end": 29
                }
            ]
        },
        {
            "text": "a cobertura de voc\u00eas chega no jacintinho",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 2,
                    "end": 11
                }
            ]
        },
        {
            "text": "a area de cobertura de voc\u00eas chega aqui",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 10,
                    "end": 19
                }
            ]
        },
        {
            "text": "a cobertura de internet chega aqui no cleto",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 2,
                    "end": 11
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 15,
                    "end": 23
                }
            ]
        },
        {
            "text": "at\u00e9 onde vai a cobertura da start",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 15,
                    "end": 24
                }
            ]
        },
        {
            "text": "vai at\u00e9 onde a internet de voc\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 15,
                    "end": 23
                },
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 0,
                    "end": 7
                }
            ]
        },
        {
            "text": "chega na ponta verde",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "a internet de voc\u00eas chega em macei\u00f3",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 2,
                    "end": 10
                },
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 14,
                    "end": 25
                }
            ]
        },
        {
            "text": "preciso saber se tem internet start no biu",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 21,
                    "end": 29
                }
            ]
        },
        {
            "text": "cobertura em santana?",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "tem internet em marasatu",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 4,
                    "end": 12
                }
            ]
        },
        {
            "text": "tem plano de internet que pegue aqui no vilage",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 4,
                    "end": 9
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 13,
                    "end": 21
                },
                {
                    "entity": "servicos",
                    "value": "cobertura",
                    "start": 26,
                    "end": 37
                }
            ]
        },
        {
            "text": "quero alterar a data de vencimento da fatura",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 16,
                    "end": 34
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 38,
                    "end": 44
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Data de Vencimento",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 0,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "data de vencimento",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 0,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "paguei a minha internet e quero desbloquear",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 15,
                    "end": 23
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 32,
                    "end": 43
                }
            ]
        },
        {
            "text": "quero a segunda via",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 8,
                    "end": 19
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Suporte \ud83d\udee0",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "quero alterar vencimento",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 6,
                    "end": 24
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "quero altera\u00e7\u00e3i",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "altera\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "preciso desbloquear minha net",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 8,
                    "end": 19
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 26,
                    "end": 29
                }
            ]
        },
        {
            "text": "como fa\u00e7o para desbloquear minha net",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 15,
                    "end": 26
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 33,
                    "end": 36
                }
            ]
        },
        {
            "text": "quero liberar internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 6,
                    "end": 13
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 14,
                    "end": 22
                }
            ]
        },
        {
            "text": "Contratar plano pessoal",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 16,
                    "end": 23
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "contratar plano pessoal",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 16,
                    "end": 23
                }
            ]
        },
        {
            "text": "contratar plano corporativo",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 16,
                    "end": 27
                }
            ]
        },
        {
            "text": "contrata\u00e7\u00e3o de planos para corpora\u00e7\u00f5es",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 15,
                    "end": 21
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 27,
                    "end": 38
                }
            ]
        },
        {
            "text": "contratar plano pra minha casa",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 26,
                    "end": 30
                }
            ]
        },
        {
            "text": "contrata\u00e7\u00e3o de plano para minha casa",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 15,
                    "end": 20
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 32,
                    "end": 36
                }
            ]
        },
        {
            "text": "quero contratar plano para minha empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 16,
                    "end": 21
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 33,
                    "end": 40
                }
            ]
        },
        {
            "text": "contratar plano para minha casa",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 27,
                    "end": 31
                }
            ]
        },
        {
            "text": "contratar plano para pessoa f\u00edsica",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 21,
                    "end": 34
                }
            ]
        },
        {
            "text": "contrata\u00e7\u00e3o de internet na minha casa",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 15,
                    "end": 23
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 33,
                    "end": 37
                }
            ]
        },
        {
            "text": "quero por internet em minha casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 28,
                    "end": 32
                }
            ]
        },
        {
            "text": "quero por internet na mnha casa ",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 27,
                    "end": 31
                }
            ]
        },
        {
            "text": "como ponho internet na minha casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 11,
                    "end": 19
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 29,
                    "end": 33
                }
            ]
        },
        {
            "text": "quero pagar internet de voc\u00eas pra por na minha casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 12,
                    "end": 20
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 47,
                    "end": 51
                }
            ]
        },
        {
            "text": "internet na minha casa",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 0,
                    "end": 8
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 18,
                    "end": 22
                }
            ]
        },
        {
            "text": "quero por internet aqui",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 10,
                    "end": 18
                }
            ]
        },
        {
            "text": "contratar plano empresarial",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 10,
                    "end": 15
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 16,
                    "end": 27
                }
            ]
        },
        {
            "text": "quero contratar internet de voc\u00eas aqui na minha empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 15
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 16,
                    "end": 24
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 48,
                    "end": 55
                }
            ]
        },
        {
            "text": "alterar vencimento",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 0,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "ol\u00e1! quero segunda via",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 11,
                    "end": 22
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "segunda via do boleto",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 15,
                    "end": 21
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "alterar velocidade",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 0,
                    "end": 7
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 8,
                    "end": 18
                }
            ]
        },
        {
            "text": "alterar plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 0,
                    "end": 13
                }
            ]
        },
        {
            "text": "alterar venicmento",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alterar venicmento",
                    "start": 0,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "altera\u00e7\u00e3o do plano",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 13,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Plano",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 0,
                    "end": 5
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "\u00e9 o plano que eu quero mudar",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 4,
                    "end": 9
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 23,
                    "end": 28
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "cancelar internet",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 0,
                    "end": 8
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 9,
                    "end": 17
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "como posso acessar a area do assiante",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "area_assinante",
                    "start": 21,
                    "end": 37
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "quanto custa a taxa de instala\u00e7\u00e3o de cabos de rede?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "precos",
                    "start": 7,
                    "end": 12
                },
                {
                    "entity": "objeto",
                    "value": "taxa",
                    "start": 15,
                    "end": 19
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 23,
                    "end": 33
                },
                {
                    "entity": "objeto",
                    "value": "cabo_rede",
                    "start": 37,
                    "end": 50
                }
            ]
        },
        {
            "text": "taxa de instala\u00e7\u00e3o de cabo par tran\u00e7ado",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "taxa",
                    "start": 0,
                    "end": 4
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 8,
                    "end": 18
                },
                {
                    "entity": "objeto",
                    "value": "cabo_rede",
                    "start": 22,
                    "end": 39
                }
            ]
        },
        {
            "text": "taxa de instala\u00e7\u00e3o de fibra \u00f3ptica",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 8,
                    "end": 18
                },
                {
                    "entity": "objeto",
                    "value": "fibra_optica",
                    "start": 22,
                    "end": 34
                }
            ]
        },
        {
            "text": "quanto \u00e9 a taxa de instala\u00e7\u00e3o de fibra \u00f3ptica?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "taxa",
                    "start": 11,
                    "end": 15
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 19,
                    "end": 29
                },
                {
                    "entity": "objeto",
                    "value": "fibra_optica",
                    "start": 33,
                    "end": 45
                }
            ]
        },
        {
            "text": "taxa de instala\u00e7\u00e3o",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 0,
                    "end": 18
                }
            ]
        },
        {
            "text": "quanto \u00e9 a taxa de instala\u00e7\u00e3o de fibra?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "taxa",
                    "start": 11,
                    "end": 15
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 19,
                    "end": 29
                },
                {
                    "entity": "objeto",
                    "value": "fibra_optica",
                    "start": 33,
                    "end": 38
                }
            ]
        },
        {
            "text": "taxa de instala\u00e7\u00e3o de cabo",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "taxa",
                    "start": 0,
                    "end": 4
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 8,
                    "end": 18
                },
                {
                    "entity": "objeto",
                    "value": "cabo_rede",
                    "start": 22,
                    "end": 26
                }
            ]
        },
        {
            "text": "quanto \u00e9 a instala\u00e7\u00e3o do cabo de internet",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 11,
                    "end": 21
                },
                {
                    "entity": "objeto",
                    "value": "cabo_rede",
                    "start": 25,
                    "end": 41
                }
            ]
        },
        {
            "text": "quanto \u00e9 a instala\u00e7\u00e3o de internet fibra",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "instalacao",
                    "start": 11,
                    "end": 21
                },
                {
                    "entity": "objeto",
                    "value": "fibra_optica",
                    "start": 25,
                    "end": 39
                }
            ]
        },
        {
            "text": "suporte",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 0,
                    "end": 7
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "estou com problemas de interne",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 10,
                    "end": 19
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 23,
                    "end": 30
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "desbloquear internet",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "confianca",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 12,
                    "end": 20
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "como contratar?",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 5,
                    "end": 14
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "Quais planos voc\u00eas tem?",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 6,
                    "end": 12
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "pra minha casa",
            "entities": [
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 10,
                    "end": 14
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Com internet eu acho",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 4,
                    "end": 12
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "n\u00e3o",
            "entities": []
        },
        {
            "text": "quero saber se chega aqui em casa, essa internet",
            "entities": [
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 29,
                    "end": 33
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 40,
                    "end": 48
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "legal, pode me mostrar os planos novamente?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 26,
                    "end": 32
                }
            ]
        },
        {
            "text": "s\u00f3 queria ver os planos",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 17,
                    "end": 23
                }
            ]
        },
        {
            "text": "e os planos",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 5,
                    "end": 11
                }
            ]
        },
        {
            "text": "chega aqui em casa?",
            "entities": [
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 14,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quero gerar 2\u00aa via",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 12,
                    "end": 18
                }
            ]
        },
        {
            "text": "quero cancelar meu plano",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "cancelamento",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 19,
                    "end": 24
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "n\u00e3o recebi a fatura esse m\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 13,
                    "end": 19
                }
            ]
        },
        {
            "text": "minha internet t\u00e1 muito lenta hoje",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 6,
                    "end": 14
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "quero atendimento suporte",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 18,
                    "end": 25
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "quero suporte",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 6,
                    "end": 13
                }
            ]
        },
        {
            "text": "quero ser atendido",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "Atendimento",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "Atendimento \ud83d\udee0",
            "entities": [
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "segunda via mano",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "segunda via de novo",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "N\u00e3o agora",
            "entities": []
        },
        {
            "text": "quero mudar a data de vencimento do boleto",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 14,
                    "end": 32
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 36,
                    "end": 42
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "quero mudar a data de vencimento",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 14,
                    "end": 32
                }
            ]
        },
        {
            "text": "quero mudar a data de vencimneto do meu boleto",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "servicos",
                    "value": "vencimento",
                    "start": 14,
                    "end": 32
                },
                {
                    "entity": "objeto",
                    "value": "boleto",
                    "start": 40,
                    "end": 46
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "t\u00f4 afim de alterar a velocidade do meu plano",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 11,
                    "end": 18
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 21,
                    "end": 31
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 39,
                    "end": 44
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "quero fazer upgrade no plano",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 23,
                    "end": 28
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 12,
                    "end": 19
                }
            ]
        },
        {
            "text": "t\u00f4 pensando em fazer downgrade na internet de casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 34,
                    "end": 42
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 46,
                    "end": 50
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 21,
                    "end": 30
                }
            ]
        },
        {
            "text": "quero mudar plano da internet de casa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "alteracao",
                    "start": 6,
                    "end": 11
                },
                {
                    "entity": "objeto",
                    "value": "plano",
                    "start": 12,
                    "end": 17
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 21,
                    "end": 29
                },
                {
                    "entity": "pessoa",
                    "value": "fisica",
                    "start": 33,
                    "end": 37
                }
            ]
        },
        {
            "text": "quero alterar velocidade da internet da empresa",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "velocidade",
                    "start": 6,
                    "end": 24
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 28,
                    "end": 36
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 40,
                    "end": 47
                }
            ]
        },
        {
            "text": "quanto \u00e9 a internet para minha empresa?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 11,
                    "end": 19
                },
                {
                    "entity": "pessoa",
                    "value": "juridica",
                    "start": 31,
                    "end": 38
                }
            ]
        },
        {
            "text": "segundavia",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 10
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Segunda via",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 0,
                    "end": 11
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "cabo rompido",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "cabo_rede",
                    "start": 0,
                    "end": 4
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 5,
                    "end": 12
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "meu roteador quebrou",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "internet",
                    "start": 4,
                    "end": 12
                },
                {
                    "entity": "servicos",
                    "value": "suporte",
                    "start": 13,
                    "end": 20
                },
                {
                    "entity": "intent",
                    "value": "suporte"
                }
            ]
        },
        {
            "text": "\u00c9 fibra \u00f3tica?",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "fibra_optica",
                    "start": 2,
                    "end": 7
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Desejo saber mais sobre o D\/Garden",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quero saber do pr\u00e9dio",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "saber mais sobre o D\/graden",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "Quero falar com atendente agora",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "T\u00f4 afim de retirar minha segunda via",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "segundavia",
                    "start": 25,
                    "end": 36
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Pr\u00f3ximas Parcelas",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 9,
                    "end": 17
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Quest\u00f5es Financeiras",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Posi\u00e7\u00e3o financeira",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "posicaofinanceira",
                    "start": 0,
                    "end": 18
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "qual meu extrato financeiro?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "consultar parcela",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "consulta",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 10,
                    "end": 17
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "Consultar Parcela",
            "entities": [
                {
                    "entity": "servicos",
                    "value": "consulta",
                    "start": 0,
                    "end": 9
                },
                {
                    "entity": "objeto",
                    "value": "parcela",
                    "start": 10,
                    "end": 17
                },
                {
                    "entity": "intent",
                    "value": "financeiro"
                }
            ]
        },
        {
            "text": "quero ver minha posi\u00e7\u00e3o financeira",
            "entities": [
                {
                    "entity": "intent",
                    "value": "financeiro"
                },
                {
                    "entity": "servicos",
                    "value": "posicaofinanceira",
                    "start": 16,
                    "end": 34
                }
            ]
        },
        {
            "text": "Estou interessado em empreendimentos",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "empreendimentos",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quero empreender em um im\u00f3vel",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "imovel",
                    "start": 23,
                    "end": 29
                }
            ]
        },
        {
            "text": "Estou interessado em lotes",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "lotes",
                    "start": 21,
                    "end": 26
                }
            ]
        },
        {
            "text": "quero comprar um lote",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "servicos",
                    "value": "contratacao",
                    "start": 6,
                    "end": 13
                }
            ]
        },
        {
            "text": "posso empreender?",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quero comprar apartamento",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "estou interessado por empreendimento comercial",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quero empreender mais",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "como posso empreender",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "estou bastante interessado em empreender num lote de voc\u00eas",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "lote",
                    "start": 45,
                    "end": 49
                }
            ]
        },
        {
            "text": "quero comprar im\u00f3vel",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "imovel",
                    "start": 14,
                    "end": 20
                }
            ]
        },
        {
            "text": "empreender",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "apartamento",
            "entities": [
                {
                    "entity": "objeto",
                    "value": "apartamento",
                    "start": 0,
                    "end": 11
                }
            ]
        },
        {
            "text": "empreender em apartamentos",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "apartamento",
                    "start": 14,
                    "end": 26
                }
            ]
        },
        {
            "text": "quero empreender em apartamento com 2 su\u00edtes",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "apartamento",
                    "start": 20,
                    "end": 31
                }
            ]
        },
        {
            "text": "Quero fazer empreendimento",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "quero empreender",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                }
            ]
        },
        {
            "text": "Tenho interesse em apartamento",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "apartamento",
                    "start": 19,
                    "end": 30
                }
            ]
        },
        {
            "text": "quero comprar um apartamento",
            "entities": [
                {
                    "entity": "intent",
                    "value": "vendas"
                },
                {
                    "entity": "objeto",
                    "value": "apartamento",
                    "start": 17,
                    "end": 28
                }
            ]
        }
    ]
}


    for data in json_dump['data']:
        text = data['text']
        print(str(text).encode('utf8', 'replace'))

        count = 0
        intent_position = None
        while count < len(data['entities']):
            print(data['entities'][count]['entity'])
            if data['entities'][count]['entity'] == 'intent':
                intent_position = count
                break
            count += 1

        if intent_position is None:
            print('Não encontrou a chave entity com o valor intent.')
            continue

        repository_ = Repository.objects.get(uuid=repository)

        repository_update = repository_.current_update(None)
        print(intent_position)
        print(data['entities'][intent_position])
        example = RepositoryExample.objects.create(
            text=text.encode('utf-8', 'replace'),
            intent=data['entities'][intent_position]['value'],
            repository_update=repository_update

        )

        for entities in data['entities']:
            entity = entities['entity']
            value = entities['value']
            if not entity == 'intent':
                start = entities['start']
                end = entities['end']

                print(value.lower())
                print(entity.lower())
                entity_serializer = NewRepositoryExampleEntitySerializer(
                    data={
                        'repository_example': example.pk,
                        "label": value.replace(' ', '_').lower(),
                        "entity": entity.replace(' ', '_').lower(),
                        "start": start,
                        "end": end,
                    }
                )
                entity_serializer.is_valid(raise_exception=True)
                entity_serializer.save()

    # print(request.json())


    return True
