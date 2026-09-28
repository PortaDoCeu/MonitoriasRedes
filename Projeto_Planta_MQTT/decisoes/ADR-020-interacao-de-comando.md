# ADR-020: Comportamento do app ao comandar

**Status:** Aceita

## Contexto

Um toque no botão vira uma mensagem que atravessa broker, gateway e CLP. Se a interface não mostrar o que está acontecendo, a pessoa toca de novo, e comandos duplicados chegam à planta.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Publicar e esquecer | Simples | Sem retorno; toques repetidos |
| Atualizar a tela assumindo sucesso | Parece rápido | Mostra estado falso quando o comando é rejeitado |
| **Botão bloqueado até a resposta, com tempo limite** | Estado sempre verdadeiro; sem duplicação | Um pouco mais de lógica no app |

## Decisão

- Ao enviar, o app gera um `id` aleatório, desabilita o controle e mostra "enviando".
- Ao receber `comando/resposta` com o mesmo `id`: mostra `executado`, `rejeitado` ou `falhou` com o `motivo`, e reabilita o controle.
- Sem resposta em 3 s: mostra "sem resposta" e reabilita.
- O valor exibido de velocidade vem sempre da telemetria (`referencia` e `velocidade`), nunca do que foi pedido.
- Com `modo_remoto = false`, controles ficam desabilitados com o aviso "bancada em modo local".
- Com `gateway/estado = offline`, todo o painel fica acinzentado com "gateway desconectado" e os valores ao vivo deixam de ser atualizados.
- Ligar o motor pede confirmação ("Ligar o motor da bancada?").

## Justificativa

A tela mostra o que a planta está fazendo, não o que alguém pediu. A diferença entre pedido e aplicado (HR10 e HR3) fica visível quando o CLP limita a referência.

## Consequências

- Positivas: comando duplicado por toque repetido é impossível.
- Negativas: um comando que chegou ao CLP mas cuja resposta se perdeu aparece como "sem resposta"; a telemetria mostra o estado real no segundo seguinte.

## Verificação

- Tocar 5 vezes seguidas em "ligar": só um comando registrado na tabela `comandos`.
- Com a chave em local, os controles aparecem desabilitados em até 2 s.
- Parar o gateway: aviso "gateway desconectado" aparece (tempo limitado pelo keepalive do MQTT, a medir no ensaio).

## Relacionadas

[ADR-010](ADR-010-ciclo-e-temporizacao.md), [ADR-011](ADR-011-validacao-de-comandos.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-019](ADR-019-tecnologia-do-app.md)
