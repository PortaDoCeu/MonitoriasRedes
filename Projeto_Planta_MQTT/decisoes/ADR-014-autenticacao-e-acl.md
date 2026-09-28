# ADR-014: Autenticação e controle de acesso no broker

**Status:** Aceita

## Contexto

O app roda no navegador do celular, e todo código de uma página web pode ser lido por quem a abre. Qualquer senha embutida no HTML é pública. Ao mesmo tempo, a turma inteira precisa ver os dados, mas só quem conduz a aula deveria comandar o motor.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Sem autenticação | Nenhum atrito | Qualquer um publica em qualquer tópico, inclusive falsificar telemetria |
| Um usuário `app` com senha no HTML | Simples | Senha pública; todo aluno pode comandar o motor |
| **Usuário de leitura público e usuário operador digitado no login** | Turma vê tudo; só quem sabe a senha comanda | Uma tela de login no app |

## Decisão

| Usuário | Senha | Pode publicar | Pode assinar |
|---|---|---|---|
| `gateway` | em `config.env` | `bancada1/telemetria/#`, `bancada1/comando/resposta`, `bancada1/gateway/estado` | `bancada1/comando/velocidade`, `bancada1/comando/motor` |
| `middleware` | em `config.env` | nada | `bancada1/#` |
| `app_leitura` | embutida no app (pública por natureza) | nada | `bancada1/telemetria/#`, `bancada1/comando/resposta`, `bancada1/gateway/estado` |
| `app_operador` | digitada na tela de login, mantida só em memória | `bancada1/comando/velocidade`, `bancada1/comando/motor` | igual ao `app_leitura` |

O app abre com `app_leitura`. Os controles de comando só aparecem depois do login como operador, que abre uma nova conexão MQTT com essas credenciais.

## Justificativa

Uma credencial que precisa estar no navegador de todos não é segredo; então ela recebe só o mínimo (leitura). O poder de comando fica numa credencial que nunca é gravada no código. A ACL também impede que um aluno com `app_leitura` publique telemetria falsa.

## Consequências

- Positivas: alunos não conseguem comandar nem falsificar dados, mesmo lendo o código da página.
- Negativas: a senha do operador trafega sem criptografia na porta 9001 ([ADR-015](ADR-015-sem-tls-na-monitoria.md)); quem capturar o tráfego a obtém.

## Verificação

- Com `mosquitto_pub -u app_leitura` tentar publicar em `bancada1/comando/motor`: mensagem descartada pelo broker (não chega ao gateway).
- Com `app_leitura` tentar publicar em `bancada1/telemetria/temperatura`: descartada.
- `grep` na pasta do app pela senha do operador: zero ocorrências.

## Relacionadas

[ADR-013](ADR-013-configuracao-do-broker.md), [ADR-015](ADR-015-sem-tls-na-monitoria.md), [ADR-020](ADR-020-interacao-de-comando.md), [ADR-025](ADR-025-configuracao-e-segredos.md), [Arquitetura.md, seção 6](../Arquitetura.md)
