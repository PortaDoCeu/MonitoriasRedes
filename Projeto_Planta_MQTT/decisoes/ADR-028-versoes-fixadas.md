# ADR-028: Versões fixadas

**Status:** Aceita

## Contexto

Bibliotecas mudam de API entre versões (o pymodbus 3.x mudou nomes de argumentos, o paho-mqtt 2.0 mudou a assinatura dos callbacks). Um `pip install` feito na véspera pode trazer uma versão que quebra o código.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Sem versão no `requirements.txt` | Sempre o mais novo | Quebra imprevisível |
| Faixas (`>=3.6,<4`) | Recebe correções | Ainda pode quebrar dentro da faixa |
| **Versões exatas (`==`)** | Reprodutível | Atualização manual |

## Decisão

- `requirements.txt` com versões exatas de pymodbus, paho-mqtt, fastapi, uvicorn e pytest, geradas por `pip freeze` no momento da implementação, depois de todos os testes passarem.
- Versão do Python registrada no README do projeto (3.12).
- Versão do Mosquitto registrada no README do projeto.
- MQTT.js e Chart.js com a versão no nome do arquivo em `static/vendor/` ([ADR-019](ADR-019-tecnologia-do-app.md)).
- Nenhuma versão é escolhida neste documento: os números são os que passarem nos testes.

## Justificativa

O ambiente da aula precisa ser idêntico ao ambiente em que os testes passaram.

## Consequências

- Positivas: reinstalar em outro notebook gera o mesmo ambiente.
- Negativas: correções de segurança das bibliotecas não chegam sozinhas; revisar versões uma vez por semestre.

## Verificação

- `pip install -r requirements.txt` num venv limpo, seguido de `pytest`: tudo passa.
- `pip list --outdated` revisado no início de cada semestre.

## Relacionadas

[ADR-008](ADR-008-stack-do-gateway.md), [ADR-016](ADR-016-stack-do-middleware.md), [ADR-019](ADR-019-tecnologia-do-app.md), [ADR-024](ADR-024-execucao-dos-servicos.md)
