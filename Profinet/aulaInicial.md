---

# Módulo 1: Fundamentos das Redes Industriais

---

## Tópico 1: TI vs. TA — O Modelo *Best Effort* da Internet face ao Determinismo Industrial

A convergência de redes nas plantas industriais exige a coexistência de dois ecossistemas com requisitos de desempenho diametralmente opostos: a Tecnologia da Informação (TI) e a Tecnologia da Automação (TA).

### 1.1 Tecnologia da Informação (TI) e o Modelo *Best Effort*

As redes de TI utilizam a pilha de protocolos TCP/IP (com base na norma **IEEE 802.3 Ethernet** comercial). Suas principais características são:

* **Foco no Rendimento (*Throughput*):** A prioridade é o volume total de dados transmitidos por unidade de tempo (ex.: Megabits por segundo), e não o instante exato da chegada do pacote.
* **Integridade dos Dados:** O protocolo de transporte utilizado predominantemente é o TCP (**RFC 793**), que implementa mecanismos de controle de fluxo, numeração de pacotes e retransmissão em caso de perda ou corrupção (*Acknowledge/Retransmit*).
* **Modelo *Best Effort* (Melhor Esforço):** A rede garante que o dado chegará ao destino íntegro, mas não há garantias matemáticas ou temporais sobre *quando* ele chegará. O tempo de trânsito (latência) é variável, introduzindo *jitter* (variação estatística do atraso de rede).

### 1.2 Tecnologia da Automação (TA) e o Determinismo

Os sistemas de controle em tempo real (CLPs, remotas de I/O, acionamentos de motores) exigem **Determinismo**.

* **Definição de Determinismo:** É a garantia matemática de que um evento de comunicação ocorrerá dentro de um limite de tempo estrito e previsível, denominado tempo de ciclo de barramento ($t_{ciclo}$).
* **Previsibilidade Temporal:** O atraso de transmissão (latência) deve ser constante. O *jitter* deve ser próximo de zero.
* **Impacto da Latência:** Em sistemas de TA, um pacote de dados correto que chega após o estouro do tempo limite do temporizador de guarda (*Watchdog Timer*) é considerado um dado inválido. A perda de sincronia temporal resulta em falhas de controle, paragens de emergência (*Trip*) ou danos mecânicos ao hardware.

---

## Tópico 2: O Paradigma PROFINET — A diferença entre a Norma de Infraestrutura (IEC) e o Protocolo de Tempo Real

O PROFINET não se limita a um protocolo de aplicação de software; ele é uma arquitetura de rede padronizada internacionalmente, dividida entre infraestrutura física e canais lógicos de processamento.

### 2.1 A Norma de Infraestrutura (IEC 61158 e IEC 61784-2)

A padronização do PROFINET é regida por normas internacionais que determinam os requisitos de conformidade para o hardware industrial:

* **IEC 61158:** Define os serviços e protocolos das camadas físicas, de enlace e de aplicação para barramentos industriais (*Fieldbuses*). No catálogo da norma, o PROFINET é classificado como **Tipo 10**.
* **IEC 61784-2:** Especifica os Perfis de Ethernet em Tempo Real (RTE). Ela estabelece os critérios construtivos necessários para que dispositivos Ethernet genéricos operem em ambientes industriais, exigindo:
* **Robustez Mecânica e Elétrica:** Cabos blindados (STP/SFTP) Categoria 5e ou superior, condutores de cobre espessos para suportar flexão mecânica e conectores industriais com grau de proteção elevado (RJ45 IP20 robusto ou M12 codificação D com proteção IP67) com alta imunidade a Interferência Eletromagnética (EMI).
* **Requisitos de Comutação (*Switching*):** Os switches integrados ou dedicados devem suportar o método de comutação *Store-and-Forward* ou *Cut-Through*, além de suporte obrigatório a VLANs e priorização de tráfego baseada na norma **IEEE 802.1Q**.



### 2.2 O Protocolo de Tempo Real (PROFINET IO)

A norma divide o canal de comunicação física em duas abordagens lógicas concorrentes dentro do mesmo cabo:

* **Canal Aberto / Não-Tempo Real (PROFINET NRT):** Opera utilizando o frame Ethernet II padrão com o campo *EtherType* preenchido com **`0x0800`** (IPv4). Os dados passam obrigatoriamente pelas camadas 3 (IP) e 4 (TCP/UDP) do processador do CLP. É utilizado para tarefas acíclicas como parametrização de engenharia via TIA Portal, diagnósticos de hardware e páginas web internas.
* **Canal de Tempo Real (PROFINET RT):** Ignora completamente as camadas de rede (IP) e transporte (TCP/UDP). Os dados da aplicação industrial são mapeados diretamente na Camada 2 (Enlace de Dados), encapsulados em frames Ethernet com o *EtherType* fixado em **`0x8892`**. Isso desvia o tráfego do sistema operacional do CLP (*Bypass* de pilha), reduzindo o tempo de processamento de software interno a microsegundos.

---

## Tópico 3: Topologias de Rede e Alta Disponibilidade — Linha, Estrela e Anel com Protocolo MRP

A disposição física dos cabos e a capacidade de tolerar falhas físicas de hardware determinam a confiabilidade da rede de automação.

