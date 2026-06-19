# Guia Prático Detalhado — Node-RED
## Redes Industriais · Engenharia de Controle e Automação

> **Como usar este guia:** Cada passo está descrito com o que clicar, onde clicar e o que aquela ação significa. Siga em ordem. Não pule etapas.

---

# PARTE 1 — INSTALAÇÃO E PRIMEIRO ACESSO

## 1.1 Instalando o Node.js

O Node-RED roda sobre o **Node.js**, que é o motor JavaScript fora do navegador. Sem ele, o Node-RED não funciona.

**No Windows:**
1. Abra o navegador e acesse: `https://nodejs.org`
2. Clique no botão verde escrito **"LTS"** (Long Term Support — versão estável)
3. Baixe e execute o instalador `.msi`
4. Na tela de instalação, clique em **Next → Next → Install → Finish**
5. Deixe todas as opções padrão marcadas

**Verificando se instalou:**
1. Pressione `Win + R`, digite `cmd` e pressione `Enter`
2. No terminal que abrir, digite:
   ```
   node --version
   ```
3. Se aparecer algo como `v18.17.0`, está instalado corretamente

---

## 1.2 Instalando o Node-RED

Com o terminal ainda aberto, digite o comando abaixo e pressione `Enter`:

```bash
npm install -g --unsafe-perm node-red
```

**O que cada parte desse comando significa:**
- `npm` → gerenciador de pacotes do Node.js (instalado junto com o Node)
- `install` → instala um pacote
- `-g` → instala de forma **global** (disponível em qualquer pasta do computador)
- `--unsafe-perm` → necessário em alguns sistemas para evitar erros de permissão
- `node-red` → o nome do pacote que estamos instalando

**O que vai acontecer na tela:**
- Você verá várias linhas passando com `npm warn`, `added X packages`
- Isso é **normal**. Aguarde até voltar ao cursor piscando
- O processo pode levar de 1 a 3 minutos

---

## 1.3 Iniciando o Node-RED

No terminal, digite:

```bash
node-red
```

**O que vai aparecer:**
```
Welcome to Node-RED
===================
...
[info] Server now running at http://127.0.0.1:1880/
[info] Starting flows
[info] Started flows
```

Quando ver **"Started flows"**, o Node-RED está rodando

> **Não feche o terminal enquanto estiver usando o Node-RED.** Fechar o terminal encerra o servidor.

---

## 1.4 Acessando a Interface

1. Abra seu navegador (Chrome ou Firefox, preferencialmente)
2. Na barra de endereços, digite exatamente:
   ```
   http://localhost:1880
   ```
3. Pressione `Enter`

Você verá a interface do Node-RED carregar com um fundo escuro e uma área de trabalho vazia.

> `localhost` significa "este próprio computador". A porta `1880` é onde o Node-RED está "escutando".

---

# PARTE 2 — CONHECENDO A INTERFACE

Ao entrar no Node-RED, você verá 4 regiões. Vamos identificar cada uma:

```
┌─────────────────────────────────────────────────────────────┐
│  🔴 Node-RED    [Deploy ▼]          ☰ menu             [?] │  ← BARRA SUPERIOR
├──────────┬──────────────────────────────────┬───────────────┤
│          │                                  │               │
│  PALETA  │          CANVAS                  │  PAINEL       │
│  DE NÓS  │     (área de trabalho)           │  LATERAL      │
│          │                                  │               │
│ [inject] │                                  │     Info      │
│ [debug]  │                                  │     Debug     │
│ [func..] │                                  │     Config    │
│          │                                  │               │
└──────────┴──────────────────────────────────┴───────────────┘
```

---

## 2.1 A Barra Superior

| Elemento | O que é | Para que serve |
|----------|---------|---------------|
| **Node-RED** (logo vermelho) | Logotipo/nome | Clique para ir à página inicial |
| **Deploy** (botão vermelho) | Botão mais importante | **Publica e ativa** o fluxo que você montou |
| **▼** (ao lado do Deploy) | Seta de opções | Permite escolher tipo de deploy (Deploy completo, fluxo atual, nós modificados) |
| **☰** (três barras) | Menu hambúrguer | Acesso a importar/exportar fluxos, configurações, paleta de nós |
| **?** | Ajuda | Documentação contextual |

> **Regra de ouro:** Nada funciona até você clicar em **Deploy**. Montar o fluxo no canvas é apenas "desenhar". O Deploy é o que "liga" o circuito.

