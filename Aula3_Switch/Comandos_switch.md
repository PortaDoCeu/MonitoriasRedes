# Lista de Consulta – ExtremeXOS 21.1
**Switch:** Extreme Networks X440-G2-48t-10GE4

> Notação: `<obrigatório>`  `{opcional}`  `[a | b]` = escolha uma opção.
> Portas no X440-G2 usam o formato `1:1` (slot:porta) ou, em switch standalone, `1`, `2`, `1-4`, `1,3,5`.
> Dica: em qualquer ponto, digite `?` para ver as opções ou `TAB` para completar o comando.
> As alterações ficam só na memória até você rodar `save configuration`.

---

## 1. Conexão ao switch

```bash
ssh -o HostKeyAlgorithms=+ssh-rsa admin@{IP_do_switch}
```
O switch pede a senha (`admin@IP's password:`); digite e tecle Enter.

| Comando | Descrição |
|---|---|
| `show version` | Versão do ExtremeXOS e hardware |
| `show switch` | Informações gerais do switch |
| `show configuration` | Mostra a configuração atual |
| `save configuration` | Salva a configuração (confirmar com `y`) |
| `exit` ou `logout` | Encerra a sessão |

---

## 2. Mirror (espelhamento de portas)

### 2.1 Mirror nomeado (múltiplas instâncias)

| Ação | Comando |
|---|---|
| Mostrar todos | `show mirror` |
| Mostrar um | `show mirror <nome_mirror>` |
| Criar | `create mirror <nome_mirror> {description <texto>}` |
| Definir porta de destino (monitor) | `configure mirror <nome_mirror> to port <porta> {tagged \| untagged}` |
| Adicionar porta de origem | `configure mirror <nome_mirror> add port <porta(s)> [ingress \| egress \| ingress-and-egress]` |
| Remover porta de origem | `configure mirror <nome_mirror> delete port <porta(s)>` |
| Ativar | `enable mirror <nome_mirror>` |
| Desativar | `disable mirror <nome_mirror>` |
| Deletar | `delete mirror <nome_mirror>` |

Exemplo:
```
create mirror MIR1 description "captura servidor"
configure mirror MIR1 to port 48
configure mirror MIR1 add port 1-4 ingress-and-egress
enable mirror MIR1
```

### 2.2 Mirror legado (instância única)

| Ação | Comando |
|---|---|
| Mostrar | `show mirroring` |
| Ativar e definir porta de destino | `enable mirroring to port <porta> [tagged \| untagged]` |
| Adicionar porta de origem | `configure mirroring add port <porta(s)> [ingress \| egress \| ingress-and-egress]` |
| Adicionar VLAN como origem | `configure mirroring add vlan <nome_vlan> {port <porta>}` |
| Remover porta de origem | `configure mirroring delete port <porta(s)>` |
| Desativar / "deletar" | `disable mirroring` |

> Obs.: `enable mirroring to port` serve para ativar e escolher o destino; para apagar tudo, use `disable mirroring` e remova as origens com `configure mirroring delete`.
> Use um modelo (2.1 ou 2.2), sem misturar os dois.

---

## 3. VLAN

| Ação | Comando |
|---|---|
| Mostrar todas | `show vlan` |
| Mostrar uma | `show vlan <nome_vlan>` |
| Mostrar detalhes | `show vlan <nome_vlan> detail` |
| Mostrar por tag | `show vlan tag <tag>` |
| Criar | `create vlan <nome_vlan>` |
| Definir tag (ID 802.1Q) | `configure vlan <nome_vlan> tag <1-4094>` |
| Criar já com tag | `create vlan <nome_vlan> tag <1-4094>` |
| Renomear | `configure vlan <nome_vlan> name <novo_nome>` |
| Descrição | `configure vlan <nome_vlan> description "<texto>"` |
| Adicionar porta (untagged/access) | `configure vlan <nome_vlan> add ports <porta(s)> untagged` |
| Adicionar porta (tagged/trunk) | `configure vlan <nome_vlan> add ports <porta(s)> tagged` |
| Remover porta | `configure vlan <nome_vlan> delete ports <porta(s)>` |
| Deletar | `delete vlan <nome_vlan>` |
| Deletar todas (exceto Default/Mgmt) | `delete vlan all` |
| Ver VLANs de uma porta | `show ports <porta> information` |

