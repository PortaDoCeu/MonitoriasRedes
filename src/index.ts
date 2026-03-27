const Modbus = require('jsmodbus');
const { Socket } = require('node:net') as typeof import('node:net');

type SocketConnectOpts = import('node:net').SocketConnectOpts;

const socket = new Socket();

const options: SocketConnectOpts = {
    host: '192.168.5.17',
    port: 502,
};

const client = new Modbus.client.TCP(socket);

async function readRegisters(): Promise<void> {
    try {
        const response: { response: { body: { valuesAsArray: unknown } } } = await client.readHoldingRegisters(0, 10);
        console.log('Registradores lidos:', response.response.body.valuesAsArray);
    } catch (error: unknown) {
        console.error('Erro ao ler registradores:', error);
    } finally {
        socket.end();
    }
}

socket.on('connect', readRegisters);

socket.on('error', (error: unknown) => {
    console.error('Erro de conexão:', error);
});

socket.connect(options);
