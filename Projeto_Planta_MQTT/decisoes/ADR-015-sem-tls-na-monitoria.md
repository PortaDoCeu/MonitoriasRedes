# ADR-015: MQTT sem TLS na monitoria (risco aceito)

**Status:** Aceita

## Contexto

Sem TLS, usuário, senha e payloads MQTT trafegam em texto claro. Com TLS, os celulares precisam confiar no certificado do broker. Sem internet e sem domínio, não há como obter um certificado de uma autoridade pública; um certificado autoassinado faz o navegador bloquear a conexão WebSocket segura até cada aluno aceitar manualmente um aviso de segurança, o que em alguns celulares nem é possível para WebSocket.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| TLS com certificado autoassinado | Tráfego cifrado | 40 celulares precisando aceitar exceção de segurança; falha comum ao vivo; ensina a turma a ignorar aviso de certificado |
| CA própria instalada nos celulares | Tráfego cifrado sem aviso | Instalar CA em celular pessoal de aluno é invasivo e demorado |
| **Sem TLS, com rede isolada e risco documentado** | Funciona em qualquer celular | Senha e dados legíveis por quem capturar o tráfego |

## Decisão

Na monitoria, MQTT e HTTP sem TLS, com as compensações:
- Wi-Fi dedicado, com WPA2 e senha, sem rota para a internet ([ADR-021](ADR-021-topologia-e-enderecamento.md));
- porta 1883 restrita ao próprio notebook ([ADR-013](ADR-013-configuracao-do-broker.md));
- senhas exclusivas deste projeto, trocadas a cada semestre;
- a segurança funcional não depende da rede ([ADR-005](ADR-005-seguranca-funcional-no-clp.md)).

Em uma implantação real, esta decisão seria revertida: TLS na porta 8883 e WSS na 443, certificado de uma CA da empresa, e autenticação por certificado de cliente para o gateway.

## Justificativa

O risco residual (alguém na rede da aula capturar a senha do operador) tem impacto limitado: o pior que um comando consegue é o que o CLP permite, dentro de `VEL_MAX` e só em modo remoto. E o risco vira conteúdo: capturar o `CONNECT` do MQTT no Wireshark e ler a senha é uma demonstração direta do porquê TLS existe, ligada ao eixo de segurança OT da monitoria.

## Consequências

- Positivas: funciona em qualquer celular sem configuração.
- Negativas: sigilo zero na rede da aula. Registrado na tabela de riscos aceitos do [README](README.md).

## Verificação

- Captura no Wireshark da rede do AP mostra o pacote `CONNECT` com usuário e senha legíveis. Se a captura não mostrar, alguma premissa desta ADR está errada.
- A senha do operador não é reutilizada em nenhum outro sistema (verificação manual do monitor).

## Relacionadas

[ADR-013](ADR-013-configuracao-do-broker.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-021](ADR-021-topologia-e-enderecamento.md), [ADR-029](ADR-029-modelo-de-ameaca.md)