**Desativar uma VLAN:** o ExtremeXOS não tem um comando `disable vlan` para L2. Para desativar na prática, remova as portas (`configure vlan <nome> delete ports <portas>`) ou desabilite as portas (`disable ports <portas>`). Para o roteamento da VLAN: `disable ipforwarding vlan <nome_vlan>`.

Exemplo:
```
create vlan VLAN10 tag 10
configure vlan VLAN10 add ports 1-8 untagged
configure vlan VLAN10 add ports 48 tagged
```

> Uma porta só pode ser untagged em uma VLAN por vez. Para movê-la, remova-a da VLAN atual (por exemplo, `Default`) antes:
> `configure vlan Default delete ports 1-8`

---

## 4. Endereços MAC (FDB) por VLAN

### 4.1 Consultar

| Ação | Comando |
|---|---|
| Mostrar toda a tabela | `show fdb` |
| Por VLAN | `show fdb vlan <nome_vlan>` |
| Por porta | `show fdb ports <porta>` |
| Por MAC | `show fdb <mac>` (ex.: `show fdb 00:11:22:33:44:55`) |
| Somente permanentes | `show fdb permanent` |
| Tempo de aging | `show fdb` (mostra o aging no cabeçalho) |

### 4.2 Adicionar / remover entradas estáticas (MAC permitido)

| Ação | Comando |
|---|---|
| Adicionar MAC estático | `create fdbentry <mac> vlan <nome_vlan> port <porta>` |
| Remover MAC estático | `delete fdbentry <mac> vlan <nome_vlan>` |
| Remover todos os estáticos | `delete fdbentry all` |
| Bloquear um MAC (blackhole) | `create fdbentry <mac> vlan <nome_vlan> blackhole` |
| Limpar MACs aprendidos | `clear fdb` (ou `clear fdb vlan <nome_vlan>` / `clear fdb ports <porta>`) |
| Configurar aging | `configure fdb agingtime <segundos>` (0 = sem aging) |

Exemplo:
```
create fdbentry 00:11:22:33:44:55 vlan VLAN10 port 5
```

### 4.3 Restringir quais MACs são aceitos em uma porta/VLAN

**Opção A – Limitar aprendizado (limit-learning):**

| Ação | Comando |
|---|---|
| Limitar nº de MACs | `configure ports <porta(s)> vlan <nome_vlan> limit-learning <n> {action [blackhole \| stop-learning]}` |
| Travar MACs já aprendidos | `configure ports <porta(s)> vlan <nome_vlan> lock-learning` |
| Destravar | `configure ports <porta(s)> vlan <nome_vlan> unlock-learning` |
| Remover limite | `configure ports <porta(s)> vlan <nome_vlan> unlimited-learning` |
| Ver configuração | `show ports <porta> information detail` |

**Opção B – Desabilitar aprendizado e usar só entradas estáticas (lista de MACs permitidos):**

| Ação | Comando |
|---|---|
| Desabilitar aprendizado | `disable learning {drop-packets \| forward-packets} ports <porta(s)>` |
| Reabilitar aprendizado | `enable learning ports <porta(s)>` |
| Cadastrar MAC permitido | `create fdbentry <mac> vlan <nome_vlan> port <porta>` |

Fluxo típico da opção B:
```
disable learning drop-packets ports 5
create fdbentry 00:11:22:33:44:55 vlan VLAN10 port 5
create fdbentry aa:bb:cc:dd:ee:ff vlan VLAN10 port 5
```

---

## 5. Comandos auxiliares

| Comando | Descrição |
|---|---|
| `show ports <porta> information` | Estado, VLANs e velocidade da porta |
| `show ports <porta> configuration` | Configuração da porta |
| `enable ports <porta(s)>` / `disable ports <porta(s)>` | Liga/desliga porta |
| `show log` | Mensagens de log |
| `show iproute` / `show ipconfig` | Rotas e interfaces IP |
| `save configuration` | Salva a configuração |
| `unconfigure switch` | **Cuidado:** apaga a configuração e reinicia |

---

*Observação:* a sintaxe exata de alguns comandos (principalmente `mirror`, `limit-learning` e `disable learning`) pode variar ligeiramente entre builds do 21.1. Confirme com `?` no CLI ou no capítulo correspondente do ExtremeXOS 21.1 Command Reference Guide.