### 3.1 Características das Topologias no Ambiente Industrial

#### Topologia em Linha (*Daisy Chain*)

* **Mecanismo:** Os dispositivos possuem switches internos de 2 portas. O cabo sai da porta 2 do dispositivo A e conecta-se à porta 1 do dispositivo B, sucessivamente.
* **Vantagens:** Minimização do custo de cabeamento e eliminação da necessidade de switches centrais no painel elétrico.
* **Desvantagens:** Baixa resiliência. Um único ponto de falha (rompimento de cabo ou desligamento de um CLP/Remota intermediária) isola todos os dispositivos localizados a jusante na linha.

#### Topologia em Estrela

* **Mecanismo:** Todos os dispositivos de campo conectam suas portas de rede diretamente a um switch Ethernet industrial centralizado.
* **Vantagens:** Isolamento de falhas. O rompimento de um cabo danifica apenas a comunicação daquele nó específico, mantendo o restante da rede operacional.
* **Desvantagens:** Alto custo de infraestrutura (metragem de cabos elevada) e dependência de um ponto único de falha (se o switch central falhar, toda a rede colapsa).

### 3.2 Protocolo MRP (Media Redundancy Protocol - IEC 62439-2)

Para unir a economia de cabeamento da linha com a alta disponibilidade, o PROFINET utiliza a topologia em anel físico gerenciada pelo protocolo **MRP**, normatizado pela **IEC 62439-2**.

#### Regras de Operação do Hardware:

1. **Definição de Papéis:** Um único dispositivo do anel (geralmente o CLP Mestre) deve ser parametrizado no software de engenharia como **MRM (Media Redundancy Manager)**. Todos os outros nós conectados no anel operam obrigatoriamente como **MRC (Media Redundancy Clients)**.
2. **Prevenção de Loop Lógico:** Em redes Ethernet normais, fechar um anel físico gera uma tempestade de *broadcast*, travando a rede. Para evitar isso, o MRM bloqueia logicamente a passagem de dados genéricos em uma das suas duas portas físicas, transformando o anel físico em uma topologia em linha do ponto de vista do tráfego de dados.
3. **Quadros de Teste (*Test Frames*):** O MRM envia continuamente frames de teste cíclicos (com identificação própria de controle MRP) saindo pela sua Porta 1 e esperando recebê-los de volta pela sua Porta 2, monitorando a integridade mecânica do anel.

#### Mecanismo de Reconfiguração em Caso de Falha:

* **Detecção:** Quando ocorre o rompimento de qualquer cabo do anel ou a queima de um MRC, os frames de teste enviados pelo MRM param de chegar à porta oposta.
* **Ação do Manager (MRM):** Ao detectar a ausência dos frames de teste, o MRM assume que o anel foi quebrado. Ele desbloqueia instantaneamente a porta de dados que estava inativa, restaurando a conectividade lógica da rede através do caminho alternativo.
* **Notificação:** O MRM envia um comando de controle para todos os MRCs limparem suas tabelas de endereçamento MAC (*MAC Address Tables / CAM Tables*). Isso força a rede a reaprender imediatamente as novas rotas físicas de comunicação.
* **Tempo de Recuperação Determinístico:** A norma IEC 62439-2 garante que o processo completo de transição e reconfiguração da rede ocorre em um tempo máximo de **200 milissegundos** para um anel contendo até 50 nós MRC, impedindo que os temporizadores de *Watchdog* de comunicação industrial estourem e parem o processo produtivo.

---

# Módulo 2: O Tráfego de Automação (A Via Rápida — PROFINET RT/IRT)

---

## Tópico 4: O *Bypass* ao Modelo OSI: Comunicação Direta na Camada 2

O tráfego determinístico do PROFINET IO baseia-se na eliminação de camadas intermediárias de processamento de software para reduzir a latência de transmissão.

### 4.1 Arquitetura de Pilha Reduzida

A pilha TCP/IP padrão exige o processamento de sete camadas (ou quatro no modelo TCP/IP), demandando tempo de CPU para processar cabeçalhos de rede e transporte. O **PROFINET RT (Real-Time)** executa um *bypass* (desvio) nas Camadas 3 (Rede) e 4 (Transporte).

* **Mapeamento Direto:** Os dados da Camada de Aplicação industrial (Camada 7) são injetados diretamente na Camada de Enlace de Dados (Camada 2).
* **Identificação de Hardware:** A comunicação dispensa endereços IP e portas lógicas (TCP/UDP). A indexação de origem e destino baseia-se exclusivamente no endereço físico **MAC Address**.

### 4.2 O Papel do EtherType `0x8892`

No frame Ethernet II padrão, o campo *EtherType* (composto por 2 bytes) indica qual protocolo está encapsulado no *payload*.

* O tráfego PROFINET RT utiliza obrigatoriamente o EtherType **`0x8892`**.
* **Mecanismo de Filtro por Hardware:** Ao detectar o valor `0x8892`, o controlador da interface de rede (NIC) do dispositivo (ex.: chip ASIC ERTEC da Siemens) direciona o pacote diretamente para a memória de buffers de I/O do processador de automação. O sistema operacional e a pilha de rede padrão do dispositivo não são acionados, eliminando o tempo de processamento associado a rotinas de software (*overhead de software*).

---

