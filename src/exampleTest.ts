class DispositivoRede {
  nome: string;
  ip: string;
  protocolo: string;

  constructor(nome: string, ip: string, protocolo: string) {
    this.nome = nome;
    this.ip = ip;
    this.protocolo = protocolo;
  }

  apresentar(): string {
    return `Dispositivo: ${this.nome} | IP: ${this.ip} | Protocolo: ${this.protocolo}`;
  }
}

const clpLinha1 = new DispositivoRede("CLP Linha 1", "192.168.0.10", "Modbus TCP");
const ihmPrincipal = new DispositivoRede("IHM Principal", "192.168.0.20", "PROFINET");

console.log(clpLinha1.apresentar());
console.log(ihmPrincipal.apresentar());