---

## 2.2 A Paleta de Nós (lado esquerdo)

É a "caixa de ferramentas". Contém todos os nós disponíveis organizados em categorias.

**Para encontrar um nó:**
- Role a lista com o scroll do mouse, **OU**
- Use a barra de busca no topo da paleta — **recomendado para iniciantes**

**Categorias principais:**
- **common** → `inject`, `debug`, `complete`, `catch`, `status`, `link in`, `link out`
- **function** → `function`, `switch`, `change`, `range`, `template`, `delay`
- **network** → `mqtt in`, `mqtt out`, `http in`, `http out`, `websocket`
- **sequence** → `split`, `join`, `sort`, `batch`
- **storage** → `file in`, `file`, `watch`

---

## 2.3 O Canvas (área central)

É onde você **monta os fluxos** arrastando nós da paleta e conectando-os com fios.

**Controles do canvas:**
| Ação | Como fazer |
|------|-----------|
| Mover o canvas | Clique e arraste em área vazia |
| Zoom in/out | Scroll do mouse, ou `Ctrl +` / `Ctrl -` |
| Resetar zoom | `Ctrl + Shift + 0` |
| Selecionar tudo | `Ctrl + A` |
| Desfazer | `Ctrl + Z` |
| Copiar nó | Selecione + `Ctrl + C`, depois `Ctrl + V` |
| Deletar nó | Selecione o nó + tecla `Delete` ou `Backspace` |

**Abas de fluxo:**  
Na parte inferior do canvas você vê abas (tipo abas do Excel). Cada aba é um **fluxo separado**. Você pode criar quantas quiser clicando no **`+`** ao lado das abas.

---

## 2.4 O Painel Lateral (lado direito)

Tem 3 abas:

**Info (Informações):**
- Quando você clica em um nó, aqui aparece a **documentação daquele nó**
- Explica o que ele faz, quais propriedades aceita e exemplos de uso
- Leia sempre antes de usar um nó novo

**Debug:**
- Aqui aparecem as mensagens dos nós `debug` que você colocar no fluxo
- É o seu **"console"** para ver o que está trafegando no fluxo
- Tem um botão no topo para limpar as mensagens antigas

**Configuration Nodes:**
- Lista nós de configuração compartilhados (ex: configuração do broker MQTT usada por vários nós)

---

# PARTE 3 — EXERCÍCIO 1: "Hello World"

## Objetivo
Criar o fluxo mais simples possível: disparar uma mensagem e ver o resultado.

**Conceito aprendido:** Nós, fios, mensagens e deploy

---

## Passo 1 — Arrastar o nó `inject`

1. Na paleta esquerda, procure o nó chamado **`inject`** (está na categoria *common* ou use a busca)
2. **Clique e segure** o mouse sobre o nó `inject`
3. **Arraste** para o centro do canvas e **solte**

**O que é o nó `inject`?**  
É o nó de entrada mais básico do Node-RED. Ele "injeta" (envia) uma mensagem para o próximo nó, podendo ser acionado manualmente (clicando em seu botão) ou automaticamente em intervalos de tempo configurados.

Você verá um nó cinza com um **pequeno quadrado azul à esquerda** (ponto de entrada, que o `inject` não usa) e **um pequeno quadrado à direita** (ponto de saída).

---

## Passo 2 — Arrastar o nó `debug`

1. Na paleta, procure o nó **`debug`** (também em *common*)
2. Arraste para o canvas e posicione **à direita do nó `inject`**

**O que é o nó `debug`?**  
É o nó que exibe o conteúdo da mensagem recebida no painel de Debug (lado direito). Ele não altera o dado recebido, apenas o exibe para fins de diagnóstico. É indispensável para testar, validar e depurar os fluxos.

---

## Passo 3 — Conectar os nós com um fio

1. Passe o mouse sobre o **quadrado cinza à direita** do nó `inject`
2. O cursor vai mudar para uma **cruz (+)**
3. **Clique e arraste** a partir desse ponto
4. Veja que um **fio cinza** começa a se formar
5. Arraste até o **quadrado cinza à esquerda** do nó `debug`
6. Quando o quadrado ficar destacado (laranja), **solte o mouse**

Você verá um fio ligando os dois nós.

**O que esse fio representa?**  
O fio representa o **canal de comunicação** entre os nós. Qualquer dado (mensagem) que sai do nó de origem percorre essa conexão para chegar ao nó de destino.

