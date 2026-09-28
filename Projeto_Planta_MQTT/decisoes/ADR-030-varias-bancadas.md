# ADR-030: Várias bancadas na mesma monitoria

**Status:** Aceita com premissa. Altera partes das ADRs 013, 017, 021 e 024. O broker compartilhado passou a ser plano B pela [ADR-031](ADR-031-broker-por-grupo.md); o prefixo `bancadaN`, os IPs e o banco por bancada continuam valendo.

## Contexto

O laboratório tem vários CLPs, cada um com sua planta, e tem internet. A turma trabalha em grupos, cada um com o próprio notebook. As ADRs anteriores supunham uma bancada e um notebook rodando tudo. Com várias bancadas, é preciso decidir onde fica o broker, como os tópicos de uma bancada não se misturam com os de outra e como cada grupo se identifica.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Cada grupo instala seu próprio Mosquitto | Isolamento total | Instalação com privilégio de administrador e firewall em cada notebook; perde tempo de aula; celulares precisam saber o broker de cada grupo |
| **Um broker compartilhado no notebook do monitor, prefixo por bancada** | Uma instalação; o monitor vê todas as bancadas no MQTT Explorer; ACL separa os grupos | Porta 1883 precisa estar aberta na rede do laboratório |
| Broker público na internet | Nada a instalar | Expõe a planta; viola a [ADR-029](ADR-029-modelo-de-ameaca.md) |

## Decisão

- **Bancada = grupo.** Cada grupo recebe um número N e usa `BANCADA=bancadaN` no `config.env`. Os tópicos passam a ser `bancadaN/...`, com a mesma estrutura da seção 5.6 do Arquitetura.md.
- **Um broker compartilhado**, no notebook do monitor, iniciado por `iniciar.ps1 -Broker` numa janela visível (e não como serviço, para o log aparecer em aula). O serviço Mosquitto padrão do Windows precisa ser parado, porque ocupa a porta 1883.
- **Porta 1883 aberta na rede** do laboratório (substitui o `listener 1883 127.0.0.1` da [ADR-013](ADR-013-configuracao-do-broker.md)), porque gateways e middlewares rodam nos notebooks dos grupos. A 9001 continua para os celulares.
- **Usuários por bancada**, gerados por `broker/criar_usuarios.py N`: `gateway_bancadaN` e `middleware_bancadaN` só acessam `bancadaN/...`; `operador_bancadaN` lê e comanda só a bancada N (para o grupo testar os próprios comandos e usar o app); `app_leitura` e `app_operador` acessam todas as bancadas com `+/...`; `monitor` tem acesso total para o projetor. As senhas vão em `broker/credenciais.md` (fora do git), uma seção por bancada.
- **Gateway, middleware e banco no notebook do grupo.** Cada middleware grava em `dados/bancadaN.db` (substitui o `dados/planta.db` da [ADR-017](ADR-017-banco-de-dados.md)).
- **IP do CLP da bancada N:** 192.168.0.(10 + N); notebook do monitor 192.168.0.10 (premissa, substitui a tabela da [ADR-021](ADR-021-topologia-e-enderecamento.md) para a monitoria).
- **Internet disponível** não muda a [ADR-019](ADR-019-tecnologia-do-app.md): as bibliotecas continuam locais, porque um app que só funciona com internet falharia na primeira queda de rede em aula.

## Justificativa

Um broker único concentra o que exige privilégio de administrador numa só máquina, a do monitor, e transforma a ACL em algo visível: um grupo tenta publicar no tópico de outro e o broker descarta. Cada grupo continua dono da sua parte (gateway, middleware, banco), que é o que ele constrói na aula.

## Consequências

- Positivas: cada grupo fala com o próprio CLP, então a conexão Modbus única da [ADR-004](ADR-004-papeis-modbus-e-db.md) deixa de ser gargalo; o monitor acompanha todas as bancadas num só lugar.
- Negativas: o broker do monitor vira ponto único de falha da aula (mitigação: a planta continua segura pelo watchdog, e os gateways reconectam sozinhos); a porta 1883 aberta na rede do laboratório aumenta a superfície (mitigação: ACL e senhas por bancada, e o broker só roda durante a aula).

## Verificação

- `gateway_bancada1` tentando publicar em `bancada2/telemetria/temperatura`: mensagem descartada pelo broker.
- MQTT Explorer do monitor mostra `bancada1/...` a `bancadaN/...` ao mesmo tempo.
- Parar o broker por 30 s: todos os gateways voltam sozinhos e nenhum motor fica ligado sem heartbeat.

## Relacionadas

[ADR-004](ADR-004-papeis-modbus-e-db.md), [ADR-013](ADR-013-configuracao-do-broker.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-017](ADR-017-banco-de-dados.md), [ADR-019](ADR-019-tecnologia-do-app.md), [ADR-021](ADR-021-topologia-e-enderecamento.md), [ADR-024](ADR-024-execucao-dos-servicos.md)
