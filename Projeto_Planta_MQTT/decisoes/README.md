# Decisões de Projeto (ADRs)

Registro das decisões necessárias para colocar o projeto em produção. Aqui, **produção** é o sistema funcionando de ponta a ponta durante uma monitoria, com a turma usando o próprio celular ([ADR-001](ADR-001-ambiente-e-requisitos.md)).

Cada arquivo é uma ADR (*Architecture Decision Record*): uma decisão, por que ela foi tomada, o que se abriu mão e como verificar que ela está sendo cumprida. A arquitetura em si está em [Arquitetura.md](../Arquitetura.md).

## Como ler

Todas as ADRs têm as mesmas seções:

| Seção | Conteúdo |
|---|---|
| Status | `Aceita` ou `Aceita com premissa` (depende de um valor ainda não conferido na bancada) |
| Contexto | O problema e as restrições |
| Alternativas consideradas | Opções avaliadas, com prós e contras |
| Decisão | O que foi escolhido, com valores concretos |
| Justificativa | Por que essa e não as outras |
| Consequências | O que se ganha e o que se perde |
| Verificação | Teste objetivo que prova que a decisão está sendo cumprida |
| Relacionadas | ADRs e seções da arquitetura ligadas a esta |

Uma ADR aceita não é editada para mudar de ideia. Se uma decisão mudar, cria-se uma ADR nova que a substitui, e a antiga recebe no status "Substituída por ADR-0XX".

## Índice

| ADR | Decisão | Área | Status |
|---|---|---|---|
| [001](ADR-001-ambiente-e-requisitos.md) | Ambiente-alvo e requisitos não funcionais | Escopo | Aceita |
| [002](ADR-002-modo-simulado.md) | Modo simulado obrigatório (`clp_simulado.py`) | Escopo | Aceita |
| [003](ADR-003-premissas-de-hardware.md) | Premissas de hardware da planta | Planta e CLP | Aceita com premissa |
| [004](ADR-004-papeis-modbus-e-db.md) | CLP servidor, gateway cliente único, DB `Array[0..99] of Word` | Planta e CLP | Aceita |
| [005](ADR-005-seguranca-funcional-no-clp.md) | Segurança funcional no CLP e no hardware | Planta e CLP | Aceita |
| [006](ADR-006-contrato-de-dados.md) | Contrato de dados congelado | Planta e CLP | Aceita |
| [007](ADR-007-protecao-do-clp.md) | Proteção de acesso ao CLP, PUT/GET desabilitado | Planta e CLP | Aceita |
| [008](ADR-008-stack-do-gateway.md) | Python 3.12, pymodbus síncrono, paho-mqtt 2.x | Gateway | Aceita |
| [009](ADR-009-concorrencia-no-gateway.md) | Fila de comandos; laço principal é o único dono do Modbus | Gateway | Aceita |
| [010](ADR-010-ciclo-e-temporizacao.md) | Ciclo de 1 s, timeout de 0,5 s, watchdog de 3 s | Gateway | Aceita |
| [011](ADR-011-validacao-de-comandos.md) | Validação em 4 passos e respostas `executado`/`rejeitado`/`falhou` | Gateway | Aceita |
| [012](ADR-012-reconexao.md) | Reconexão e descarte de comandos expirados | Gateway | Aceita |
| [013](ADR-013-configuracao-do-broker.md) | Mosquitto 2.x, 1883 só local, 9001 WebSocket, sem persistência | Broker | Aceita |
| [014](ADR-014-autenticacao-e-acl.md) | Usuários `gateway`, `middleware`, `app_leitura`, `app_operador` e ACL | Broker | Aceita |
| [015](ADR-015-sem-tls-na-monitoria.md) | Sem TLS na monitoria (risco aceito) | Broker | Aceita |
| [016](ADR-016-stack-do-middleware.md) | FastAPI + uvicorn, escritor único no banco | Middleware | Aceita |
| [017](ADR-017-banco-de-dados.md) | SQLite em WAL, UTC ISO 8601, sem expurgo | Middleware | Aceita |
| [018](ADR-018-api-http.md) | API HTTP somente leitura e exportação CSV | Middleware | Aceita |
| [019](ADR-019-tecnologia-do-app.md) | HTML e JS puro, bibliotecas servidas localmente | App | Aceita |
| [020](ADR-020-interacao-de-comando.md) | Botão bloqueado até a resposta, tempo limite de 3 s | App | Aceita |
| [021](ADR-021-topologia-e-enderecamento.md) | Sub-rede 192.168.0.0/24 com AP dedicado | Rede e implantação | Aceita com premissa |
| [022](ADR-022-firewall-do-notebook.md) | Firewall do notebook: só 8000 e 9001 | Rede e implantação | Aceita |
| [023](ADR-023-relogio.md) | Relógio do notebook como fonte única de horário | Rede e implantação | Aceita |
| [024](ADR-024-execucao-dos-servicos.md) | Mosquitto como serviço, Python em venv, `iniciar.ps1` | Rede e implantação | Aceita |
| [025](ADR-025-configuracao-e-segredos.md) | `config.env` único, segredos fora do git | Rede e implantação | Aceita |
| [026](ADR-026-logs.md) | `logging` em console e arquivo rotativo | Qualidade | Aceita |
| [027](ADR-027-testes-e-aceitacao.md) | Testes unitários, integração e ensaio de aceitação | Qualidade | Aceita |
| [028](ADR-028-versoes-fixadas.md) | Versões exatas no `requirements.txt` | Qualidade | Aceita |
| [029](ADR-029-modelo-de-ameaca.md) | Modelo de ameaça, alvo SL 1 da IEC 62443 | Segurança | Aceita |
| [030](ADR-030-varias-bancadas.md) | Várias bancadas: prefixo `bancadaN`; broker compartilhado (hoje plano B) | Rede e implantação | Aceita com premissa |
| [031](ADR-031-broker-por-grupo.md) | Cada grupo configura e sobe o próprio Mosquitto (etapa 2 da aula) | Broker | Aceita |

