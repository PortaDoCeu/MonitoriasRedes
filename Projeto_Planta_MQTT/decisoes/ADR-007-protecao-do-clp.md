# ADR-007: Proteção de acesso ao CLP

**Status:** Aceita

## Contexto

Na mesma rede do CLP estarão o notebook e, pelo AP Wi-Fi, os celulares da turma. Com a proteção padrão aberta, qualquer um com TIA Portal na rede pode baixar outro programa, parar a CPU ou ler e escrever variáveis por comunicação S7 (PUT/GET).

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Deixar acesso total (padrão comum em laboratório) | Nenhum atrito | Qualquer um na rede reprograma o CLP |
| Proibir qualquer acesso | Máxima proteção | Impede o próprio monitor de ajustar o programa |
| **Nível de acesso com senha para escrita, PUT/GET desabilitado** | Monitor mantém controle; alunos só leem | Uma senha a mais para guardar |

## Decisão

- Em Properties da CPU, Protection & Security: nível de acesso que exige senha para escrita (download, mudança de modo RUN/STOP). A senha fica com o monitor e fora do repositório.
- "Permit access with PUT/GET communication from remote partner" desmarcado.
- A única comunicação de dados aceita é Modbus TCP na porta 502, pela conexão do gateway ([ADR-004](ADR-004-papeis-modbus-e-db.md)).

## Justificativa

Fecha o caminho de reprogramação e a porta de comunicação S7 que o projeto não usa. É a aplicação direta do princípio de desabilitar o que não é necessário, visto no eixo de segurança OT da monitoria.

## Consequências

- Positivas: alunos não conseguem parar a CPU ou baixar programa, nem por engano.
- Negativas: o Modbus TCP em si continua sem autenticação; isso é tratado pela conexão única e pela rede ([ADR-021](ADR-021-topologia-e-enderecamento.md), [ADR-029](ADR-029-modelo-de-ameaca.md)).

## Verificação

- Tentar "Go offline / Go online" e download pelo TIA Portal de outra máquina sem senha: operação negada.
- Configuração PUT/GET visível como desmarcada nas propriedades exportadas do projeto.

## Relacionadas

[ADR-004](ADR-004-papeis-modbus-e-db.md), [ADR-025](ADR-025-configuracao-e-segredos.md), [ADR-029](ADR-029-modelo-de-ameaca.md)
