Compreendido. Aqui está o roteiro técnico e direto, do zero, focado exclusivamente nos cliques e configurações dentro do TIA Portal para estabelecer a comunicação PROFINET RT entre os dois CLPs físicos e capturar os dados.
Fase 1: Preparação do Projeto e Topologia
Conexão Física: Conecte o CLP 1, o CLP 2 e o Computador a um mesmo Switch de rede.
Criação do Projeto: Abra o TIA Portal, crie um novo projeto e clique em Add new device.
Adição dos Controladores: * Adicione o modelo exato do seu primeiro CLP S7-1500. Renomeie-o para CLP_Controlador.
Adicione o modelo exato do seu segundo CLP S7-1500. Renomeie-o para CLP_IDevice.
Endereçamento IP:
Vá em Device configuration do CLP_Controlador. Clique na porta verde (PROFINET). Em Properties > Ethernet addresses, defina o IP (ex: 192.168.0.1). Adicione uma nova sub-rede clicando em Add new subnet (será criada a PN/IE_1).
Vá no CLP_IDevice, clique na porta verde, defina o IP (ex: 192.168.0.2) e conecte-o à mesma sub-rede PN/IE_1.
Fase 2: Configurando o CLP 2 como I-Device (Escravo)
Vá para a tela Device configuration do seu CLP_IDevice.
Clique na interface PROFINET (o pequeno quadrado verde no desenho do CLP).
Na janela inferior, vá em Properties > General > Operating mode.
Marque a caixa de seleção "IO device".
Logo abaixo, no campo Assigned IO controller, abra a lista suspensa e selecione "CLP_Controlador.PROFINET interface_1".
(Nota: Ao fazer isso, o TIA Portal cria automaticamente a relação mestre-escravo no Network View).
Criando as Áreas de Transferência (Obrigatório):
Ainda dentro do menu Operating mode, role a barra lateral um pouco para baixo e clique em Transfer areas.
Clique na primeira linha vazia da tabela (<Add new>).
O TIA Portal criará automaticamente a área Transfer area_1. Ele mapeará as saídas (Q) do Controlador para as entradas (I) do I-Device (Ex: Os bytes QW2 do mestre vão escrever nos bytes IW2 do escravo).
Fase 3: O "Assign Device Name" (Protocolo DCP)
Esta etapa é crucial porque dispositivos PROFINET I-Device não iniciam a comunicação pelo IP, mas sim pelo "Nome de Dispositivo" atrelado ao MAC Address.
Prepare o Wireshark (A Prática em si): Antes de clicar no TIA Portal, abra o Wireshark no PC, selecione sua placa de rede Ethernet e aplique o filtro: pn_dcp.
No TIA Portal, vá para a tela Network view. Você verá os dois CLPs unidos por uma linha verde tracejada ou contínua.
Clique com o botão direito sobre a linha verde da rede (ou clique com o botão direito no CLP_IDevice) e selecione Assign device name.
Uma nova janela se abrirá:
No campo PROFINET device name, verifique se o nome do seu escravo está selecionado (geralmente será clp_idevice).
Em PG/PC interface, garanta que a sua placa de rede física está selecionada.
Clique no botão Update list.
O Grito na Rede: Neste momento, olhe para o Wireshark. Você verá pacotes de Broadcast/Multicast (Identify Request). É o TIA Portal procurando os equipamentos físicos pelo MAC.
A Atribuição: O CLP físico do laboratório aparecerá na lista da janela do TIA Portal, com seu endereço MAC de fábrica. Selecione-o na lista e clique no botão Assign name. O status mudará para "OK".
Fase 4: Compilação e Download
Como as arquiteturas de hardware mudaram drasticamente (um virou mestre, o outro virou remota), você deve carregar o hardware do zero.
Clique com o botão direito no CLP_Controlador na árvore de projeto > Download to device > Hardware and Software (only changes). Siga o assistente, mande parar (Stop) se necessário, carregue e coloque em Run.
Repita o mesmo processo: clique com o botão direito no CLP_IDevice > Download to device > Hardware and Software. Carregue e coloque em Run.
Olhe fisicamente para os CLPs. O LED "ERROR" ou "MAINT" não deve estar piscando. Os LEDs devem estar verdes, indicando que a malha PROFINET subiu e está saudável.
Fase 5: Validação da Prática com Wireshark (PROFINET RT)
Retorne ao Wireshark e pare a captura anterior.
Altere o filtro de pn_dcp para pn_rt e inicie uma nova captura.
Você verá uma enxurrada de pacotes na tela (geralmente a cada 2 milissegundos).
Análise: Clique em qualquer pacote. Você notará que na janela de dissecção de protocolos do Wireshark não existe a camada de IP (IPv4). O protocolo pula do Ethernet II (com EtherType 0x8892) direto para o PROFINET IO Real-Time.
(Para provar a comunicação lógica: Você pode ir no CLP_Controlador, criar uma "Watch Table", forçar um valor no endereço QW2 e abrir uma "Watch Table" no CLP_IDevice para ver o valor chegando instantaneamente no endereço IW2 através da rede que vocês acabaram de mapear e interceptar).

Gostei da aula, mas quero adicionar conteúdo teórico com base nela
Excelente iniciativa. Conectar a configuração prática dos softwares com a teoria de redes é o que transforma uma aula de "apertar botões" em uma verdadeira aula de engenharia.

Como a cadeira é de Introdução às Redes de Comunicação, o foco teórico perfeito para amarrar essa prática é a desconstrução do Modelo OSI. O PROFINET é o exemplo perfeito para mostrar aos alunos por que as regras da TI tradicional às vezes precisam ser "quebradas" ou adaptadas na indústria.

Aqui está um roteiro teórico espelhado na sua prática, que você pode apresentar no quadro ou em slides antes ou durante a execução:

