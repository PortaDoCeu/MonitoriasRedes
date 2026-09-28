# Lista de Exercícios: Fieldbus, RS232/RS485 e Modbus

Monitoria de Introdução às Redes de Comunicação, UFPE

Esta lista está dividida em cinco partes:

1. Artigo *Evolution potentials for fieldbus systems* e Livro, Cap. 7 *Fieldbus Systems: History and Evolution*
2. Artigo *The fieldbus war: history or short break between battles?*
3. RS232: DTE versus DCE
4. Meio físico: RS232, RS485 e CSMA/CD (referência: normas TIA/EIA-232-F, TIA/EIA-485-A e IEEE 802.3)
5. Modbus: funções, RTU e TCP (referência: especificações da Modbus Organization, modbus.org: *MODBUS Application Protocol Specification* V1.1b3, *MODBUS over Serial Line Specification and Implementation Guide* V1.02 e *MODBUS Messaging on TCP/IP Implementation Guide* V1.0b)

Responda com suas palavras. Nas questões numéricas, mostre o raciocínio.

---

## Parte 1: Evolution potentials for fieldbus systems / Cap. 7 Fieldbus Systems: History and Evolution

**1.1** Cite duas principais motivações para o surgimento das redes Fieldbus.

**1.2** Leia o texto de apoio abaixo e responda.

> **Texto de apoio: a pirâmide de automação**
>
> A pirâmide de automação é um modelo que descreve a estrutura hierárquica da automação industrial. Ela representa como diferentes sistemas se conectam e interagem para formar um sistema de automação de fábrica ou processo. A classificação reflete os diferentes níveis desta pirâmide:
>
> **Nível 0, Campo:** abrange dispositivos no campo, como sensores e atuadores. Responsável pela coleta de dados básicos e execução de comandos de controle.
>
> **Nível 1, Controle:** inclui controladores, como CLPs (Controladores Lógicos Programáveis) e RTUs (Unidades Terminais Remotas). Interpreta os dados do campo e executa ações de controle.
>
> **Nível 2, Supervisão:** envolve sistemas SCADA (Supervisão, Controle e Aquisição de Dados) e DCS (Sistemas de Controle Distribuído). Coleta dados dos sistemas de controle, apresenta informações de forma visual e permite controle manual ou automatizado.
>
> **Nível 3, Gerenciamento de Produção:** abrange sistemas MES (Sistemas de Execução de Manufatura). Fornece informações em tempo real para gerenciar operações de produção, como planejamento, agendamento e rastreamento de produção.
>
> **Nível 4, Gerenciamento Corporativo:** inclui sistemas ERP (Planejamento de Recursos Empresariais). Interage com os níveis inferiores para fornecer informações estratégicas de gerenciamento, como finanças, cadeia de suprimentos e logística.
>
> O modelo da pirâmide de automação foi concebido para fornecer uma visão clara da estrutura organizacional necessária para a automação integrada, servindo como base para a Manufatura Integrada por Computador (CIM). Cada nível na pirâmide desempenha um papel distinto, mas todos trabalham juntos para fornecer automação eficiente e transparente.
>
> A pirâmide de automação é baseada na norma ISA-95 (também conhecida como IEC 62264). Esta norma internacional define um modelo padrão para a integração entre sistemas de controle de fábrica (níveis 0 a 2) e sistemas de gestão empresarial (nível 4), estabelecendo padrões para o intercâmbio de informações entre esses níveis. A ISA-95 descreve os seguintes níveis:
>
> - **Nível 0:** representa o processo físico real.
> - **Nível 1:** inclui dispositivos de campo, como sensores e atuadores que interagem diretamente com o processo.
> - **Nível 2:** sistemas de controle, como CLPs e RTUs, que coletam dados do campo e controlam diretamente os dispositivos.
> - **Nível 3:** sistemas de gerenciamento de operações de produção, como MES, que supervisionam e controlam a produção.
> - **Nível 4:** sistemas de gestão corporativa, como ERP, que fornecem informações estratégicas para a gestão do negócio.
>
> A ISA-95 foi desenvolvida para facilitar a integração entre sistemas de gestão e controle, proporcionando uma estrutura comum para a troca de informações e melhorando a eficiência operacional.

