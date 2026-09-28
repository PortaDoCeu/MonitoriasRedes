# ADR-031: Cada grupo levanta o próprio broker

**Status:** Aceita. Substitui o broker compartilhado da [ADR-030](ADR-030-varias-bancadas.md) como caminho principal da monitoria; o broker compartilhado vira plano B.

## Contexto

Na ADR-030 o broker era um só, no notebook do monitor, e os grupos só consumiam. Gabriel decidiu que configurar o broker faz parte do que a turma precisa aprender: o `mosquitto.conf`, os usuários e a ACL são exatamente onde as decisões de segurança do MQTT acontecem (autenticação, permissões por tópico, portas expostas). Com o broker pronto, esse conteúdo ficava invisível.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Manter o broker compartilhado, só mostrado pelo monitor | Nenhum tempo extra de aula | A turma nunca escreve a configuração nem a ACL; segurança do MQTT fica teórica |
| **Cada grupo escreve e sobe o próprio Mosquitto** | A turma configura autenticação e ACL de verdade; na etapa de segurança testa a ACL que escreveu | Cerca de 40 minutos de aula; exige Mosquitto instalado e o serviço padrão parado em cada notebook |
| Cada grupo usa um broker embutido em Python | Nada a instalar | Não é o que se usa na indústria; esconde o arquivo de configuração |

## Decisão

- **Etapa 2 da aula (cerca de 40 min):** cada grupo completa `broker/mosquitto.conf` e `broker/acl` a partir de esqueletos com `TODO`, cria os usuários com `mosquitto_passwd` e sobe o broker com `mosquitto -c broker\mosquitto.conf -v`.
- **Usuários do broker do grupo:** `gateway`, `middleware`, `app_leitura` (senha `leitura`, pública, [ADR-014](ADR-014-autenticacao-e-acl.md)) e `operador`. As permissões são as mesmas da ADR-014, restritas aos tópicos `bancadaN/...`.
- **Configuração:** a mesma decisão da [ADR-013](ADR-013-configuracao-do-broker.md) (anônimo proibido, sem persistência, 1883 para os programas e 9001 WebSocket para o app), com uma diferença: a 1883 fica aberta na rede, e não só em 127.0.0.1, porque é mais simples para a turma e deixa o broker acessível para o monitor conferir. O ganho de fechar a 1883 aparece como pergunta na etapa de segurança.
- **No `config.env`:** `BROKER_LOCAL=sim` e `MQTT_HOST=127.0.0.1`. O `iniciar.ps1` sobe o broker do grupo antes do middleware e do gateway.
- **Gabarito** em `aula/gabarito_broker/`, testado por `testes/test_broker_grupo.py`; **esqueleto** em `aula/esqueleto_broker/`, que vai para `broker/` no pacote dos alunos.
- **Plano B:** grupo travado por 15 minutos usa o broker compartilhado do monitor (ADR-030), com `BROKER_LOCAL=nao` e as credenciais `gateway_bancadaN`/`middleware_bancadaN`.
- **Cronograma:** preparação, etapa do CLP e intervalos encolhem para caber a nova etapa; as etapas seguintes são renumeradas (publicar 3, comandar 4, banco e app 5, segurança 6).

## Justificativa

A ACL deixa de ser uma tabela num documento e passa a ser um arquivo que o grupo escreveu, errou e corrigiu. Na etapa de segurança, a tentativa de burlar a ACL é contra a configuração do próprio grupo, e a janela do broker mostra a publicação negada. É o mesmo raciocínio de zonas e condutos da Aula 2: quem configura o conduto decide o que passa.

## Consequências

- Positivas: a turma configura autenticação, autorização por tópico e listeners; a captura da senha no Wireshark (etapa 6) é do tráfego do próprio broker.
- Negativas: o cronograma fica apertado; cada notebook precisa do Mosquitto instalado e do serviço padrão parado (exige administrador, feito em casa); o monitor não vê mais todas as bancadas num só MQTT Explorer, e confere cada grupo no notebook dele.
- Como gateway e broker estão no mesmo notebook, a captura do Wireshark é na interface de loopback.

## Verificação

- `pytest testes/test_broker_grupo.py`: com o gabarito, conexão anônima e senha errada são recusadas, o `operador` comanda e o `app_leitura` não.
- Na aula, checkpoint da etapa 2: MQTT Explorer recusado sem usuário e com senha errada, aceito com `operador`.

## Relacionadas

[ADR-013](ADR-013-configuracao-do-broker.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-015](ADR-015-sem-tls-na-monitoria.md), [ADR-024](ADR-024-execucao-dos-servicos.md), [ADR-030](ADR-030-varias-bancadas.md)