> Se errar a conexão: clique no fio para selecioná-lo (ele fica laranja) e pressione `Delete` para apagar.

---

## Passo 4 — Fazer o Deploy

1. Olhe para o canto superior direito
2. Clique no botão vermelho **"Deploy"**
3. Aparecerá uma notificação verde no topo: **"Successfully deployed"**

**O que aconteceu?**  
O Node-RED compilou seu fluxo e o colocou em execução. Antes do Deploy, o fluxo existe apenas como um "rascunho" visual. Após o Deploy, ele está **ativo e monitorando** inputs.

> Sempre que modificar qualquer coisa no canvas, você precisa fazer Deploy novamente para as mudanças entrarem em vigor. O botão ficará **cinza com uma bolinha vermelha** quando houver mudanças não deployadas.

---

## Passo 5 — Disparar a mensagem

1. Olhe para o nó `inject` no canvas
2. À **esquerda** do nó há um pequeno **botão quadrado cinza**
3. Clique nesse botão

No painel de **Debug** (lado direito), você verá uma linha aparecer com a mensagem enviada. O padrão é `timestamp` (número de milissegundos desde 1970 — formato Unix).

**O que acabou de acontecer?**  
Você clicou para disparar uma mensagem → ela percorreu o fio → chegou ao nó `debug` → foi exibida no painel. É o ciclo básico de todo fluxo Node-RED: **entrada → processamento → saída**.

---

## Passo 6 — Configurar uma mensagem personalizada

Vamos mudar o que o `inject` envia.

1. **Dê duplo clique** no nó `inject`
2. Uma janela de configuração se abre
3. Localize o campo **"msg.payload"**
4. Clique no seletor que está escrito **"timestamp"** e mude para **"string"**
5. No campo de texto que aparecer, escreva: `Sensor OK`
6. Clique em **"Done"** (canto superior direito da janela)
7. Clique em **"Deploy"** novamente
8. Clique no botão do nó `inject`

No painel Debug aparecerá: `Sensor OK`

**Explicando os campos da janela de configuração do `inject`:**

| Campo | Significado |
|-------|-------------|
| **Name** | Nome que aparece no nó no canvas (opcional, mas ajuda a organizar) |
| **msg.payload** | O conteúdo principal da mensagem enviada |
| **msg.topic** | Assunto/rótulo da mensagem (muito usado com MQTT) |
| **Repeat** | Define se o disparo é manual, periódico ou agendado |
| **Inject once after** | Dispara automaticamente X segundos após o Deploy |

---

## Desafio Extra — Disparo automático

1. Dê duplo clique no nó `inject`
2. Em **"Repeat"**, mude de `none` para `interval`
3. Configure: a cada **2** segundos
4. Clique em **Done** → **Deploy**
5. Observe as mensagens chegando automaticamente no painel Debug

Para parar: dê duplo clique → mude Repeat de volta para `none` → Deploy.

---

# PARTE 4 — EXERCÍCIO 2: Lógica de Alarme de Temperatura

## Objetivo
Criar uma lógica de controle real: ler um valor, tomar uma decisão e rotear a saída.

**Conceito aprendido:** Nó `function`, múltiplas saídas, JavaScript básico

---

## O Cenário

Um sensor de temperatura manda um valor (0–100°C). O sistema deve:
- Se temperatura ≤ 75°C → exibir "Normal"
- Se temperatura > 75°C → exibir "ALARME"

---

## Passo 1 — Montar os nós no canvas

Precisamos de: 1 `inject` + 1 `function` + 2 `debug`

1. Arraste 1 nó **`inject`** para o canvas
2. Arraste 1 nó **`function`** para o canvas (à direita do inject)
3. Arraste 2 nós **`debug`** para o canvas (um acima e um abaixo, à direita do function)

Disposição sugerida:
```
                         ┌──────────┐
                    ┌───►│ debug 1  │  (saída normal)
┌────────┐  ┌──────┤    └──────────┘
│ inject ├─►│ func │
└────────┘  └──────┤    ┌──────────┐
                    └───►│ debug 2  │  (alarme)
                         └──────────┘
```

---

## Passo 2 — Configurar o nó `inject`

1. Dê duplo clique no nó `inject`
2. Mude `msg.payload` de **"timestamp"** para **"number"**
3. Digite o valor **`80`** no campo
4. Clique em **Done**