Com base nisso, as redes fieldbus encontram-se em qual camada da pirâmide da automação? Justifique usando as duas numerações apresentadas (pirâmide clássica e ISA-95).

**1.3** Qual padrão de meio físico precedeu praticamente todas as redes de campo industrial?

**1.4** Leia o texto de apoio e responda.

> Uma grande contribuição veio a partir das redes de computadores, quando o modelo ISO/OSI foi introduzido. Este modelo de referência é ponto de partida para o desenvolvimento de muitos protocolos de comunicação complexos.
>
> A primeira aplicação do modelo OSI ao domínio da automação foi a definição da rede MAP (Manufacturing Automation Protocol) na esteira da ideia CIM. O MAP pretendia ser uma estrutura para o controle abrangente de processos industriais, e o resultado da definição foi um protocolo poderoso e flexível, mas também muito complexo. Posteriormente, surgiu o padrão mais rígido chamado de Mini-MAP, que também não teve o sucesso esperado.

O que fez com que a rede MAP fosse redimensionada para a rede Mini-MAP?

**1.5** Explique quais as vantagens de se ter interoperabilidade em sistemas industriais.

**1.6** Quais são os principais benefícios trazidos pelos sistemas Fieldbus em comparação com os sistemas de cabeamento ponto a ponto?

**1.7** Quais camadas do modelo OSI um sistema Fieldbus normalmente usa? Por que as demais costumam ser omitidas?

**1.8** Quais foram os dois projetos europeus que protagonizaram a "guerra dos Fieldbus"?

**1.9** Qual foi a solução adotada pela IEC para resolver o impasse na padronização?

**1.10** O que é o IEC 61784 e qual sua relação com o IEC 61158?

**1.11** Quais são os três paradigmas de comunicação discutidos no capítulo? Dê uma característica de cada um.

---

## Parte 2: The fieldbus war: history or short break between battles?

**2.1** Na segunda metade da década de 1980, no início dos esforços da IEC no comitê técnico TC65C, o desenvolvimento de sistemas fieldbus era principalmente um empreendimento europeu, impulsionado por projetos de pesquisa que ainda tinham uma forte formação acadêmica, bem como por muitos desenvolvimentos proprietários. Os resultados mais promissores foram o FIP francês e o PROFIBUS alemão.

Em relação aos paradigmas de comunicação existentes, explique com detalhes qual era o da arquitetura FIP e qual era o da arquitetura PROFIBUS.

**2.2** No dia 15 de junho de 1999, o Comitê da IEC decidiu seguir um caminho completamente novo para quebrar o impasse. Um mês depois, no dia 16 de julho, os representantes dos principais concorrentes no debate (Fieldbus Foundation, Fisher Rosemount, ControlNet International, Rockwell Automation, organização de usuários PROFIBUS e Siemens) assinaram um "Memorando de Entendimento", que pretendia pôr fim à guerra do fieldbus. A resolução foi criar um padrão IEC 61158 grande e abrangente, acomodando todos os sistemas fieldbus. Com grande esforço e sob substancial pressão de tempo, o projeto foi compilado, submetido para votação e divulgado como padrão em 31 de dezembro de 2000.

Ficou evidente que a coleta de especificações de fieldbus na norma IEC 61158 é inútil para qualquer implementação. É necessário um manual para uso prático mostrando quais partes podem ser compiladas para um sistema funcional e como isso pode ser feito. Esta diretriz foi compilada posteriormente como IEC 61784, como uma definição dos chamados "perfis".

Quais padrões compuseram inicialmente a norma IEC 61784?

