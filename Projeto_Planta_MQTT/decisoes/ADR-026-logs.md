# ADR-026: Registro de eventos (logs)

**Status:** Aceita

## Contexto

Quando algo falha em aula, é preciso saber em qual camada, em segundos. Depois da aula, é preciso reconstruir o que aconteceu.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| `print` | Nenhum setup | Sem nível, sem horário, sem arquivo |
| Sistema central de logs (ELK, Loki) | Busca e painéis | Infraestrutura desproporcional |
| **Módulo `logging` do Python, console e arquivo rotativo** | Padrão; nível, horário e origem em cada linha | Nenhum painel |

## Decisão

- `logging` com formato `horário nível [programa] mensagem`.
- Console em nível INFO (o que a turma vê nas janelas).
- Arquivo `logs/<programa>.log` em nível DEBUG, com `RotatingFileHandler` de 5 MB e 3 arquivos.
- Eventos obrigatórios em INFO: conexão e desconexão (Modbus e MQTT), cada comando com `id`, resultado e motivo, mudança de status.
- Leituras periódicas só em DEBUG, para não poluir o console.
- Mosquitto com `log_dest file` em `logs/mosquitto.log`.
- Senhas nunca aparecem em log.
- Pasta `logs/` fora do git.

## Justificativa

O console mostra os eventos que interessam à aula; o arquivo guarda o detalhe para depois. Rotação impede que um log esquecido encha o disco.

## Consequências

- Positivas: toda falha do ensaio de aceitação deixa rastro com horário.
- Negativas: nenhuma correlação automática entre logs de programas diferentes, mitigada pelo `id` de comando presente em todos.

## Verificação

- `grep` pela senha do gateway em `logs/`: zero ocorrências.
- Seguir um `id` de comando: aparece no log do gateway e no banco com o mesmo resultado.

## Relacionadas

[ADR-011](ADR-011-validacao-de-comandos.md), [ADR-024](ADR-024-execucao-dos-servicos.md), [ADR-027](ADR-027-testes-e-aceitacao.md)