Teoria da Fase 1 e 2: O Modelo OSI e o Duplo Papel da Rede
Quando os alunos estão definindo IPs e conectando a topologia.

Conceito Teórico: Pilha TCP/IP vs. Pilha PROFINET.

A Pergunta para a turma: "Se o PROFINET de tempo real não usa endereço IP, por que o TIA Portal nos obriga a configurar IPs na mesma sub-rede (ex: 192.168.0.x)?"

A Explicação: Uma rede industrial moderna roda duas "vias" simultâneas no mesmo cabo.

O Canal Acíclico (TI / Best Effort): Usa as Camadas 3 (Rede/IP) e 4 (Transporte/TCP-UDP). É por este canal que o TIA Portal faz o download do programa, que o CLP envia dados para um servidor web, ou que se faz o diagnóstico da rede. É lento e sujeito a atrasos (Jitter).

O Canal Cíclico (TA / Real-Time): Pula as camadas 3 e 4. Vai direto da Camada 2 (Enlace/MAC) para a Camada 7 (Aplicação). É o tráfego de controle crítico.

Conceito Teórico: Domínio de Broadcast.

Ao criar a sub-rede PN/IE_1, os alunos estão definindo um domínio de colisão/broadcast onde todos os pacotes Multicast (como o DCP) poderão navegar livremente através dos switches locais.

Teoria da Fase 3: Protocolo DCP e Resolução de Endereços
Quando os alunos usam o "Assign Device Name" e capturam pacotes no Wireshark.

Conceito Teórico: Resolução de Endereços e Limitações do DHCP.

A Pergunta para a turma: "Por que não usamos o bom e velho DHCP para dar IPs automáticos às remotas, como fazemos com nossos celulares no Wi-Fi?"

A Explicação: Na indústria, o tempo de reparo (MTTR) é crítico. Se um módulo de I/O queima às 3 da manhã, o técnico de manutenção troca a peça física. O DHCP demoraria para negociar (Discover, Offer, Request, Acknowledge) ou poderia dar um IP diferente. O PROFINET usa o DCP (Discovery and Configuration Protocol). O Controlador guarda a topologia. Ao ver um novo MAC address na porta onde a peça queimou, ele injeta instantaneamente o "Device Name" original na peça nova.

Conceito Teórico: Tipos de Transmissão (Camada 2).

Mostrar no Wireshark o endereço MAC de destino 01:0E:CF:00:00:00.

Explicar a diferença: Unicast (Um para Um - Comunicação normal), Broadcast (Um para Todos - Inunda a rede), e Multicast (Um para um Grupo Específico). O DCP é Multicast, projetado para que apenas as placas de rede da Siemens "escutem", poupando o processamento dos PCs conectados no mesmo switch.

Teoria da Fase 4: Plano de Controle vs. Plano de Dados
Quando os alunos fazem o download e a máquina entra em RUN.

Conceito Teórico: Arquiteturas de Roteamento.

Durante o Download to device, os alunos estão usando o Plano de Controle/Gerenciamento. Os pacotes viajam pelo IP, são pesados e garantem que a máquina saiba o que fazer.

Quando entra em RUN, ativa-se o Plano de Dados. A lógica de transferência (Transfer area_1 -> QW2 para IW2) começa a fluir sem a intervenção do TCP/IP.

Teoria da Fase 5: O Core do Tempo Real (PROFINET RT)
Quando a turma filtra pn_rt e analisa o frame.

Conceito Teórico: Determinismo vs. Best Effort.

A Pergunta para a turma: "Por que pular a camada de IP faz o PROFINET ser mais rápido?"

A Explicação: Uma rede tradicional Ethernet (CSMA/CD) foi feita para não perder dados, não importando quanto tempo demore (Best Effort ou Melhor Esforço). Redes industriais precisam de Determinismo: a garantia matemática de que o dado sairá do CLP 1 e chegará ao CLP 2 em exatos 2.0 ms.

Conceito Teórico: Anatomia do Frame e Redução de Overhead.

Desenhe no quadro a diferença do encapsulamento (Overhead):

Pacote TI (Ping/Web): Ethernet Header (14 bytes) + IP Header (20 bytes) + TCP/UDP Header (20 bytes) + Dados + FCS.

Pacote PROFINET RT: Ethernet Header (14 bytes) + Dados (variáveis do CLP) + FCS.

Mostre que, ao remover o IP e o TCP, o processador do CLP não precisa gastar tempo calculando rotas, checando portas lógicas ou ordenando pacotes. O pacote chega na placa de rede (MAC) e vai direto para a memória do CLP (IW2).

Conceito Teórico: QoS (Quality of Service) e VLAN Tagging (IEEE 802.1Q).

Peça aos alunos para expandirem o cabeçalho Ethernet II no Wireshark de um pacote pn_rt. Eles verão um campo chamado 802.1Q Virtual LAN.

A teoria aqui é o QoS. O PROFINET insere uma tag de prioridade Priority: 6 no pacote de Camada 2. Isso garante que, se houver tráfego pesado no switch do laboratório (alguém baixando um arquivo via TCP), o switch dará passagem VIP obrigatória para o pacote do CLP, garantindo o determinismo.

Dica de Abordagem para a Monitoria
Você pode amarrar a aula da seguinte forma:

Exposição Breve (15 min): Mostra os slides com o conceito do Modelo OSI e os diferentes tipos de tráfego.

Mão na Massa (Prática que estruturamos): Eles configuram, rodam o Wireshark e ativam os CLPs.

Fechamento Teórico (10 min): Com o Wireshark rodando na tela de cada um, você faz o "debriefing", apontando na tela deles: "Estão vendo que não tem IP aqui? Essa é a prova do determinismo que falamos no início da aula."