**2.3** Como a Ethernet encontrada nas primeiras redes de computadores foi incorporada com sucesso às redes de campo industrial?

---

## Parte 3: RS232, DTE versus DCE

> **Texto de apoio**
>
> Na especificação RS232, **DTE** (*Data Terminal Equipment*, equipamento terminal de dados) e **DCE** (*Data Communications Equipment*, equipamento de comunicação de dados) são os dois tipos de equipamento que ficam nas pontas de uma conexão serial. Em geral, o DTE é o computador e o DCE é o modem.
>
> Como a RS232 foi pensada principalmente para ligar um DTE a um DCE, a pinagem dos dois lados foi definida para que o cabo fosse o mais simples possível: o pino 1 de um lado liga no pino 1 do outro, o pino 2 no pino 2, e assim por diante. Esse tipo de cabo é chamado de **cabo direto** (*straight-through*), e ainda é o padrão para ligar um modem a um PC.
>
> O problema aparece quando se quer ligar dois DTEs diretamente, sem modem, o que é muito comum. Com um cabo direto entre dois DTEs, o transmissor de um fica ligado ao transmissor do outro, e o receptor ao receptor, e nenhuma comunicação acontece. Nesse caso é preciso um cabo que cruze as linhas, ligando o transmissor de um equipamento ao receptor do outro e vice-versa. Esse cabo é chamado de **null-modem**, porque substitui os dois modems que uma aplicação RS232 tradicional colocaria entre os dois DTEs.

**3.1** Defina DTE e DCE e dê um exemplo de equipamento de cada tipo.

**3.2** Por que a pinagem da RS232 permite ligar um DTE a um DCE com um cabo direto?

**3.3** Explique o que acontece, no nível dos sinais TX e RX, quando dois DTEs são ligados com um cabo direto.

**3.4** O que é um cabo null-modem e de onde vem esse nome?

**3.5** Você precisa ligar um notebook (via adaptador USB-serial) à porta serial de programação de um CLP, que também se comporta como DTE. Qual cabo você usa? E se a ligação fosse notebook para modem?

**3.6** Num conector DB9 de um DTE, o pino 2 é RX e o pino 3 é TX, e o pino 5 é o terra de sinal (GND). Desenhe as ligações mínimas (três fios) de um cabo null-modem entre dois DB9 de DTEs.

---

## Parte 4: Meio físico, RS232, RS485 e CSMA/CD

**4.1** A RS232 usa transmissão *single-ended* (referenciada ao terra) e a RS485 usa transmissão *diferencial*. Explique a diferença entre as duas e por que a diferencial é mais imune a ruído em ambiente industrial.

**4.2** Compare RS232 e RS485 preenchendo a tabela:

| Característica | RS232 | RS485 |
|---|---|---|
| Tipo de sinal | | |
| Topologia (ponto a ponto ou multiponto) | | |
| Número de dispositivos no barramento | | |
| Distância máxima típica | | |
| Taxa de transmissão típica | | |
| Full-duplex ou half-duplex (na versão a 2 fios) | | |

**4.3** Cite pelo menos três vantagens da RS485 sobre a RS232 para uma rede de campo que liga um CLP a vários inversores de frequência espalhados pelo chão de fábrica.

**4.4** Para que servem os resistores de terminação (tipicamente 120 Ω) nas pontas de um barramento RS485? Onde eles devem ser colocados?

**4.5** A RS485 define protocolo de comunicação? Em qual camada do modelo OSI ela se encaixa, e o que é preciso adicionar por cima para que dois equipamentos troquem dados de verdade?

**4.6** Numa RS485 a 2 fios, todos os dispositivos compartilham o mesmo par. O que aconteceria se dois dispositivos transmitissem ao mesmo tempo? Como o Modbus RTU evita que isso aconteça? (retome esta questão na Parte 5)

**4.7** Explique o funcionamento do **CSMA/CD** (*Carrier Sense Multiple Access with Collision Detection*), descrevendo o que significa cada parte da sigla.

