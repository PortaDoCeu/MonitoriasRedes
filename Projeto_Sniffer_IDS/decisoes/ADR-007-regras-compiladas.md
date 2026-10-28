# ADR-007: Regras compiladas no firmware

**Status:** Aceita

## Contexto

As regras dizem o que é suspeito: quem pode escrever, quais operações nunca deveriam ocorrer, que taxa é normal. Elas mudam pouco (quando a planta muda), mas são o coração da detecção: quem conseguir alterá-las pode cegar o sensor.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Tabela `const rule_t RULES[]` no firmware** | Ninguém altera pela rede; sem interpretador; sem memória extra | Mudar uma regra exige gravar firmware |
| Regras recebidas por MQTT | Flexível; muda em tempo real | Canal de entrada no sensor; precisa de autenticação e assinatura; vira alvo |
| Arquivo de regras na flash | Muda na manutenção sem recompilar | Precisa de interpretador e de proteção do arquivo |

## Decisão

- Regras e inventário (`assets`) são tabelas constantes, compiladas no firmware.
- Cada regra é **dado**, não código: protocolo, operação, papel de origem proibido, faixa de endereço e taxa máxima (Arquitetura, seção 6.3).
- O sensor não aceita nenhuma configuração pela rede.
- Na versão Python, as regras são funções curtas numa lista `REGRAS`; o inventário é o dicionário `ATIVOS`.

## Justificativa

Num sensor de segurança, o menor número possível de entradas é a escolha mais segura. Atualizar o firmware na manutenção é aceitável porque a planta muda pouco.

## Consequências

- Positivas: nada a atacar pela rede na lógica de detecção; regras auditáveis lendo uma tabela.
- Negativas: cada planta precisa do seu firmware (ou de um inventário gerado na compilação); ajustar falso positivo leva mais tempo.

## Verificação

- O firmware não assina nenhum tópico MQTT e não abre nenhuma porta de escuta (verificado com varredura de portas na interface Wi-Fi).
- Cada regra tem um `.pcap` de teste que a dispara e um que não a dispara.

## Relacionadas

[ADR-003](ADR-003-uplink-wifi-mqtt.md), [Arquitetura, seção 8](../Arquitetura.md#8-regras-iniciais)