---

## Passo 3 — Configurar o nó `function` com 2 saídas

O nó `function` permite escrever código JavaScript para processar a mensagem.

1. Dê duplo clique no nó **`function`**
2. A janela tem várias abas. Estamos na aba **"On Message"** (onde escrevemos o código executado a cada mensagem recebida)
3. No campo **"Outputs"** (canto inferior esquerdo da janela), mude de `1` para `2`
   - Isso cria **duas saídas** no nó (dois quadradinhos à direita)
4. No editor de código, **apague o conteúdo padrão** e cole o seguinte:

```javascript
// Pega o valor que chegou na mensagem
const temperatura = msg.payload;

// Toma a decisão
if (temperatura > 75) {
    // Muda o texto da mensagem para indicar alarme
    msg.payload = "ALARME: Temperatura alta! (" + temperatura + "°C)";
    
    // node.send([saída1, saída2])
    // null = não envia por essa saída
    // msg = envia por essa saída
    node.send([null, msg]);  // envia APENAS pela saída 2
    
} else {
    msg.payload = "Normal: " + temperatura + "°C";
    node.send([msg, null]);  // envia APENAS pela saída 1
}
```

5. Clique em **Done**

**Entendendo o código linha por linha:**

```javascript
const temperatura = msg.payload;
// msg é o objeto mensagem que chega no nó
// msg.payload é o campo principal — aqui é o número que o inject enviou
// Estamos guardando esse número numa variável chamada "temperatura"

if (temperatura > 75) { ... }
// Estrutura de decisão padrão do JavaScript
// Se temperatura maior que 75, executa o primeiro bloco

node.send([null, msg]);
// node.send() é a função que envia a mensagem pelas saídas
// Recebe um ARRAY: cada posição = uma saída
// [null, msg] → saída 1 recebe null (não envia), saída 2 recebe msg (envia)
// [msg, null] → saída 1 envia, saída 2 não envia
```

---

## Passo 4 — Conectar os fios

Agora o nó `function` tem **2 quadradinhos de saída** no lado direito.

1. Conecte a **saída do `inject`** à **entrada do `function`**
2. Conecte a **saída 1 do `function`** (quadrado de cima) ao **primeiro nó `debug`**
3. Conecte a **saída 2 do `function`** (quadrado de baixo) ao **segundo nó `debug`**

---

## Passo 5 — Nomear os nós para organização

Boa prática: nomeie os nós para saber o que cada um faz.

**Para o inject:**
1. Duplo clique → campo **"Name"** → escreva `Temperatura`→ Done

**Para os debug:**
1. Duplo clique no primeiro debug → campo **"Name"** → escreva `Status Normal` → Done
2. Duplo clique no segundo debug → campo **"Name"** → escreva `Alarme` → Done

---

## Passo 6 — Deploy e Testes

1. Clique em **Deploy**
2. Clique no botão do nó `inject` (com valor 80)
3. Observe no painel Debug: deve aparecer no canal de Alarme

**Agora teste com outros valores:**

- Dê duplo clique no `inject` → mude o valor para `50` → Done → Deploy → clique no botão
  - Deve aparecer na saída Normal
- Mude para `75` → Deploy → clique
  - Deve aparecer Normal (75 **não é maior** que 75)
- Mude para `76` → Deploy → clique
  - Deve aparecer Alarme
- Mude para `100` → Deploy → clique
  - Alarme

---

## Passo 7 — Entendendo o painel Debug

No painel Debug, cada linha de mensagem mostra:

```
10:23:41  msg.payload : string[28]  "Normal: 50°C"
│         │             │            │
│         │             │            └─ conteúdo da mensagem
│         │             └─ tipo e tamanho
│         └─ qual campo da mensagem
└─ horário do disparo
```

Você pode clicar em `▶` antes da mensagem para expandir e ver o objeto `msg` completo com todos os campos.

---

# PARTE 5 — EXERCÍCIO 3: Comunicação MQTT

## Objetivo
Simular comunicação entre dispositivos numa rede industrial usando o protocolo MQTT.

**Conceito aprendido:** MQTT, broker, tópicos, publish/subscribe

---

## Entendendo MQTT antes de começar

**O que é MQTT?**  
É um protocolo de comunicação leve baseado no modelo **publicar/assinar (pub/sub)**. Usado amplamente em automação industrial, IoT e sistemas SCADA.

**Os 3 papéis do MQTT:**