**4.8** O que é o algoritmo de *backoff* exponencial binário e por que ele é usado depois de uma colisão?

**4.9** Na Ethernet a 10 Mbit/s, o quadro mínimo é de 64 bytes. Calcule o tempo que leva para transmitir esse quadro e explique por que existe um tamanho mínimo de quadro no CSMA/CD.

**4.10** Por que o CSMA/CD é considerado **não determinístico**? Por que isso foi, historicamente, um argumento contra o uso de Ethernet no chão de fábrica?

**4.11** Em uma rede Ethernet moderna com *switches* e enlaces *full-duplex*, o CSMA/CD ainda atua? Explique o que mudou.

---

## Parte 5: Modbus

### 5.A Conceitos gerais

**5.1** Em qual camada do modelo OSI o Modbus está definido? O que muda entre Modbus RTU, Modbus ASCII e Modbus TCP?

**5.2** Explique a relação mestre/escravo (no Modbus serial) ou cliente/servidor (no Modbus TCP). Um escravo pode iniciar uma comunicação por conta própria?

**5.3** O modelo de dados do Modbus tem quatro tabelas. Complete:

| Tabela | Tamanho de cada item | Leitura/Escrita | Exemplo de uso |
|---|---|---|---|
| Coils | | | |
| Discrete Inputs | | | |
| Input Registers | | | |
| Holding Registers | | | |

### 5.B Funções

**5.4** Complete a tabela com as funções mais importantes do Modbus:

| Código (decimal) | Código (hex) | Nome | Tabela acessada |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 15 | | | |
| 16 | | | |

**5.5** Qual a diferença entre as funções 6 e 16? Em que situação vale a pena usar a 16 mesmo para escrever poucos registradores?

**5.6** Qual a diferença entre as funções 3 e 4? Por que não existe uma função de escrita para Input Registers?

**5.7** Na função 5 (*Write Single Coil*), quais valores são enviados no campo de dados para ligar e para desligar a bobina?

**5.8** Quando um escravo não consegue atender uma requisição, ele devolve uma **resposta de exceção**. Como o código de função é modificado nessa resposta? Explique o significado dos códigos de exceção 01, 02, 03 e 04.

### 5.C Modbus RTU e controle de acesso ao meio

**5.9** Descreva os campos de um quadro Modbus RTU (endereço, função, dados, CRC), dizendo o tamanho de cada um.

**5.10** Qual a faixa de endereços válidos de escravos no Modbus RTU? O que acontece quando o mestre envia uma mensagem para o endereço 0?

**5.11** Explique o **controle de acesso ao meio** no Modbus RTU. Por que não há colisões em um barramento RS485 com Modbus RTU, mesmo sem nenhum mecanismo como o CSMA/CD?

**5.12** Esse método de acesso ao meio é determinístico? Como você estimaria o tempo máximo para o mestre ler todos os escravos de uma rede?

**5.13** No Modbus RTU não há um caractere de início nem de fim de quadro. Como o receptor sabe onde um quadro termina? Explique o intervalo de silêncio de 3,5 tempos de caractere.

**5.14** No Modbus RTU cada caractere tem 11 bits (1 start, 8 dados, 1 paridade ou 1 stop extra, 1 stop). Calcule o intervalo de silêncio de 3,5 caracteres a 9600 bit/s.

**5.15** Para que serve o CRC no final do quadro RTU? Que tipo de erro ele detecta?

**5.16** Decodifique a requisição Modbus RTU abaixo (valores em hexadecimal), identificando cada campo:

```
11 03 00 6B 00 03 76 87
```

**5.17** Decodifique a resposta correspondente e diga quais valores (em decimal) foram lidos em cada registrador:

```
11 03 06 AE 41 56 52 43 40 49 AD
```

**5.18** Monte (sem o CRC) a requisição Modbus RTU para que o mestre escreva o valor 1000 (decimal) no holding register de endereço 10 do escravo 5, usando a função 6.

