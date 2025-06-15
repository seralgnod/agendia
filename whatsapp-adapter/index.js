console.log("Iniciando o Adaptador do WhatsApp...");

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const PYTHON_WEBHOOK_URL = 'http://localhost:8000/webhook/whatsapp';
const client = new Client({ authStrategy: new LocalAuth() });

client.on('qr', qr => {
    console.log("QR Code recebido! Escaneie com seu celular.");
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('Cliente do WhatsApp está pronto e conectado!');
});

client.on('message', async message => {
    if (message.fromMe) {
        return;
    }
    console.log(`\n--- Nova Mensagem ---`);
    console.log(`De: ${message.from}`);
    console.log(`Mensagem: ${message.body}`);
    console.log(`---------------------`);

    const payload = {
        sender: message.from,
        text: message.body
    };

    try {
        console.log(`[PASSO 1] Enviando para o webhook: ${PYTHON_WEBHOOK_URL}`);
        const response = await axios.post(PYTHON_WEBHOOK_URL, payload);
        console.log("[PASSO 2] Backend Python respondeu com sucesso.");
        console.log("Dados recebidos do backend:", response.data); // LOG ADICIONADO

        if (response.data && response.data.reply) {
            const replyText = response.data.reply;
            console.log(`[PASSO 3] Preparando para enviar resposta ao cliente: "${replyText}"`);
            
            // MÉTODO ALTERNATIVO: Usando message.reply() que é mais direto
            await message.reply(replyText);
            
            console.log("[PASSO 4] Resposta enviada com sucesso!");
        } else {
            console.error("[ERRO DE LÓGICA] O backend respondeu, mas não encontrou o campo 'reply' no JSON.");
        }

    } catch (error) {
        console.error("[ERRO CRÍTICO] Falha na comunicação com o backend ou no envio da resposta.", error.message);
        await message.reply("Desculpe, meu cérebro (serviço principal) está temporariamente fora do ar. Tente novamente mais tarde.");
    }
});

client.initialize();