```
                    ┌─────────────┐
   CLP/Sensor       │             │    SCADA/Dashboard
  [Publicador] ────►│   BROKER    │────► [Assinante]
  publica dado      │  (servidor) │     recebe dado
                    │             │
                    └─────────────┘
```

- **Publicador:** envia dados para um tópico no broker (ex: CLP enviando temperatura)
- **Broker:** servidor central que recebe e redistribui mensagens (ex: Mosquitto, HiveMQ)
- **Assinante:** recebe dados de tópicos de seu interesse (ex: sistema SCADA)
- **Tópico:** endereço da mensagem, como uma "pasta" no broker (ex: `fabrica/linha1/temperatura`)

---

## Passo 1 — Montar os dois fluxos no canvas

Vamos criar **dois fluxos separados** na mesma aba:
- Um **Publicador** (quem envia dados)
- Um **Assinante** (quem recebe dados)

**Fluxo Publicador:**  
Arraste para o canvas: 1 nó `inject` + 1 nó `mqtt out`

**Fluxo Assinante:**  
Arraste para o canvas (abaixo do publicador): 1 nó `mqtt in` + 1 nó `debug`

```
── PUBLICADOR ─────────────────────────────
  [ inject: valor 42 ] ──► [ mqtt out ]

── ASSINANTE ──────────────────────────────
        [ mqtt in ] ──► [ debug ]
```

---

## Passo 2 — Configurar o nó `inject`

1. Duplo clique no `inject`
2. `msg.payload` → mude para **"number"** → valor `42`
3. Name: `Simular Sensor`
4. Done

---

## Passo 3 — Configurar o nó `mqtt out` (Publicador)

Este nó **publica** mensagens no broker MQTT.

1. Dê duplo clique no nó **`mqtt out`**
2. Você verá a janela de configuração com o campo **"Server"** vazio
3. Clique no **lápis** ao lado do campo "Server"
4. Uma nova janela de configuração do servidor MQTT abre

**Na janela "Edit mqtt-broker node":**

| Campo | O que preencher | Explicação |
|-------|----------------|-----------|
| **Name** | `Broker HiveMQ` | Nome que aparecerá no nó (para identificar) |
| **Server** | `broker.hivemq.com` | Endereço do broker público gratuito |
| **Port** | `1883` | Porta padrão do MQTT (não criptografado) |
| **Protocol** | `MQTT V3.1.1` | Versão do protocolo (deixe o padrão) |
| **Client ID** | *deixe vazio* | O Node-RED gera automaticamente |
| **Keep Alive** | `60` | Tempo em segundos para manter conexão ativa |

5. Clique em **Add** (ou Update)
6. Volta para a janela do `mqtt out`. Agora configure:

| Campo | O que preencher | Explicação |
|-------|----------------|-----------|
| **Server** | `Broker HiveMQ` | O que acabamos de configurar |
| **Topic** | `eca/sala01/temperatura` | O endereço onde a mensagem será publicada |
| **QoS** | `0` | Qualidade do serviço: 0 = entrega sem confirmação (mais rápido) |
| **Retain** | *desmarcado* | Não reter última mensagem no broker |
| **Name** | `Publicar Temperatura` | Nome do nó |

7. Clique em **Done**

**O que é o Tópico?**  
O tópico é o **endereço ou identificador** das mensagens no protocolo MQTT. É composto por uma string contendo barras que definem uma estrutura hierárquica, como:

```
fabrica / linha1 / sensor / temperatura
  │         │        │          │
  └─ local  └─ setor └─ tipo    └─ grandeza
```

Boa prática: use tópicos descritivos e hierárquicos. Evite espaços e caracteres especiais.

---

## Passo 4 — Configurar o nó `mqtt in` (Assinante)

Este nó **assina** (escuta) um tópico no broker e dispara quando chega uma mensagem.

1. Dê duplo clique no nó **`mqtt in`**
2. Em **Server**, selecione **"Broker HiveMQ"** (o mesmo que configuramos)
3. Em **Topic**, digite exatamente: `eca/sala01/temperatura`
   - Deve ser **idêntico** ao tópico do `mqtt out`
4. **QoS**: `0`
5. **Output**: `auto-detect type` (detecta automaticamente se é número, string ou JSON)
6. **Name**: `Receber Temperatura`
7. Clique em **Done**

---

## Passo 5 — Conectar os fios

