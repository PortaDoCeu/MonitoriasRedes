# ADR-021: Topologia e endereçamento da rede

**Status:** Aceita com premissa

## Contexto

CLP, notebook e celulares precisam estar numa mesma rede. O CLP e o notebook ficam no cabo, pelo switch da bancada; os celulares só têm Wi-Fi. A rede não pode ter rota para a internet ([ADR-001](ADR-001-ambiente-e-requisitos.md), [ADR-015](ADR-015-sem-tls-na-monitoria.md)).

![Rede da bancada](../img/rede.png)

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Wi-Fi da universidade | Nada a montar | Celulares e CLP em redes diferentes; sem controle de firewall; expõe a bancada |
| Notebook como hotspot | Sem equipamento extra | Limite de clientes do hotspot do Windows (8, a confirmar); notebook vira roteador |
| Duas sub-redes (OT e Wi-Fi) com o notebook roteando | Segmentação real entre zonas | Exige duas interfaces e roteamento no notebook; complexo para a aula |
| **Uma sub-rede, AP dedicado ligado ao switch, firewall no notebook** | Simples; suporta 40 clientes | Celulares estão na mesma sub-rede do CLP |

## Decisão

| Equipamento | Endereço | Observação |
|---|---|---|
| Sub-rede | 192.168.0.0/24 | Sem gateway padrão para a internet |
| CLP | 192.168.0.1 | Endereço que o TIA Portal propõe por padrão, o mesmo da Aula 2 (premissa) |
| AP Wi-Fi | 192.168.0.2 | WPA2, SSID e senha próprios da bancada, DHCP ligado |
| Notebook | 192.168.0.10 | Fixo, no cabo |
| Celulares | 192.168.0.100 a 192.168.0.199 | DHCP do AP |

## Justificativa

É a topologia mais simples que atende 40 clientes. A exposição do CLP aos celulares na mesma sub-rede é compensada por: conexão Modbus única ocupada pelo gateway ([ADR-004](ADR-004-papeis-modbus-e-db.md)), proteção de acesso da CPU ([ADR-007](ADR-007-protecao-do-clp.md)) e isolamento de clientes no AP, se disponível.

## Consequências

- Positivas: montagem em minutos com um AP comum.
- Negativas: não há segmentação de rede de verdade entre OT e TI; as zonas são lógicas. Esta é a principal diferença para uma implantação real e está registrada nos riscos aceitos. Pode virar exercício: redesenhar com VLAN usando o switch gerenciado do laboratório.

## Verificação

- Celular conectado recebe IP entre .100 e .199 e abre `http://192.168.0.10:8000`.
- `ping 8.8.8.8` a partir do notebook, com o cabo da internet desligado, falha.
- Se o AP tiver isolamento de clientes: `ping 192.168.0.1` a partir de um celular falha (registrar o resultado).

## Relacionadas

[ADR-004](ADR-004-papeis-modbus-e-db.md), [ADR-007](ADR-007-protecao-do-clp.md), [ADR-015](ADR-015-sem-tls-na-monitoria.md), [ADR-022](ADR-022-firewall-do-notebook.md), [Arquitetura.md, seção 10](../Arquitetura.md)