## Tópico 5: Mecanismos de Hardware: *Quality of Service* (QoS) e *Update Time*

Para garantir que os frames de automação não sofram atrasos por colisões ou congestionamentos em switches, utilizam-se parâmetros normatizados de priorização e temporização.

### 5.1 Priorização de Tráfego via IEEE 802.1Q (QoS)

O PROFINET RT utiliza a extensão de cabeçalho da norma **IEEE 802.1Q** (VLAN Tagging) incorporada ao frame Ethernet.

* **Campo PCP (*Priority Code Point*):** Dentro da tag de 4 bytes do IEEE 802.1Q, existem 3 bits dedicados à definição de prioridade de tráfego, permitindo 8 níveis diferentes (0 a 7).
* **Configuração PROFINET:** O tráfego RT é indexado fixamente com **Prioridade 6** (*Internetwork Control*).
* **Comportamento no Switch:** Quando um switch industrial compatível com PROFINET (Conformance Class A, B ou C) recebe múltiplos pacotes simultâneos, o circuito interno de comutação analisa o campo PCP. Pacotes com marcação 6 são alocados na fila de saída de maior prioridade (*High Priority Egress Queue*), sobrepondo-se ao tráfego de dados convencional (Prioridade 0 - *Best Effort*).

### 5.2 *Update Time* e Mecanismo de *Watchdog*

A troca de dados de I/O cíclica no PROFINET não é reativa, mas sim síncrona, governada por dois tempos parametrizáveis no software de engenharia:

1. **Update Time (Tempo de Atualização):** Intervalo exato (geralmente parametrizado entre 1 ms, 2 ms, 4 ms até 512 ms) em que o dispositivo transmissor é obrigado a disparar um novo frame com os dados atualizados.
2. **Watchdog Factor (Multiplicador de Guarda):** Número inteiro (padrão de fábrica é 3) que define o limite tolerável de ciclos perdidos.

$$\text{Tempo de Retenção (Watchdog Time)} = \text{Update Time} \times \text{Watchdog Factor}$$

* **Mecanismo de Hardware:** Se o temporizador interno do receptor atingir o *Watchdog Time* sem receber o frame correspondente com o incremento correto do contador de ciclos, o hardware assume falha de conexão. O CLP interrompe a execução lógica, gera um alarme de sistema (OB86 no ecossistema Siemens) e os módulos de saída são forçados para o estado seguro pré-configurado (*Fail-Safe State*).

---

## Tópico 6: Descoberta e Inicialização: O Protocolo DCP

O **DCP (Discovery and Basic Configuration Protocol)** é o protocolo proprietário integrado à norma PROFINET destinado à parametrização inicial de dispositivos na Camada 2.

### 6.1 Operação por Nome de Dispositivo (*Device Name*)

Dispositivos PROFINET saem de fábrica sem endereço IP configurado. A identificação unívoca do hardware na planta é baseada em uma string alfanumérica gravada na memória não-volátil do dispositivo, denominada **PROFINET Device Name** (ex.: `et200sp-painel01`).

### 6.2 Sequência de Inicialização do Hardware

O protocolo opera através de frames de classe *Multicast* Ethernet utilizando o endereço de destino específico da organização PI (`01:0E:CF:00:00:00`). A sequência ocorre em três etapas:

1. **DCP Identify (Identificação):** O IO-Controller (CLP) envia um frame em *Multicast* para a rede contendo o *Device Name* que ele busca de acordo com o projeto de hardware.
2. **DCP Response (Resposta):** O dispositivo periférico que possuir o nome correspondente responde diretamente ao endereço MAC do CLP, enviando suas informações de hardware e endereço MAC fabril.
3. **DCP Set (Configuração):** O CLP envia um pacote direcionado (Unicast) gravando os parâmetros de rede IP (Endereço IP, Máscara de Sub-rede e Gateway) na memória temporária ou permanente do dispositivo com base no nome validado. Após esta etapa, o canal TCP/IP fica disponível para diagnósticos acíclicos.

---

## Tópico 7: Interoperabilidade: Arquivos GSDML

Para garantir que controladores de um fabricante gerenciem dispositivos periféricos de terceiros, a associação PI padronizou a descrição de hardware.

### 7.1 Estrutura de Dados XML

O **GSDML (General Station Description Markup Language)** é um arquivo estruturado baseado na linguagem XML. Ele descreve de forma matemática todas as propriedades técnicas e limitações físicas de um dispositivo de automação.

### 7.2 Conteúdo Técnico do Arquivo GSDML

O arquivo descreve obrigatoriamente:

* **Identificação de Perfil:** *Vendor ID* (Identificação do Fabricante) e *Device ID* (Identificação do Equipamento).
* **Mapeamento Modular:** Definição dos limites físicos de Slots e Subslots que o dispositivo suporta.
* **Estrutura do Payload:** Tamanho em bytes dos dados de entrada (inputs) e saída (outputs) de cada módulo.
* **Parâmetros de Configuração:** Faixas de operação de canais analógicos, filtros de hardware e limites de engenharia.
* **Dicionário de Diagnósticos:** Códigos hexadecimais de erro correspondentes a falhas físicas (ex.: curto-circuito, quebra de fio).