1. Conecte: `inject` → `mqtt out`
2. Conecte: `mqtt in` → `debug`

> Observe que os dois fluxos **não estão conectados entre si** no canvas. A conexão acontece através do **broker MQTT na internet**.

---

## Passo 6 — Deploy e Verificação da Conexão

1. Clique em **Deploy**
2. Olhe abaixo dos nós `mqtt out` e `mqtt in`
3. Você verá um texto em verde: **"connected"**

Se aparecer **"connecting"** por mais de 30 segundos, pode ser problema de rede. Tente:
- Verificar se a internet está funcionando
- Usar um broker alternativo: `test.mosquitto.org` (mesma configuração, só muda o endereço)

Se aparecer **"disconnected"**, verifique se o endereço do broker está correto.

---

## Passo 7 — Testar a Comunicação

1. Abra o painel **Debug** (aba no lado direito)
2. Clique no botão do nó **`inject`**
3. No painel Debug deve aparecer: `42`

**O que aconteceu por baixo dos panos:**
```
[inject: 42] → [mqtt out] → INTERNET → broker.hivemq.com
                                              │
                          [debug: 42] ← [mqtt in] ←┘
```

O dado saiu do seu computador, foi até um servidor na nuvem e voltou para o seu computador — tudo em milissegundos!

---

## Passo 8 — Experimentos para Fazer com os Alunos

**Experimento A — Publicar de dois computadores diferentes:**
- Se dois alunos configurarem o **mesmo tópico** no broker, eles podem se comunicar entre máquinas!
- Um publica, o outro recebe

**Experimento B — Tópico com wildcard:**
- No `mqtt in`, use o tópico `eca/sala01/#`
- O `#` é um curinga que assina **todos os sub-tópicos**
- Agora assine também `eca/sala01/umidade`, `eca/sala01/pressao`, etc.

**Experimento C — Payload JSON:**
- No `inject`, mude para `{}`  (Object) e monte um objeto:
  ```json
  { "temperatura": 80, "unidade": "C", "sensor": "PT100" }
  ```
- No `function`, use `msg.payload.temperatura` para acessar o valor

---

# PARTE 6 — RECURSOS AVANÇADOS 

## 6.1 Instalando Novos Nós — Paleta de Extensões

O Node-RED tem milhares de nós criados pela comunidade. Para instalar:

1. Clique em **☰** (menu hambúrguer, canto superior direito)
2. Clique em **"Manage palette"**
3. Clique na aba **"Install"**
4. Use a barra de busca para encontrar o nó desejado
5. Clique em **"install"** ao lado do nó
6. Aguarde a instalação (aparece barra de progresso)
7. Novos nós aparecerão na paleta esquerda

**Nós industriais recomendados:**

| Nome do pacote | Para que serve |
|---------------|----------------|
| `node-red-contrib-modbus` | Comunicação Modbus TCP/RTU com CLPs |
| `node-red-contrib-opcua` | Protocolo OPC-UA (padrão industrial) |
| `node-red-dashboard` | Criar dashboards com gauges, gráficos e botões |
| `node-red-node-serialport` | Comunicação serial RS-232/RS-485 |


---

# Dashboard Moderno com FlowFuse Dashboard (Dashboard 2.0)

O **FlowFuse Dashboard** é a evolução moderna do antigo Dashboard do Node-RED. Ele permite criar interfaces gráficas para supervisão e controle de processos industriais sem precisar desenvolver páginas web manualmente.

Com ele é possível criar:

* Indicadores numéricos
* Gráficos em tempo real
* Botões de comando
* Chaves liga/desliga
* Campos de entrada
* Tabelas
* Medidores (gauges)
* Interfaces responsivas para computadores, tablets e smartphones

---

## Por que usar o FlowFuse Dashboard?

O pacote antigo `node-red-dashboard` utilizava a tecnologia AngularJS, que foi descontinuada e não recebe mais atualizações.

O pacote atual:

```bash
@flowfuse/node-red-dashboard
```

é conhecido como **Dashboard 2.0** e utiliza tecnologias modernas baseadas em Vue.js.

### Principais vantagens

| Dashboard Antigo               | FlowFuse Dashboard                  |
| ------------------------------ | ----------------------------------- |
| AngularJS                      | Vue.js                              |
| Projeto descontinuado          | Desenvolvimento ativo               |
| Interface limitada             | Interface moderna                   |
| Menos opções de personalização | Maior flexibilidade                 |
| Responsividade limitada        | Responsivo para dispositivos móveis |

