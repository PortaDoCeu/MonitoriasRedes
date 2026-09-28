# ADR-022: Firewall do notebook

**Status:** Aceita

## Contexto

O notebook concentra broker, middleware e gateway. Por padrão, qualquer serviço que abra uma porta pode ficar acessível à rede, inclusive programas que não fazem parte do projeto.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Firewall desligado | Nada bloqueia a aula | Expõe tudo que roda no notebook aos celulares |
| **Firewall do Windows ligado, com regras de entrada só para o necessário** | Superfície mínima | Uma etapa de preparação |

## Decisão

Regras de entrada no perfil de rede usado na bancada:

| Porta | Protocolo | Origem permitida | Uso |
|---|---|---|---|
| 8000 | TCP | 192.168.0.0/24 | App e API do middleware |
| 9001 | TCP | 192.168.0.0/24 | MQTT sobre WebSocket |

Todo o resto de entrada é bloqueado. A porta 1883 não precisa de regra porque o Mosquitto só escuta em 127.0.0.1 ([ADR-013](ADR-013-configuracao-do-broker.md)). O uvicorn escuta em `0.0.0.0:8000`. As regras são criadas pelo `iniciar.ps1` com `New-NetFirewallRule`, se ainda não existirem.

## Justificativa

Duas portas atendem tudo que os celulares precisam. Restringir a origem à sub-rede da bancada impede acesso caso o notebook seja ligado em outra rede com o sistema rodando.

## Consequências

- Positivas: um celular não alcança nenhum outro serviço do notebook.
- Negativas: criar regras de firewall exige executar o `iniciar.ps1` como administrador na primeira vez.

## Verificação

- De um celular: `:8000` e `:9001` respondem; qualquer outra porta testada (por exemplo 1883, 445) não responde.
- `Get-NetFirewallRule -DisplayName "Planta*"` lista exatamente as duas regras.

## Relacionadas

[ADR-013](ADR-013-configuracao-do-broker.md), [ADR-021](ADR-021-topologia-e-enderecamento.md), [ADR-024](ADR-024-execucao-dos-servicos.md)