### 5.D Modbus TCP e controle de acesso ao meio

**5.19** O que é o cabeçalho **MBAP**? Descreva cada um dos seus campos (Transaction Identifier, Protocol Identifier, Length, Unit Identifier) e o tamanho de cada um.

**5.20** Por que o quadro Modbus TCP não tem CRC, ao contrário do RTU? Quem faz a verificação de erros nesse caso?

**5.21** Qual a porta TCP padrão do Modbus TCP? Quem abre a conexão, o cliente ou o servidor?

**5.22** Para que serve o Unit Identifier, já que no Modbus TCP o dispositivo é identificado pelo endereço IP? Dê um exemplo de situação em que ele é essencial (pense em um *gateway* Modbus TCP para Modbus RTU).

**5.23** Explique o **controle de acesso ao meio** no Modbus TCP. O Modbus TCP define algum mecanismo próprio de acesso ao meio ou ele depende de outra camada? Compare com o Modbus RTU.

**5.24** Uma rede Modbus TCP com um *hub* antigo (half-duplex) e outra com um *switch* (full-duplex). Em qual das duas o CSMA/CD pode causar atrasos imprevisíveis? Justifique.

**5.25** Decodifique a requisição Modbus TCP abaixo:

```
00 01 00 00 00 06 01 03 00 00 00 02
```

**5.26** Decodifique a resposta abaixo e explique por que o campo Length vale 7:

```
00 01 00 00 00 07 01 03 04 00 0A 00 14
```

**5.27** O que significa a resposta abaixo? Qual foi o provável erro do cliente?

```
00 02 00 00 00 03 01 83 02
```

**5.28** Monte a requisição Modbus TCP completa (MBAP + PDU) para escrever os valores 100 e 200 (decimal) nos holding registers 0 e 1 do dispositivo com Unit ID 1, usando a função 16 e Transaction ID 5.

### 5.E Mais pacotes

Nesta seção, todos os endereços são base zero (o primeiro item de cada tabela tem endereço 0).

**5.29** Decodifique a requisição e a resposta Modbus TCP abaixo. Quantas coils foram lidas, a partir de qual endereço, e qual o estado (ligada ou desligada) de cada uma? Explique por que o campo Length da resposta vale 5.

```
Requisição: 00 03 00 00 00 06 01 01 00 13 00 0A
Resposta:   00 03 00 00 00 05 01 01 02 CD 01
```

**5.30** Decodifique a requisição e a resposta Modbus TCP abaixo. Qual tabela do modelo de dados foi acessada e qual valor (em decimal) foi lido?

```
Requisição: 00 04 00 00 00 06 01 04 00 08 00 01
Resposta:   00 04 00 00 00 05 01 04 02 00 0A
```

**5.31** Monte (sem o CRC) a requisição Modbus RTU para que o mestre **ligue** a coil de endereço 172 do escravo 17, usando a função 5. O que muda no quadro para **desligar** a mesma coil?

**5.32** Monte a requisição Modbus TCP completa (MBAP + PDU) para escrever, com a função 15, os estados abaixo nas coils de endereço 19 a 28 do dispositivo com Unit ID 1, usando Transaction ID 7. Mostre como os bits são agrupados nos bytes de dados.

| Endereço | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|
| Estado | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 0 |

**5.33** Um mestre Modbus RTU recebeu a resposta abaixo (CRC omitido). Qual escravo respondeu, a qual função ele está respondendo, e o que deu errado?

```
0A 81 02
```

### 5.F Segurança

**5.34** Olhando os quadros das seções 5.D e 5.E, existe algum campo de autenticação ou de criptografia no Modbus TCP? Que consequência isso tem para alguém que consiga se conectar na porta 502 do CLP?

**5.35** Cite duas medidas de rede que reduzem esse risco sem alterar o protocolo Modbus.