Para novos projetos, recomenda-se sempre utilizar o **FlowFuse Dashboard**.

---

## Instalando o Dashboard

1. Clique em **☰ → Manage Palette**
2. Abra a aba **Install**
3. Pesquise por:

```text
@flowfuse/node-red-dashboard
```

4. Clique em **Install**
5. Aguarde a conclusão da instalação

Após instalar, uma nova categoria chamada **Dashboard** aparecerá na paleta de nós.

---

## Estrutura Básica do Dashboard

O Dashboard é organizado em três níveis:

```text
Page
 └── Group
      └── Widget
```

### Page (Página)

Representa uma tela completa da aplicação.

Exemplos:

* Supervisório
* Sensores
* Alarmes
* Manutenção

---

### Group (Grupo)

Organiza widgets dentro de uma página.

Exemplos:

* Temperaturas
* Pressões
* Motores
* Bombas

---

### Widget

São os componentes visuais exibidos para o usuário.

Exemplos:

* ui-button
* ui-text
* ui-gauge
* ui-chart
* ui-switch
* ui-slider

---

## Exemplo Prático — Exibindo uma Temperatura

Monte o seguinte fluxo:

```text
inject → ui-gauge
```

### Passo 1

Arraste um nó:

```text
inject
```

Configure:

* Tipo: Number
* Valor: 25

---

### Passo 2

Arraste um nó:

```text
ui-gauge
```

Ao abrir a configuração:

1. Crie uma nova Page chamada:

```text
Supervisório
```

2. Crie um novo Group chamado:

```text
Temperatura
```

3. Configure:

```text
Label: Temperatura
Units: °C
Min: 0
Max: 100
```

---

### Passo 3

Conecte os nós:

```text
inject → ui-gauge
```

---

### Passo 4

Clique em:

```text
Deploy
```

---

## Acessando o Dashboard

Após o Deploy, abra no navegador:

```text
http://localhost:1880/dashboard
```

Você verá um medidor exibindo o valor enviado pelo nó `inject`.

Ao clicar no botão do `inject`, o valor será atualizado em tempo real.

---

## Aplicações Industriais

O FlowFuse Dashboard pode ser utilizado para:

* Supervisão de processos industriais
* Monitoramento de sensores
* Controle de iluminação
* Controle HVAC
* Sistemas de irrigação
* Monitoramento de energia
* Integração com MQTT
* Interfaces SCADA simplificadas

Embora não substitua sistemas SCADA profissionais em aplicações críticas, é uma excelente ferramenta para ensino, prototipagem, laboratórios e pequenos sistemas de automação.

---

### Widgets mais utilizados

| Widget        | Função                |
| ------------- | --------------------- |
| `ui-text`     | Exibir texto          |
| `ui-button`   | Acionar comandos      |
| `ui-switch`   | Liga/desliga          |
| `ui-gauge`    | Medidor analógico     |
| `ui-chart`    | Gráfico em tempo real |
| `ui-slider`   | Ajuste de valores     |
| `ui-dropdown` | Lista de seleção      |
| `ui-template` | HTML personalizado    |
| `ui-table`    | Exibição de tabelas   |

> Em projetos industriais educacionais, uma combinação de **MQTT + Node-RED + FlowFuse Dashboard** permite construir sistemas completos de monitoramento e controle com poucos nós e sem necessidade de programação web avançada.


---

## 6.2 Importando e Exportando Fluxos

Para compartilhar um fluxo com os alunos:

**Exportar:**
1. Pressione `Ctrl + A` para selecionar todos os nós
2. Pressione `Ctrl + E` (ou ☰ → Export)
3. Escolha **"selected nodes"**
4. Clique em **"Copy to Clipboard"**
5. Cole em qualquer editor de texto — é um JSON

**Importar:**
1. Pressione `Ctrl + I` (ou ☰ → Import)
2. Cole o JSON no campo
3. Clique em **"Import"**
4. Os nós aparecem no canvas prontos para usar

---

## 6.3 Subflows — Reutilizando Lógica

Um **Subflow** é um grupo de nós empacotado como um único nó personalizado. Útil para lógicas que se repetem (ex: filtro de temperatura em múltiplas linhas de produção).

**Para criar:**
1. Selecione os nós que quer agrupar (`Ctrl + A` ou clique + arraste)
2. ☰ → **"Create subflow from selection"**
3. Dê um nome ao subflow
4. Ele aparece na paleta como um novo nó

