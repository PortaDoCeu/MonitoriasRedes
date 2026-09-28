// App da bancada: dados ao vivo por MQTT sobre WebSocket, histórico por HTTP.
// Decisões: ADR-014 (dois usuários), ADR-019 (tecnologia), ADR-020 (comportamento do comando).

const CFG = window.CONFIG;
const B = CFG.bancada;
const T = {
  temperatura: `${B}/telemetria/temperatura`,
  velocidade: `${B}/telemetria/velocidade`,
  referencia: `${B}/telemetria/referencia`,
  status: `${B}/telemetria/status`,
  cmdVelocidade: `${B}/comando/velocidade`,
  cmdMotor: `${B}/comando/motor`,
  resposta: `${B}/comando/resposta`,
  estado: `${B}/gateway/estado`,
};
const URL_BROKER = `ws://${CFG.wsHost || location.hostname}:${CFG.wsPorta}`;
const TEMPO_LIMITE_MS = 3000;
const MAX_PONTOS = 3600;

const FALHAS = {
  1: "Falha no inversor", 2: "Heartbeat perdido: o CLP parou o motor",
  3: "Emergência acionada", 4: "Temperatura acima do limite", 5: "Leitura do termopar inválida",
};
const NOMES_STATUS = {
  motor_ligado: "motor ligado", modo_remoto: "remoto", falha_inversor: "falha no inversor",
  heartbeat_perdido: "heartbeat perdido", referencia_limitada: "referência limitada",
  emergencia: "emergência",
};

const $ = (id) => document.getElementById(id);
const esc = (x) => String(x ?? "").replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
const estado = { status: null, gatewayOnline: false, clp: false, pendente: null, operador: null };

$("titulo").textContent = `Bancada ${B.replace(/\D/g, "") || B}`;
$("ref").max = CFG.velMax;

// ---------------------------------------------------------------- gráfico

const grafico = new Chart($("grafico"), {
  type: "line",
  data: {
    labels: [],
    datasets: [
      { label: "Temperatura (°C)", data: [], borderColor: "#B7791F", yAxisID: "t", pointRadius: 0, borderWidth: 2 },
      { label: "Velocidade (rpm)", data: [], borderColor: "#0B7F7D", yAxisID: "v", pointRadius: 0, borderWidth: 2 },
    ],
  },
  options: {
    animation: false,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    scales: {
      x: { ticks: { maxTicksLimit: 6 } },
      t: { position: "left", title: { display: true, text: "°C" } },
      v: { position: "right", min: 0, grid: { drawOnChartArea: false }, title: { display: true, text: "rpm" } },
    },
  },
});

const horaLocal = (ts) => new Date(ts).toLocaleTimeString("pt-BR");
let ultimaVelocidade = null;

function adicionarPonto(ts, temperatura) {
  grafico.data.labels.push(horaLocal(ts));
  grafico.data.datasets[0].data.push(temperatura);
  grafico.data.datasets[1].data.push(ultimaVelocidade);
  if (grafico.data.labels.length > MAX_PONTOS) {
    grafico.data.labels.shift();
    grafico.data.datasets.forEach((d) => d.data.shift());
  }
  grafico.update("none");
}

async function carregarHistorico() {
  const [temp, vel] = await Promise.all(["temperatura", "velocidade"].map(
    (g) => fetch(`/historico?grandeza=${g}&horas=1`).then((r) => r.json())));
  const velPorTs = new Map(vel.map((p) => [p.ts, p.valor]));
  grafico.data.labels = temp.map((p) => horaLocal(p.ts));
  grafico.data.datasets[0].data = temp.map((p) => p.valor);
  grafico.data.datasets[1].data = temp.map((p) => velPorTs.get(p.ts) ?? null);
  grafico.update("none");
}

// ---------------------------------------------------------------- tela

function atualizarTela() {
  const s = estado.status;
  const aviso = $("aviso");
  let texto = "";
  let classe = "";
  if (!estado.gatewayOnline) texto = "Gateway desconectado: os valores não estão sendo atualizados.";
  else if (!estado.clp) texto = "Gateway sem conexão com o CLP.";
  else if (s && s.codigo_falha) texto = `Falha ${s.codigo_falha}: ${FALHAS[s.codigo_falha] || "desconhecida"}.`;
  else if (s && !s.modo_remoto) { texto = "Bancada em modo local: comandos pela rede estão bloqueados."; classe = "atencao"; }
  aviso.textContent = texto;
  aviso.className = `aviso ${classe} ${texto ? "" : "escondido"}`;

  document.querySelector("main").style.opacity = estado.gatewayOnline ? 1 : 0.55;
  $("chip-gateway").className = `chip ${estado.gatewayOnline ? "ok" : "falha"}`;
  $("chip-clp").className = `chip ${estado.gatewayOnline && estado.clp ? "ok" : "falha"}`;

  if (s) {
    $("status").innerHTML = Object.entries(NOMES_STATUS).map(([chave, nome]) => {
      const alerta = ["falha_inversor", "heartbeat_perdido", "emergencia"].includes(chave);
      return `<span class="${s[chave] ? (alerta ? "alerta" : "ativo") : ""}">${nome}</span>`;
    }).join("");
  }

  const podeComandar = estado.gatewayOnline && estado.clp && s && s.modo_remoto && !estado.pendente;
  ["b-ref", "b-ligar", "b-parar", "b-reconhecer", "ref"].forEach((id) => { $(id).disabled = !podeComandar; });
}