Durante a compilação do projeto no TIA Portal, o software lê o arquivo GSDML para calcular a distribuição exata dos bytes dentro do frame cíclico PROFINET RT.

---

## Tópico 8: Anatomia da Trama PROFINET RT

O frame PROFINET RT modifica a estrutura do frame Ethernet II padrão para otimizar a densidade de dados úteis e embutir informações de sincronismo e diagnóstico rápido.

### 8.1 Campos do Frame Byte a Byte

* **Preamble & SFD (8 Bytes):** Padrão físico Ethernet de sincronização de clock de rede (não contabilizado no cálculo de overhead de software).
* **Destination MAC Address (6 Bytes):** Endereço físico do dispositivo receptor.
* **Source MAC Address (6 Bytes):** Endereço físico do dispositivo transmissor.
* **VLAN Tag IEEE 802.1Q (4 Bytes):**
* *TPID (2 Bytes):* Fixo em `0x8100` indicando presença de tag.
* *TCI (2 Bytes):* Contém os 3 bits de prioridade (definidos em 6) e o ID da VLAN.


* **EtherType (2 Bytes):** Fixo em **`0x8892`**.
* **Frame ID (2 Bytes):** Identificador interno do bloco de dados cíclicos. Valores entre `0x8000` e `0xBBFF` determinam frames RT cíclicos de Classe 1.
* **IO Data / Payload (1 a 1440 Bytes):** Bloco contendo os valores reais das variáveis de processo (variáveis booleanas, inteiras, floats) dispostas sequencialmente conforme configurado nos slots e subslots.
* **APDU Status (Unidade de Dados de Aplicação - 4 Bytes no fechamento):**
* *Cycle Counter (2 Bytes):* Contador incremental sequencial gerado a cada envio para detecção de perda de pacotes pelo receptor.
* *Data Status (1 Byte):* Bitmask que informa o estado de operação do transmissor (se o CLP está em RUN ou STOP, se os dados são válidos ou se há falha local).
* *Transfer Status (1 Byte):* Fixo em `0x00` para transmissões cíclicas padrão.


* **FCS - Frame Check Sequence (4 Bytes):** Código CRC-32 para validação matemática contra corrupção de bits no cabo.

### 8.2 Análise de Overhead

Enquanto uma transmissão via socket TCP/IP convencional exige um overhead mínimo de 54 bytes de cabeçalhos de controle (Ethernet + IP + TCP) para enviar qualquer dado, o frame PROFINET RT fixa seu overhead estrutural de rede em **26 bytes** (MACs + VLAN + EtherType + Frame ID + APDU Status), minimizando a taxa de ocupação da largura de banda do barramento.

---

## Tópico 9: Perfis Especializados: PROFIsafe

O **PROFIsafe** é o perfil de segurança funcional normatizado pela **IEC 61784-3-3**, projetado para transmitir dados relacionados à proteção de vidas humanas (botões de emergência, cortinas de luz, travas de segurança) utilizando a mesma infraestrutura física do PROFINET RT.

### 9.1 O Princípio do *Black Channel* (Canal Negro)

O PROFIsafe baseia-se no conceito de que a rede de comunicação subjacente (cabos, switches, bridges) não possui confiabilidade de segurança biológica intrinsicamente garantida. Portanto, a camada de segurança funcional deve rodar de forma independente e isolada dentro do payload do frame de dados comum. O PROFINET RT atua apenas como um transportador cego (*Black Channel*).

### 9.2 O Mecanismo do Safety Trailer (Trailer de Segurança)

Para detectar e mitigar erros de rede como repetição de pacotes, perda, inserção incorreta, atrasos ou corrupção de dados, o PROFIsafe consome entre 4 a 6 bytes do payload útil do frame PROFINET RT, adicionando os seguintes mecanismos de controle diretamente controlados pela CPU de Segurança (F-CPU):

1. **Consecutive Number (Número Consecutivo):** Um contador interno de pacotes que reinicia em ciclos curtos. Garante que o receptor identifique se pacotes foram duplicados ou inseridos fora de ordem por falha de memória de switches intermediários.
2. **Timeout Monitoring (F-WDTime):** Um temporizador de segurança dedicado e independente do watchdog padrão do PROFINET. Se o pacote de segurança não for processado pela lógica de segurança interna dentro do tempo limite estrito (ex.: 20 ms), o sistema força a máquina para o desligamento seguro.
3. **Codificação por ID Único (F-Source-Address e F-Dest-Address):** Endereçamentos lógicos de segurança configurados via hardware (frequentemente via DIP-switches físicos nos módulos de I/O de segurança). Impede que um frame destinado a uma barreira de proteção acione incorretamente outro módulo homólogo.
4. **F-CRC (CRC de Segurança):** Um cálculo matemático polinomial CRC próprio executado unicamente sobre os dados de segurança e o trailer de proteção. Ele é independente do FCS de 4 bytes do frame Ethernet final. Se o cálculo matemático falhar na recepção da F-CPU, os dados de entrada são descartados e o sistema entra em estado de falha segura (*F-Fail*).

---

# Módulo 3: O Tráfego de TI na Indústria (A Via Comum — PROFINET NRT)

---

## Tópico 10: O Canal TCP/IP Padrão (NRT) — O Uso do EtherType `0x0800` na Mesma Infraestrutura Física