---

# PARTE 7 — AVALIAÇÃO DE SAÍDA

Antes de encerrar a monitoria, peça que cada aluno responda as questões abaixo (pode ser oral ou escrito):

---

### Questões Conceituais

**1.** O que é um **nó** no Node-RED? Dê um exemplo de nó que vimos hoje e explique o que ele faz.

**2.** O que é `msg.payload`? Por que ele é o campo mais importante de uma mensagem?

**3.** Para que serve o botão **Deploy**? O que acontece se você modificar um fluxo e não fizer o Deploy?

**4.** Qual é a diferença entre um **Publicador** e um **Assinante** no MQTT?

**5.** No Exercício 2, o código usou `node.send([msg, null])`. O que o `null` significa nesse contexto?

---

### Questão de Aplicação

**6.** Descreva como você montaria um sistema Node-RED que:
- Leia temperatura de um sensor via MQTT (tópico: `planta/forno1/temp`)
- Se a temperatura for maior que 200°C, publique um alarme no tópico `planta/forno1/alarme`
- Se for menor ou igual a 200°C, exiba "Operação Normal" no debug

*(Não precisa construir — descreva quais nós usaria e como os conectaria)*

---

### Gabarito Resumido (para o monitor)

1. Nó = unidade de processamento. Ex: `inject` dispara mensagens; `function` processa; `debug` exibe.
2. `msg.payload` é o campo que carrega o dado principal da mensagem (o "conteúdo").
3. Deploy ativa o fluxo. Sem Deploy, as mudanças existem só no canvas como rascunho.
4. Publicador envia para o broker; Assinante recebe do broker.
5. `null` significa "não enviar por essa saída".
6. `mqtt in` → `function` (if temp > 200) → `mqtt out` (alarme) / `debug` (normal).

---

# APÊNDICE — REFERÊNCIA RÁPIDA

## Atalhos do Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl + Z` | Desfazer |
| `Ctrl + A` | Selecionar tudo |
| `Ctrl + C / V` | Copiar / Colar nós |
| `Ctrl + I` | Importar fluxo |
| `Ctrl + E` | Exportar fluxo |
| `Ctrl + D` | Fazer Deploy |
| `Delete` | Deletar nó ou fio selecionado |
| `Ctrl + +/-` | Zoom in/out |
| `Ctrl + Shift + 0` | Reset zoom |

---

## Tipos de Dados no `inject`

| Tipo | Exemplo | Quando usar |
|------|---------|-------------|
| `string` | `"Sensor OK"` | Texto simples |
| `number` | `42` | Valores numéricos, temperaturas, etc. |
| `boolean` | `true` / `false` | Liga/desliga, aberto/fechado |
| `JSON` | `{"temp": 25}` | Múltiplos dados juntos |
| `timestamp` | `1718800000000` | Marca temporal (padrão) |
| `flow.` | variável de fluxo | Ler dado armazenado no contexto do fluxo |

---

## Estrutura de um Tópico MQTT Industrial

```
empresa / area / equipamento / grandeza
   │       │        │             │
   │       │        │             └── temperatura, pressao, rpm, status
   │       │        └────────────── forno01, motor03, valvula_A
   │       └─────────────────────── linha1, utilidades, manutencao
   └─────────────────────────────── acme, fabrica_sp, planta_norte

Exemplo real:
  acme/linha1/forno01/temperatura
  acme/linha1/forno01/pressao
  acme/linha1/motor03/rpm
  acme/utilidades/compressor/status
```

---

## Quando Usar Cada Nó

| Necessidade | Nó a usar |
|-------------|-----------|
| Disparar uma mensagem manualmente ou em intervalo | `inject` |
| Ver o que está na mensagem | `debug` |
| Executar lógica/decisão | `function` |
| Rotear por condição sem código | `switch` |
| Alterar campos da mensagem sem código | `change` |
| Enviar dado via MQTT | `mqtt out` |
| Receber dado via MQTT | `mqtt in` |
| Fazer requisição HTTP | `http request` |
| Atrasar uma mensagem | `delay` |
| Juntar várias mensagens em uma | `join` |

---

*Guia elaborado para a disciplina de Redes Industriais — Engenharia de Controle e Automação*  
*Todos os exercícios foram testados no Node-RED v3.x com Node.js v18 LTS*