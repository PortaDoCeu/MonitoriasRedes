"""Gera usuários, senhas e ACL do broker para N bancadas (ADR-014 e ADR-030).

Uso (na pasta Projeto_Planta_MQTT):
    python broker/criar_usuarios.py 6

Cria, dentro de broker/:
    senhas          arquivo de senhas do Mosquitto (fora do git)
    acl             regras de acesso por usuário
    credenciais.md  senhas para entregar a cada grupo (fora do git)

Usuários:
    gateway_bancadaN     publica telemetria e respostas da bancada N, assina os comandos dela
    middleware_bancadaN  só assina bancadaN/#
    operador_bancadaN    lê e comanda só a bancada N (grupo testa comandos e usa o app)
    app_leitura          só lê (senha pública, vai no app)
    app_operador         lê e comanda qualquer bancada (senha só do monitor)
    monitor              acesso total, para o MQTT Explorer do projetor
"""

import secrets
import shutil
import subprocess
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
CANDIDATOS = [shutil.which("mosquitto_passwd"),
              r"C:\Program Files\mosquitto\mosquitto_passwd.exe"]

LEITURA_APP = ["+/telemetria/#", "+/comando/resposta", "+/gateway/estado"]


def senha():
    return secrets.token_urlsafe(9)


def main(n_bancadas, pasta=PASTA):
    pasta = Path(pasta)
    passwd = next((p for p in CANDIDATOS if p and Path(p).exists()), None)
    if passwd is None:
        sys.exit("mosquitto_passwd não encontrado. Instale o Mosquitto primeiro.")

    usuarios = {"app_leitura": "leitura", "app_operador": senha(), "monitor": senha()}
    acl = ["# Gerado por broker/criar_usuarios.py. Não edite à mão.", ""]

    acl += ["user app_leitura"] + [f"topic read {t}" for t in LEITURA_APP] + [""]
    acl += (["user app_operador"] + [f"topic read {t}" for t in LEITURA_APP]
            + ["topic write +/comando/velocidade", "topic write +/comando/motor", ""])
    acl += ["user monitor", "topic readwrite #", ""]

    for n in range(1, n_bancadas + 1):
        b = f"bancada{n}"
        usuarios[f"gateway_{b}"] = senha()
        usuarios[f"middleware_{b}"] = senha()
        usuarios[f"operador_{b}"] = senha()
        acl += [f"user gateway_{b}",
                f"topic write {b}/telemetria/#",
                f"topic write {b}/comando/resposta",
                f"topic write {b}/gateway/estado",
                f"topic read {b}/comando/velocidade",
                f"topic read {b}/comando/motor",
                "",
                f"user middleware_{b}",
                f"topic read {b}/#",
                "",
                f"user operador_{b}",
                f"topic read {b}/#",
                f"topic write {b}/comando/velocidade",
                f"topic write {b}/comando/motor",
                ""]

    (pasta / "acl").write_text("\n".join(acl), encoding="utf-8")

    arquivo_senhas = pasta / "senhas"
    arquivo_senhas.write_text("", encoding="utf-8")
    for usuario, s in usuarios.items():
        subprocess.run([passwd, "-b", str(arquivo_senhas), usuario, s], check=True,
                       stdout=subprocess.DEVNULL)

    linhas = ["# Credenciais do broker (NÃO versionar)", "",
              f"- app_leitura: `{usuarios['app_leitura']}` (pública, vai no app)",
              f"- app_operador: `{usuarios['app_operador']}` (só o monitor)",
              f"- monitor: `{usuarios['monitor']}` (MQTT Explorer do projetor)", ""]
    for n in range(1, n_bancadas + 1):
        b = f"bancada{n}"
        linhas += [f"## {b}", "", "```",
                   f"BANCADA={b}",
                   f"MQTT_USUARIO_GATEWAY=gateway_{b}",
                   f"MQTT_SENHA_GATEWAY={usuarios[f'gateway_{b}']}",
                   f"MQTT_USUARIO_MIDDLEWARE=middleware_{b}",
                   f"MQTT_SENHA_MIDDLEWARE={usuarios[f'middleware_{b}']}",
                   "```", "",
                   f"Operador da bancada (MQTT Explorer e login no app): `operador_{b}` / `{usuarios[f'operador_{b}']}`", ""]
    (pasta / "credenciais.md").write_text("\n".join(linhas), encoding="utf-8")
    print(f"{len(usuarios)} usuários criados para {n_bancadas} bancadas. Veja {pasta / 'credenciais.md'}")
    return usuarios


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6)
