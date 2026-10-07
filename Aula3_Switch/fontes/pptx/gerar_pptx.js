// Gera o PowerPoint: cada slide é a página do PDF do Beamer (mesmo visual)
// e as falas de cada \note{} vão para as notas do apresentador.
//
// Normalmente rodado pelo fontes/compilar.ps1. Parâmetros por variável de ambiente:
//   NOTAS    arquivo JSON das notas        (padrão: notas.json)
//   IMAGENS  pasta com slide-NN.png         (padrão: imagens)
//   TEX      fonte dos slides, para títulos (padrão: ../slides_aula3.tex)
// e o arquivo de saída como argumento        (padrão: ../../slides_aula3.pptx)

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const NOTAS = process.env.NOTAS || "notas.json";
const IMAGENS = process.env.IMAGENS || "imagens";
const TEX = process.env.TEX || "../slides_aula3.tex";
const SAIDA = process.argv[2] || "../../slides_aula3.pptx";

const notas = JSON.parse(fs.readFileSync(NOTAS, "utf8"));
const imagens = fs.readdirSync(IMAGENS).filter((f) => f.endsWith(".png")).sort();
if (imagens.length !== notas.length) {
  throw new Error(`${imagens.length} imagens e ${notas.length} notas: recompile e extraia de novo`);
}

// Título de cada frame, para o texto alternativo das imagens
const tex = fs.readFileSync(TEX, "utf8");
const titulos = ["O Switch na Rede da Planta"].concat(
  [...tex.matchAll(/\\begin\{frame\}\{(.*)\}\s*$/gm)].map((m) =>
    m[1].replace(/\\texttt\{([^}]*)\}/g, "$1").replace(/\\_/g, "_").replace(/[{}]/g, "")));

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";              // 10 x 5.625 pol, mesma proporção do Beamer
pres.title = "O Switch na Rede da Planta";
pres.author = "Gabriel de Oliveira e Silva";

imagens.forEach((arquivo, i) => {
  const slide = pres.addSlide();
  slide.background = { color: "0B1020" };
  slide.addImage({
    path: path.join(IMAGENS, arquivo), x: 0, y: 0, w: 10, h: 5.625,
    altText: titulos[i] || `Slide ${i + 1}`,
  });
  slide.addNotes(notas[i]);
});

pres.writeFile({ fileName: SAIDA }).then((f) => console.log("gerado:", f));
