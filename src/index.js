"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const Modbus = require('jsmodbus');
const { Socket } = require('node:net');
const socket = new Socket();
const options = {
    host: '127.0.0.1',
    port: 502,
};
const client = new Modbus.client.TCP(socket);
async function readRegisters() {
    try {
        const response = await client.readHoldingRegisters(0, 10);
        console.log('Registradores lidos:', response.response.body.valuesAsArray);
    }
    catch (error) {
        console.error('Erro ao ler registradores:', error);
    }
    finally {
        socket.end();
    }
}
socket.on('connect', readRegisters);
socket.on('error', (error) => {
    console.error('Erro de conexão:', error);
});
socket.connect(options);
//# sourceMappingURL=index.js.map