O tráfego de Não-Tempo Real (NRT - *Non-Real-Time*) no ecossistema PROFINET refere-se a toda comunicação baseada na pilha de protocolos de TI convencional que transita pela rede industrial sem privilégios determinísticos.

### 10.1 Mecanismo de Identificação e Filtro por Hardware

A coexistência do tráfego NRT e RT no mesmo meio físico é governada pelo campo *EtherType* do frame Ethernet II (norma **IEEE 802.3**).

* **O Código `0x0800`:** Quando um dispositivo ou switch recebe um frame cujo campo *EtherType* contém o valor hexadecimal `0x0800`, o hardware identifica-o estritamente como um pacote contendo um datagrama IPv4 (**RFC 791**). O código `0x0806` identifica pacotes ARP (*Address Resolution Protocol*).
* **Roteamento de Pilha Interna:** Ao contrário do tráfego RT (`0x8892`), o frame `0x0800` é direcionado para o controlador de interrupções do sistema operacional/firmware do processador do CLP. O pacote é processado sequencialmente pelas camadas de rede e transporte (pilha TCP/IP de software), consumindo ciclos de CPU padrão.

### 10.2 Priorização e Alocação de Banda

* **Quality of Service (QoS):** No cabeçalho **IEEE 802.1Q**, os frames NRT operam com o campo PCP (*Priority Code Point*) configurado em `0` (*Best Effort*) ou `1` (*Background*).
* **Gerenciamento de Fila nos Switches:** Em cenários de alta ocupação de rede, os switches dão vazão prioritária aos pacotes com tags de maior valor (como o RT com prioridade 6). Os pacotes `0x0800` permanecem nos buffers de entrada (*ingress buffers*) até que a janela temporal de tempo real termine.
* **Alocação de Banda Residual:** A norma **IEC 61784-2** determina que uma porcentagem da largura de banda total do canal Ethernet (geralmente entre 10% e 50%, dependendo da parametrização do ciclo) deve ser reservada para o tráfego assíncrono NRT, impedindo que a comunicação cíclica de I/O cause o bloqueio completo (*starvation*) dos serviços de TI.

---

## Tópico 11: Protocolos Hóspedes — Como o Modbus TCP e Servidores Web Rodam Dentro da Rede PROFINET

Como a infraestrutura física e de enlace do PROFINET baseia-se estritamente em Ethernet padrão, qualquer protocolo de aplicação que utilize a pilha TCP/IP pode trafegar em paralelo através do canal NRT.

### 11.1 Integração do Modbus TCP (IEC 61158 Type 8)

O Modbus TCP opera estritamente na Camada de Aplicação (Camada 7) e utiliza o transporte orientado à conexão TCP na **Porta Lógica 502**.

* **Encapsulamento Transparente:** O frame Modbus TCP que trafega em uma rede PROFINET mantém a seguinte estrutura de encapsulamento: `Ethernet Header (EtherType 0x0800) -> IP Header -> TCP Header (Port 502) -> MBAP Header -> Modbus PDU`.
* **Inexistência de Modificação:** O hardware PROFINET não altera, insere ou remove nenhum byte da estrutura do Modbus TCP. O CLP atua simultaneamente como um nó PROFINET (via hardware ASIC) e como um cliente/servidor Modbus TCP (via software na camada de aplicação do usuário).

### 11.2 Serviços de Hipertexto (HTTP/HTTPS)

Os CLPs industriais modernos integram servidores web nativos no firmware para interfaceamento local ou remoto.

* **Portas Utilizadas:** Porta TCP 80 para HTTP não encriptado e Porta TCP 443 para HTTPS encriptado via TLS (*Transport Layer Security*).
* **Aplicações Práticas Atendidas:**
* Atualização remota de firmware do hardware.
* Leitura de buffers de diagnóstico de erros (*System Diagnostics*).
* Visualização de tabelas de variáveis através de páginas customizadas criadas pelo usuário (*User-defined Web Pages*).



### 11.3 Protocolos Auxiliares de Gerenciamento

* **SNMP (Simple Network Management Protocol - RFC 1157):** Opera sobre UDP (portas 161 e 162). É uma exigência de conformidade do PROFINET para que softwares de gerenciamento de rede (NMS) interroguem objetos MIB (*Management Information Base*) nos switches e CLPs, coletando estatísticas de erro de porta, atenuação de cabos e carga de tráfego.

---

## Tópico 12: *Open User Communication* (OUC) — Abertura de Sockets e Comunicação Bilateral com TSEND e TRCV

A *Open User Communication* (OUC) é o conjunto de instruções nativas do firmware do controlador que permite ao programador estruturar fluxos de dados customizados através da abertura direta de soquetes de rede (*Sockets*), sem depender de protocolos proprietários de fabricantes.

### 12.1 Arquitetura de Sockets e Modos de Transporte

A parametrização de uma conexão OUC exige a definição de uma estrutura de dados de conexão (ex.: tipo de dados `TCON_IP_v4` no ambiente Siemens), contendo os seguintes parâmetros de rede:

* Endereço IP do dispositivo local e do parceiro remoto.
* Porta lógica local e remota (faixa utilizável de livre escolha entre 1025 e 65535).
* Seleção do protocolo da Camada de Transporte:

