# ADR-024: Execução e ordem de inicialização

**Status:** Aceita

## Contexto

São três processos (broker, middleware, gateway) e opcionalmente o CLP simulado, num notebook com Windows 11. Subir na ordem errada gera erros de conexão no início; subir manualmente em quatro terminais é lento e propenso a erro na frente da turma.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Docker Compose | Ambiente idêntico em qualquer máquina | Docker Desktop no Windows é pesado e exige virtualização; nem toda máquina do laboratório tem |
| Serviços do Windows para tudo (por exemplo NSSM) | Sobem com o sistema | Ferramenta extra; logs e paradas menos visíveis em aula |
| **Mosquitto como serviço; Python em venv, iniciados por um script** | Poucas peças; tudo visível | Script específico de Windows |

## Decisão

- Mosquitto instalado pelo instalador oficial e registrado como serviço do Windows, com o `mosquitto.conf` do projeto.
- Um único venv em `Projeto_Planta_MQTT/.venv` com o `requirements.txt`.
- `iniciar.ps1`, nesta ordem:
  1. confere que o venv existe e o `config.env` existe;
  2. cria as regras de firewall, se faltarem ([ADR-022](ADR-022-firewall-do-notebook.md));
  3. reinicia o serviço do Mosquitto e espera a porta 9001 responder;
  4. inicia o `middleware.py` e espera `GET /docs` responder;
  5. se `MODO=simulado`, inicia o `clp_simulado.py`;
  6. inicia o `gateway.py`;
  7. mostra o endereço do app para os celulares.
- Cada processo Python roda em sua própria janela, para que o log fique visível em aula.
- `parar.ps1` encerra na ordem inversa.

## Justificativa

A ordem garante que cada peça encontre as que dependem dela já no ar. Janelas separadas deixam cada camada visível, o que é o próprio conteúdo da aula.

## Consequências

- Positivas: um comando sobe tudo, dentro do tempo de 5 min da [ADR-001](ADR-001-ambiente-e-requisitos.md).
- Negativas: roda só no Windows; para Linux seria preciso um script equivalente.

## Verificação

- Notebook recém-ligado: `iniciar.ps1` sobe tudo e o app mostra dados em menos de 5 min.
- Rodar `iniciar.ps1` duas vezes seguidas não cria regras nem processos duplicados.

## Relacionadas

[ADR-001](ADR-001-ambiente-e-requisitos.md), [ADR-013](ADR-013-configuracao-do-broker.md), [ADR-022](ADR-022-firewall-do-notebook.md), [ADR-025](ADR-025-configuracao-e-segredos.md), [ADR-028](ADR-028-versoes-fixadas.md)
