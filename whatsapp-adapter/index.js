console.log("Iniciando o Adaptador do WhatsApp...");

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

// URL do webhook do nosso backend Python
// Por enquanto, ele ainda não existe, mas vamos apontar para onde ele estará.
const PYTHON_WEBHOOK_URL = 'http://localhost:8000/webhook/whatsapp';

// Usamos LocalAuth para salvar a sessão e não precisar escanear o QR Code toda vez.
const client = new Client({
    authStrategy: new LocalAuth()
});

// Evento 1: Gerar o QR Code
// Este evento é disparado quando o cliente precisa de autenticação.
client.on('qr', qr => {
    console.log("QR Code recebido! Escaneie com seu celular.");
    qrcode.generate(qr, { small: true });
});

// Evento 2: Cliente Autenticado e Pronto
// Disparado quando a conexão com o WhatsApp é bem-sucedida.
client.on('ready', () => {
    console.log('Cliente do WhatsApp está pronto e conectado!');
});

// Evento 3: Mensagem Recebida (O mais importante!)
// Disparado toda vez que uma nova mensagem chega.
client.on('message', async message => {
    // Ignora mensagens que nós mesmos enviamos
    if (message.fromMe) {
        return;
    }

    console.log(`\n--- Nova Mensagem ---`);
    console.log(`De: ${message.from}`); // Número do remetente
    console.log(`Mensagem: ${message.body}`);
    console.log(`---------------------`);

    // Prepara os dados para enviar ao backend Python
    const payload = {
        sender: message.from,
        text: message.body
    };

    // Tenta enviar a mensagem para o nosso backend via webhook
    try {
        console.log(`Enviando para o webhook: ${PYTHON_WEBHOOK_URL}`);
        await axios.post(PYTHON_WEBHOOK_URL, payload);
        console.log("Dados enviados para o backend Python com sucesso.");
    } catch (error) {
        console.error("ERRO: Falha ao enviar dados para o backend Python.", error.message);
    }
});


// Inicia o cliente
client.initialize();