# Programa do CLP: FB_Planta

`FB_Planta.scl` tem a lógica da bancada: escala da temperatura, referência de velocidade para a saída analógica, partida do inversor, chave local/remoto, emergência, watchdog do heartbeat e códigos de falha. É a mesma lógica do `clp_simulado.py`, que tem testes automatizados; o SCL em si **ainda não foi compilado nem testado num CLP real**.

Ele se apoia no que a Aula 2 já deixou pronto em cada CLP: o `MB_SERVER` e o DB `DB_HoldingRegisters` com `holdingRegister : Array[0..99] of Word`.

## Passo a passo no TIA Portal

### 1. Abrir o projeto da Aula 2

Abra o projeto em que o `MB_SERVER` já funciona. Confirme na Watch Table que o `cliente.js` ou um cliente Modbus consegue ler o DB. Se isso não funcionar, resolva primeiro seguindo o notebook da Aula 2: nada daqui funciona sem o `MB_SERVER`.

### 2. Endereço IP da bancada

Em **Device configuration**, clique na porta PROFINET e, em **Properties > General > Ethernet addresses**, defina o IP da bancada:

| Bancada | IP do CLP |
|---|---|
| bancada1 | 192.168.0.11 |
| bancada2 | 192.168.0.12 |
| bancada N | 192.168.0.(10 + N) |

Premissa ([ADR-030](../decisoes/ADR-030-varias-bancadas.md)): confirme com a faixa real da rede do laboratório.

### 3. Tabela de variáveis da planta

Em **PLC tags > Add new tag table**, crie a tabela `Planta` com as variáveis abaixo. O endereço depende da fiação de cada bancada: confira em **Device configuration**, clicando em cada módulo e olhando **I/O addresses**.

| Nome | Tipo | Endereço | O que é |
|---|---|---|---|
| `TemperaturaTC` | Int | canal do SM 1231 TC (ex.: %IW96) | Temperatura do termopar |
| `ChaveRemoto` | Bool | entrada digital (ex.: %I0.0) | TRUE com a chave em remoto |
| `EmergenciaOk` | Bool | entrada digital (ex.: %I0.1) | Contato NF: TRUE sem emergência |
| `FalhaInversor` | Bool | entrada digital (ex.: %I0.2) | Saída de falha do inversor |
| `PartidaInversor` | Bool | saída digital (ex.: %Q0.0) | Partida do inversor |
| `ReferenciaAQ` | Int | saída do SB 1232 (ex.: %QW80) | Referência de velocidade em corrente |

Confira no módulo SM 1231 TC que o tipo de termopar está configurado (tipo K, premissa) e a unidade em graus Celsius. Na saída do SB 1232, configure o tipo **Current** e a faixa **0 to 20 mA**.

### 4. Importar o FB

1. Na árvore do projeto, abra **External source files > Add new external file** e escolha `FB_Planta.scl`.
2. Clique com o botão direito no arquivo importado e escolha **Generate blocks from source**.
3. O bloco `FB_Planta [FBx]` aparece em **Program blocks**.

Se a geração acusar erro em `VAR CONSTANT`, mova as constantes para a seção **Constant** da interface do bloco com os mesmos nomes e valores.

### 5. Chamar o FB no Main [OB1]

Numa rede nova do `Main [OB1]`, depois da rede do `MB_SERVER`, arraste o `FB_Planta` e aceite o DB de instância `FB_Planta_DB`. Ligue os pinos:

| Pino | Ligar em |
|---|---|
| `iTemperatura` | `"TemperaturaTC"` |
| `xRemoto` | `"ChaveRemoto"` |
| `xEmergenciaOk` | `"EmergenciaOk"` |
| `xFalhaInversor` | `"FalhaInversor"` |
| `qPartida` | `"PartidaInversor"` |
| `qReferencia` | `"ReferenciaAQ"` |
| `hr` | `"DB_HoldingRegisters".holdingRegister` |

Em SCL, a mesma chamada fica:

```
"FB_Planta_DB"(iTemperatura := "TemperaturaTC",
               xRemoto := "ChaveRemoto",
               xEmergenciaOk := "EmergenciaOk",
               xFalhaInversor := "FalhaInversor",
               qPartida => "PartidaInversor",
               qReferencia => "ReferenciaAQ",
               hr := "DB_HoldingRegisters".holdingRegister);
```

### 6. Proteção do CLP (ADR-007)

Em **Properties > Protection & Security**:
- nível de acesso com senha para escrita (a senha fica com o monitor);
- **Connection mechanisms**: deixe **Permit access with PUT/GET communication** desmarcado.

### 7. Compilar, carregar e conferir

1. **Compile** (Ctrl+B) e **Download to device**.
2. Coloque em RUN.
3. Numa Watch Table, monitore `"DB_HoldingRegisters".holdingRegister[0]` a `[12]`.
4. Aqueça o termopar com a mão: `[0]` deve subir (°C × 10).
5. Gire a chave local/remoto: o bit 1 de `[2]` deve acompanhar.

O motor **não liga pela Watch Table sozinha**, porque o watchdog exige o heartbeat mudando em `[12]`. Para testar o acionamento, rode o gateway de referência apontando para este CLP e comande pelo app ou pelo `mosquitto_pub`.

## Diferenças que podem aparecer no CLP real

| Item | O que conferir |
|---|---|
| Escala do termopar | Se o SM 1231 TC entrega °C × 10. Se entregar outra escala, ajuste antes de `#hr[0]` e nas constantes `LIMITE_TEMP`, `TEMP_MIN`, `TEMP_MAX` |
| Fio rompido | Com diagnóstico ligado, o módulo costuma entregar 32767; `TEMP_MAX` já trata isso como falha 5 |
| 4 mA | `AQ_4MA = 5530` assume 0 a 20 mA em 0 a 27648. Se o inversor aceitar 0 a 10 V, troque a saída para tensão e use `AQ_4MA = 0` |
| Emergência | Se o contato for NA em vez de NF, inverta em `xEmergenciaOk` |