#### Opção A: TCP (Transmission Control Protocol - RFC 793)

* **Características:** Protocolo orientado à conexão. Exige o procedimento físico de *Three-Way Handshake* (sinais lógicos SYN, SYN-ACK, ACK) antes do início da transmissão de dados.
* **Integridade:** Garante a entrega dos bytes na ordem correta, controle de congestionamento e retransmissão automática por hardware em caso de perda de pacotes. É um fluxo de dados contínuo (*stream-oriented*).

#### Opção B: UDP (User Datagram Protocol - RFC 768)

* **Características:** Protocolo não orientado à conexão. Baseado no envio de datagramas isolados (*packet-oriented*).
* **Integridade:** Não há checagem de recebimento, numeração de pacotes ou retransmissão. Possui menor overhead estrutural e menor tempo de processamento se comparado ao TCP.

### 12.2 Blocos de Instrução de Código

A execução da comunicação OUC é assíncrona em relação ao ciclo de scan do CLP e depende de blocos funcionais específicos:

* **TCON:** Executa a abertura do Socket de rede. Um dispositivo é configurado como *Active Connection Establishment* (Cliente, que inicia o disparo do pacote SYN) e o outro como *Passive Connection Establishment* (Servidor, que abre a porta em modo de escuta *Listen*).
* **TDISCON:** Encerra a conexão lógica e libera os recursos de memória da interface de rede do CLP.
* **TSEND / TSEND_C:** Transmite um bloco de dados linear alocado na memória do CLP (ex.: uma matriz de bytes, um bloco de dados - DB). O sufixo `_C` (*Compact*) indica que o bloco gerencia internamente as funções de conexão e desconexão de forma automática.
* **TRCV / TRCV_C:** Monitora o buffer de recepção da interface de rede e copia os dados brutos recebidos para a área de memória parametrizada no programa do usuário. O bloco exige a definição do modo de recepção (comprimento de dados fixo ou terminação por caractere delimitador).
  
---

# Módulo 4: O Ecossistema Siemens e Acoplamento de CLPs

---

## Tópico 13: O Protocolo S7 Communication (S7comm e S7comm+)

O S7comm é o protocolo proprietário da camada de aplicação (Camada 7 do Modelo OSI) desenvolvido pela Siemens para a comunicação e engenharia de seus controladores lógicos programáveis.

### 13.1 S7comm Clássico

Utilizado nas famílias legadas S7-300 e S7-400. Suas características técnicas são:

* **Dependência de Arquitetura:** Originalmente projetado para redes seriais (MPI e PROFIBUS), foi adaptado para redes Ethernet através do encapsulamento em soluções de transporte abertas.
* **Vulnerabilidade de Segurança:** Os dados trafegam inteiramente em texto limpo (*plaintext*). Não implementa mecanismos de criptografia, autenticação de origem ou assinaturas digitais.
* **Vulnerabilidades Conhecidas:** Permite ataques de injeção de pacotes e espelhamento de comandos (*Replay Attacks*). A captura do tráfego via analisador de rede expõe diretamente a estrutura de dados (DBs, Marks) e o código-fonte das funções carregadas.

### 13.2 S7comm-Plus (S7comm+)

Introduzido com as famílias de controladores S7-1200 e S7-1500 e o software TIA Portal.

* **Mecanismos de Proteção:** Implementa segurança na camada de aplicação através de algoritmos criptográficos baseados em chaves simétricas e assimétricas.
* **Integridade de Sessão:** Cada sessão de comunicação entre o software de engenharia (ou HMI) e o CLP gera um identificador dinâmico (*Challenge-Response Session ID*). Pacotes capturados e retransmitidos posteriormente são descartados pelo firmware do CLP (proteção *Anti-Replay*).
* **Criptografia do Payload:** O cabeçalho e os dados úteis das variáveis manipuladas passam por um processo de hashing e cifragem. Isso impede a leitura passiva dos valores das tags de processo e bloqueia a modificação não autorizada de blocos de lógica (OBs, FCs, FBs) em trânsito pela rede.

---

## Tópico 14: A Ponte de Compatibilidade — ISO on TCP (RFC 1006)

Para que o protocolo de aplicação S7comm (baseado no conceito de blocos de mensagens delimitados) trafegue sobre redes de dados modernas que utilizam o protocolo TCP, é necessária a implementação da especificação **RFC 1006** (ISO on TCP).

### 14.1 O Problema da Fragmentação do TCP

O protocolo TCP (**RFC 793**) é orientado ao fluxo contínuo de bytes (*Stream-oriented*). Ele não possui delimitadores de início e fim de mensagem em sua camada de transporte. O TCP segmenta os dados da aplicação de acordo com a MTU (*Maximum Transmission Unit*) da rede física.

Os sistemas de automação baseados no padrão ISO/OSI necessitam de comunicações baseadas em mensagens estruturadas e blocos fechados denominados PDUs (*Protocol Data Units*). O receptor precisa saber exatamente onde termina uma instrução para processá-la.

### 14.2 Estrutura de Encapsulamento da RFC 1006

A RFC 1006 introduz duas subcamadas entre o TCP e o S7comm para simular os serviços de transporte orientados à conexão ISO (ISO 8073):

#### 1. Cabeçalho TPKT (Transport Service on top of TCP)

