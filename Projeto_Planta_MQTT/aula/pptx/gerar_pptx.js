// Gera slides_projeto.pptx: cada slide é a página do PDF do Beamer (mesmo visual)
// e as falas de cada \note{} vão para as notas do apresentador do PowerPoint.
//
// Uso (na pasta aula/pptx), depois de compilar ../slides_projeto.tex:
//   python extrair_notas.py ../slides_projeto.tex notas.json
//   miktex-pdftoppm -r 240 -png ../slides_projeto.pdf imagens/slide
//   node gerar_pptx.js [arquivo.pptx]   (padrão: ../slides_projeto.pptx)

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const notas = JSON.parse(fs.readFileSync("notas.json", "utf8"));
const imagens = fs.readdirSync("imagens").filter((f) => f.endsWith(".png")).sort();
if (imagens.length !== notas.length) {
  throw new Error(`${imagens.length} imagens e ${notas.length} notas: recompile e extraia de novo`);
}

// Título de cada frame, para o texto alternativo das imagens
const tex = fs.readFileSync("../slides_projeto.tex", "utf8");
const titulos = ["Do CLP ao Celular"].concat(
  [...tex.matchAll(/\\begin\{frame\}\{(.*)\}\s*$/gm)].map((m) =>
    m[1].replace(/\\texttt\{([^}]*)\}/g, "$1").replace(/\\_/g, "_").replace(/[{}]/g, "")));

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";              // 10 x 5.625 pol, mesma proporção do Beamer
pres.title = "Do CLP ao Celular";
pres.author = "Gabriel de Oliveira e Silva";

imagens.forEach((arquivo, i) => {
  const slide = pres.addSlide();
  slide.background = { color: "0B1020" };
  slide.addImage({
    path: path.join("imagens", arquivo), x: 0, y: 0, w: 10, h: 5.625,
    altText: titulos[i] || `Slide ${i + 1}`,
  });
  slide.addNotes(notas[i]);
});

pres.writeFile({ fileName: process.argv[2] || "../slides_projeto.pptx" }).then((f) => console.log("gerado:", f));