// ---------------------------------------------------------------- MQTT: leitura

const leitor = mqtt.connect(URL_BROKER, {
  username: "app_leitura", password: CFG.senhaLeitura,
  clientId: `app-${B}-${Math.random().toString(16).slice(2, 10)}`, reconnectPeriod: 2000,
});

leitor.on("connect", () => {
  $("chip-broker").className = "chip ok";
  leitor.subscribe([T.temperatura, T.velocidade, T.referencia, T.status, T.estado, T.resposta], { qos: 1 });
});
leitor.on("close", () => { $("chip-broker").className = "chip falha"; });

leitor.on("message", (topico, carga) => {
  let dados;
  try { dados = JSON.parse(carga.toString()); } catch { return; }
  switch (topico) {
    case T.temperatura:
      $("v-temperatura").textContent = dados.valor.toFixed(1);
      adicionarPonto(dados.ts, dados.valor);
      break;
    case T.velocidade:
      $("v-velocidade").textContent = dados.valor;
      ultimaVelocidade = dados.valor;
      break;
    case T.referencia:
      $("v-referencia").textContent = dados.valor;
      break;
    case T.status:
      estado.status = dados;
      atualizarTela();
      break;
    case T.estado:
      estado.gatewayOnline = dados.estado === "online";
      estado.clp = dados.clp === true;
      atualizarTela();
      break;
    case T.resposta:
      receberResposta(dados);
      break;
  }
});

// ---------------------------------------------------------------- MQTT: operador

$("login").addEventListener("submit", (evento) => {
  evento.preventDefault();
  $("erro-login").textContent = "";
  const cliente = mqtt.connect(URL_BROKER, {
    username: $("usuario").value, password: $("senha").value,
    clientId: `operador-${B}-${Math.random().toString(16).slice(2, 10)}`,
    reconnectPeriod: 0,
  });
  cliente.on("connect", () => {
    estado.operador = cliente;
    $("senha").value = "";                 // a senha não fica guardada (ADR-014)
    $("login").classList.add("escondido");
    $("controles").classList.remove("escondido");
    atualizarTela();
  });
  cliente.on("error", () => {
    $("erro-login").textContent = "Usuário ou senha recusados pelo broker.";
    cliente.end(true);
  });
});

$("b-sair").addEventListener("click", () => {
  if (estado.operador) estado.operador.end(true);
  estado.operador = null;
  $("controles").classList.add("escondido");
  $("login").classList.remove("escondido");
});

function enviar(topico, valor, descricao) {
  if (!estado.operador || estado.pendente) return;
  const id = Math.random().toString(36).slice(2, 10);
  estado.operador.publish(topico, JSON.stringify({ id, valor }), { qos: 1 });
  estado.pendente = { id, descricao, timer: setTimeout(() => finalizar("sem-resposta", "sem resposta em 3 s"), TEMPO_LIMITE_MS) };
  mostrarResposta("", `Enviando: ${descricao}...`);
  atualizarTela();
}

function receberResposta(dados) {
  if (!estado.pendente || dados.id !== estado.pendente.id) {
    carregarComandos();
    return;
  }
  clearTimeout(estado.pendente.timer);
  finalizar(dados.resultado, dados.motivo);
}

function finalizar(resultado, motivo) {
  const descricao = estado.pendente ? estado.pendente.descricao : "";
  estado.pendente = null;
  mostrarResposta(resultado, `${descricao}: ${resultado}${motivo ? ` (${motivo})` : ""}`);
  atualizarTela();
  carregarComandos();
}

function mostrarResposta(classe, texto) {
  $("resposta").className = `resposta ${classe}`;
  $("resposta").textContent = texto;
}

$("ref").addEventListener("input", () => { $("ref-valor").textContent = $("ref").value; });
$("b-ref").addEventListener("click", () => enviar(T.cmdVelocidade, Number($("ref").value), `referência ${$("ref").value} rpm`));
$("b-ligar").addEventListener("click", () => {
  if (confirm("Ligar o motor da bancada?")) enviar(T.cmdMotor, 1, "ligar");
});
$("b-parar").addEventListener("click", () => enviar(T.cmdMotor, 0, "parar"));
$("b-reconhecer").addEventListener("click", () => enviar(T.cmdMotor, 2, "reconhecer falha"));

// ---------------------------------------------------------------- lista de comandos

async function carregarComandos() {
  const lista = await fetch("/comandos?limite=8").then((r) => r.json()).catch(() => []);
  $("comandos").innerHTML = lista.map((c) => {
    const tipo = c.topico.split("/").pop();
    const quando = horaLocal(c.ts);
    return `<li>${quando} · ${esc(tipo)} = ${esc(c.valor ?? "?")} · <strong>${esc(c.resultado ?? "aguardando")}</strong>${c.motivo ? ` (${esc(c.motivo)})` : ""}</li>`;
  }).join("") || "<li>Nenhum comando ainda.</li>";
}

carregarHistorico().catch(() => {});
carregarComandos();
atualizarTela();