## Premissas a validar na bancada

Valores assumidos para o projeto avançar. Cada um deve ser conferido antes da primeira aula; se algum cair, as ADRs listadas são revisadas.

| Premissa | Valor assumido | ADRs afetadas | Como validar |
|---|---|---|---|
| CPU | S7-1200 CPU 1214C | 003, 004 | Etiqueta da CPU e Device configuration |
| Saída analógica | SB 1232 AQ em corrente, usada de 4 a 20 mA | 003, 005 | Signal board instalada na CPU |
| Termopar | Tipo K, módulo SM 1231 TC | 003, 006 | Etiquetas do sensor e do módulo; resolução no manual do SM 1231 |
| Realimentação de velocidade | Não existe; HR1 copia HR3 | 003, 006 | Fiação da saída analógica do inversor |
| Motor | 4 polos, 60 Hz | 003 | Placa do motor |
| `VEL_MAX` | 1700 rpm | 003, 005, 011, 025 | Rotação nominal da placa, arredondada para baixo |
| Faixa de temperatura | 0 a 150 °C | 003, 006 | Tipo de termopar e fonte de calor da bancada |
| Limite de alarme | 80 °C | 003, 005 | Combinar com o professor responsável |
| Emergência e chave local/remoto | Existem, ligadas ao CLP; emergência corta a potência | 003, 005 | Inspeção da bancada |
| Conexões por instância de `MB_SERVER` | Uma | 004, 029 | Manual Siemens Entry-ID 102020340 e teste com dois clientes |
| IP do CLP | 192.168.0.1 (bancada única) ou 192.168.0.(10 + N) na monitoria | 021, 030 | Online & diagnostics no TIA Portal; faixa da rede do laboratório |
| AP Wi-Fi | Disponível, com DHCP e WPA2; isolamento de clientes se houver | 021, 015 | Equipamento do laboratório |

## Riscos aceitos

Riscos conhecidos que ficam sem tratamento nesta versão, de forma deliberada.

| Risco | Por que foi aceito | O que o reduz | ADR |
|---|---|---|---|
| Senha do operador e dados MQTT legíveis na rede da aula | TLS inviável com celulares de alunos e sem internet | Wi-Fi isolado com WPA2, senha exclusiva, limites no CLP | [015](ADR-015-sem-tls-na-monitoria.md) |
| Celulares na mesma sub-rede do CLP | Segmentação real exigiria roteamento no notebook | Conexão Modbus única, proteção da CPU, isolamento no AP | [021](ADR-021-topologia-e-enderecamento.md) |
| Acesso Modbus direto ao CLP com o gateway desligado | Modbus TCP não tem autenticação | Gateway sempre ligado durante a aula; limites no CLP | [029](ADR-029-modelo-de-ameaca.md) |
| Negação de serviço contra o broker ou o AP | Fora do alvo SL 1 | Watchdog leva a planta ao estado seguro | [029](ADR-029-modelo-de-ameaca.md) |
| Motor gira até 3 s após o gateway parar | Tempo do watchdog | Emergência física sempre disponível | [005](ADR-005-seguranca-funcional-no-clp.md), [010](ADR-010-ciclo-e-temporizacao.md) |
| Operação só testada por 3 h | Uso real é uma aula | Ensaio de 3 h antes da primeira aula | [001](ADR-001-ambiente-e-requisitos.md) |

## Antes da primeira aula

1. Preencher a tabela de premissas com os valores reais.
2. Revisar as ADRs afetadas por premissas que mudaram.
3. Rodar o ensaio de aceitação completo ([ADR-027](ADR-027-testes-e-aceitacao.md)) na bancada e no modo simulado.