Possui tamanho fixo de **4 bytes** e precede imediatamente qualquer bloco de dados. Sua estrutura byte a byte é:

* **Byte 0:** Versão do protocolo (Fixo em `0x03`).
* **Byte 1:** Reservado (Fixo em `0x00`).
* **Bytes 2 e 3:** Comprimento total do pacote (Composto por 16 bits, contabiliza o tamanho do próprio TPKT + COTP + S7comm + Payload).

#### 2. Cabeçalho COTP (Connection Oriented Transport Protocol - ISO 8073)

Identifica o tipo de PDU de transporte (TPDU). Varia de 3 a 7 bytes.

* Define os parâmetros de conexão inicial (*Connection Request* e *Connection Confirm*) e gerencia a fragmentação de blocos S7comm cujo tamanho excede a capacidade máxima de PDU configurada no CLP (*PDU Size Negotiation*).

A pilha final de transmissão na **Porta TCP 102** estrutura-se como: `Ethernet Header -> IP Header -> TCP Header (Port 102) -> TPKT Header -> COTP Header -> S7comm -> Payload`.

---

## Tópico 15: Comunicação Unilateral PLC-to-PLC — Instruções PUT e GET

As instruções PUT e GET utilizam serviços baseados no protocolo S7comm clássico para realizar a transferência de dados entre dois controladores sem a necessidade de sincronismo de código do lado receptor.

### 15.1 Mecanismo de Operação

* **Unilateralidade:** Toda a configuração da conexão e a execução lógica do bloco ocorrem exclusivamente no CLP Cliente. O CLP Servidor atua de forma puramente passiva.
* **Instrução GET (S7 Read):** O CLP Cliente envia uma requisição especificando a área de memória exata do CLP Servidor (ex.: `DB10.DBX0.0`, comprimento de 50 bytes). O firmware do CLP Servidor processa a requisição e devolve os dados.
* **Instrução PUT (S7 Write):** O CLP Cliente envia um frame contendo dados locais e indica o endereço de destino na memória do CLP Servidor, sobrescrevendo a área remota.

### 15.2 Características de Execução e Riscos de Segurança

* **Independência de Software:** A leitura ou escrita na memória do CLP Servidor ocorre diretamente no nível do firmware da interface de rede do controlador. Não há necessidade de programar nenhum bloco de código ou lógica de recepção no programa do CLP Servidor. O programa do usuário do servidor não é notificado da alteração dos dados.
* **Vulnerabilidade de Segurança por Acesso Direto:** Como o processamento ignora a lógica do usuário, qualquer dispositivo conectado à rede que envie um frame S7comm parametrizado na porta TCP 102 pode ler ou modificar variáveis críticas do CLP Servidor.
* **Mecanismo de Bloqueio (Hardware Properties):** Nas CPUs modernas S7-1200 e S7-1500, o acesso unilateral vem desabilitado por padrão de fábrica. Para permitir a operação de PUT e GET, o engenheiro deve marcar explicitamente a opção *"Permit access with PUT/GET communication from remote partner"* nas propriedades de segurança do hardware no TIA Portal.

---

## Tópico 16: Comunicação Determinística PLC-to-PLC — Configuração de I-Device

O recurso **I-Device (Intelligent Device)** permite o acoplamento determinístico de dados entre dois ou mais CLPs operando diretamente na Camada 2, eliminando o uso de blocos de função de comunicação no programa do usuário.

### 16.1 Mecanismo de Funcionamento

A configuração transforma a CPU de um CLP em um periférico descentralizado (remota de I/O virtual) para outro CLP.

* **IO-Controller:** O CLP mestre da rede.
* **I-Device / IO-Device:** O CLP inteligente subordinado. Do ponto de vista da rede PROFINET, ele passa a se comportar como um módulo de I/O padrão.

### 16.2 Áreas de Transferência (*Transfer Areas*)

A troca de dados é realizada mapeando buffers de memória diretamente na imagem do processo (*Process Image Inputs/Outputs*) de ambos os controladores.

* O engenheiro configura áreas unidirecionais de entrada e saída de tamanhos fixos (ex.: 32 bytes de *Inputs* e 32 bytes de *Outputs*).
* Uma escrita na área de saídas virtuais (`QW`) do CLP I-Device é transmitida instantaneamente pelo hardware da rede e surge diretamente na área de entradas virtuais (`IW`) do CLP IO-Controller no ciclo de atualização subsequente.

### 16.3 Vantagens Técnicas face aos Blocos de Comunicação

* **Determinismo de Barramento:** A comunicação ocorre via **PROFINET RT (EtherType `0x8892`)**. Os dados compartilham da mesma prioridade de hardware de leitura de sensores críticos (QoS Prioridade 6).
* **Latência Sub-milissegundo:** Dispensa a execução de lógicas assíncronas em blocos de software (como `TSEND` ou `PUT`). A velocidade de transferência é idêntica ao *Update Time* da rede, permitindo sincronismo de dados entre máquinas em tempos inferiores a 2 milissegundos.

---

## Tópico 17: Segregação de Redes — Processadores de Comunicação (Módulos CP) vs. Portas Integradas

A arquitetura de hardware escolhida para o CLP determina a separação galvânica e lógica entre os níveis de controle de processo (TA) e redes corporativas (TI).

