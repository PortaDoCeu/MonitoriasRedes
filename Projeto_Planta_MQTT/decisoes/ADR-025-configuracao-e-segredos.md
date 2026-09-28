# ADR-025: Configuração e segredos

**Status:** Aceita

## Contexto

IPs, portas, `VEL_MAX`, modo real ou simulado e senhas precisam ser iguais entre gateway, middleware, simulado e broker. O repositório é público ou compartilhado; senhas não podem ir para o git.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Valores no código | Nenhum arquivo extra | Mudar um IP exige editar vários programas; senha vai para o git |
| Um arquivo de configuração por programa | Isolamento | Mesmos valores repetidos; divergência |
| **Um `config.env` para todos, com modelo versionado** | Fonte única; segredos fora do git | Todos os programas leem o mesmo arquivo |

## Decisão

- `config.env` na raiz do projeto, lido por gateway, middleware e simulado; fora do git (`.gitignore`).
- `config.exemplo.env` versionado, com todas as chaves e valores de exemplo, sem senhas reais.
- Chaves mínimas: `MODO`, `MODBUS_HOST`, `MODBUS_PORT`, `MQTT_HOST`, `MQTT_PORT`, `MQTT_USUARIO_GATEWAY`, `MQTT_SENHA_GATEWAY`, `MQTT_USUARIO_MIDDLEWARE`, `MQTT_SENHA_MIDDLEWARE`, `VEL_MAX`, `PERIODO_LEITURA_S`, `HTTP_PORTA`.
- `broker/senhas` (gerado com `mosquitto_passwd`) também fora do git.
- A senha do `app_leitura` fica no `app.js` (é pública por decisão, [ADR-014](ADR-014-autenticacao-e-acl.md)); a do `app_operador` só no `broker/senhas` e com o monitor.
- Cada programa valida o `config.env` na partida e encerra com mensagem clara se faltar uma chave.

## Justificativa

Um arquivo, um lugar para mudar. O modelo versionado documenta o que precisa existir sem expor valores.

## Consequências

- Positivas: trocar CLP real por simulado é mudar duas linhas.
- Negativas: quem clona o repositório precisa copiar o modelo e preencher as senhas antes de rodar.

## Verificação

- `git ls-files` não lista `config.env` nem `broker/senhas`.
- Apagar uma chave do `config.env`: o programa encerra dizendo qual chave falta.

## Relacionadas

[ADR-002](ADR-002-modo-simulado.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-024](ADR-024-execucao-dos-servicos.md)