### 17.1 Portas Integradas à CPU (*Onboard Ports*)

As interfaces de rede físicas integradas diretamente no bloco da CPU compartilham do mesmo barramento interno de processamento e contexto de roteamento.

* Se múltiplas portas físicas integradas existirem na mesma CPU, elas frequentemente operam como um switch interno (*Switch Mode*). Todo tráfego que atinge uma porta trafega pelo barramento interno do processador principal do CLP.
* **Risco de Carga de Rede:** Um ataque de negação de serviço (DoS) ou uma tempestade de *broadcast* na rede corporativa conectada a essa porta consome diretamente os ciclos de clock da CPU principal do CLP, podendo causar falhas de processamento e paradas no controle da máquina.

### 17.2 Processadores de Comunicação (Módulos CP / CM)

Módulos CPs (ex.: CP 1543-1) são placas de expansão de hardware instaladas no rack do CLP que possuem processadores, memórias e pilhas de rede totalmente independentes da CPU principal.

* **Isolamento de Redes:** O tráfego de dados da rede externa (TI) morre fisicamente no hardware do módulo CP. A CPU do CLP realiza apenas a troca de variáveis limpas através do barramento do backplane do rack.
* **Funções Avançadas de Segurança Industrial:**
* **Firewall Integrado:** Módulos CP industriais executam filtros baseados em inspeção de pacotes (SPI), bloqueando tráfegos de IP e portas que não correspondam estritamente ao projeto de automação.
* **Proteção contra Tempestades de Redundância:** Implementam limitadores de hardware para tráfego de *broadcast* e *multicast*, isolando o núcleo de processamento do CLP de instabilidades geradas por falhas na rede de TI.



---

---

# Módulo 5: Diagnóstico e Ferramentas Práticas

---

## Tópico 18: Análise de Rede — Captura e Dissecação de Pacotes no Wireshark

O diagnóstico avançado de falhas, intermitências e gargalos em redes industriais PROFINET exige a análise direta de frames binários capturados através de espelhamento de porta (*Port Mirroring / SPAN*) em switches gerenciáveis.

### 18.1 Dissecação de Frames PROFINET RT (Tempo Real)

* **Filtro de Exibição no Wireshark:** `pn_rt` ou pelo EtherType direto `eth.type == 0x8892`.

#### Campos Críticos a Inspecionar para Diagnóstico:

1. **Frame ID:** Verifica a classe do serviço. Valores entre `0x8000` e `0xBBFF` confirmam tráfego cíclico em tempo real de Classe 1.
2. **Cycle Counter:** Analisa o incremento sequencial de cada frame. Saltos na numeração (ex.: frame anterior `4500` e frame atual `4502`) indicam perda física de pacotes (*Packet Drop*) devido a ruído eletromagnético ou switches saturados.
3. **Data Status (1 Byte):** Campo binário de estado. O bit mais significativo (**Bit 2 - Provider State**) indica se o emissor está em modo funcional ativo (`1` para RUN) ou parado (`0` para STOP). O **Bit 0 (State)** valida se os valores contidos no payload são confiáveis (`1`) ou se o módulo remoto gerou uma falha de hardware local (`0`).

### 18.2 Dissecação de Frames PROFINET NRT (TCP/IP)

* **Filtros de Exibição no Wireshark:** `ip.proto == 6` (para TCP), `tcp.port == 102` (para S7comm) ou `tcp.port == 502` (para Modbus TCP).

#### Campos Críticos a Inspecionar para Diagnóstico:

1. **EtherType:** Deve constar obrigatoriamente como **`0x0800`** (IPv4).
2. **Análise de Conexão TCP (Flags):** Identificação de instabilidade de comunicação via blocos TSEND/TRCV ou S7comm através do monitoramento de flags TCP. A ocorrência frequente de pacotes com as flags `RST` (Reset) ou sequências repetidas de `Retransmission` aponta para falhas na pilha de software ou quedas de conexão lógica por estouro de timeout do socket.
3. **Análise ISO on TCP (TPKT):** Expanda a camada superior ao TCP. Verifique se o primeiro byte do TPKT inicia com `0x03` e confira se o campo *Length* casa exatamente com o número de bytes trafegados.

### 18.3 Dissecação de Frames PROFINET DCP (Descoberta de Dispositivos)

* **Filtro de Exibição no Wireshark:** `pn_dcp`.

#### Campos Críticos a Inspecionar para Diagnóstico:

1. **Endereço MAC de Destino:** Deve constar obrigatoriamente o endereço de multicast global da PI: **`01:0e:cf:00:00:00`**.
2. **DCP Service Type:** Identifica a fase do handshake.
* `Identify Request (0x05):` CLP varrendo a rede em busca do nome do dispositivo.
* `Identify Response (0x01):` Dispositivo respondendo com suas credenciais de hardware.
* `Set Request (0x04):` Comando do CLP gravando as configurações de IP baseadas no nome validado.


3. **DCP Block Option:** Identifica os parâmetros transmitidos. Inspecione os sub-blocos `Device Properties / Name of Station` para depurar problemas de digitação de nomes alfanuméricos no TIA Portal que impedem a inicialização correta da comunicação de hardware em campo.Qu