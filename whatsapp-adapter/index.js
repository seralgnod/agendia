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
    console.log(`De: ${message.from}`); // Quem enviou
    console.log(`Para: ${message.to}`);   // Para quem foi enviada
    console.log(`Mensagem: ${message.body}`);
    console.log(`---------------------`);

    // --- ALTERAÇÃO AQUI ---
    // Adicionamos o 'recipient' ao payload
    const payload = {
        sender: message.from,
        recipient: message.to, // O número que recebeu a mensagem
        text: message.body
    };

    try {
        console.log(`[PASSO 1] Enviando para o webhook: ${PYTHON_WEBHOOK_URL}`);
        const response = await axios.post(PYTHON_WEBHOOK_URL, payload);
        console.log("[PASSO 2] Backend Python respondeu com sucesso.");
        // ... (resto do código permanece o mesmo) ...
        if (response.data && response.data.reply) {
            const replyText = response.data.reply;
            console.log(`[PASSO 3] Preparando para enviar resposta ao cliente: "${replyText}"`);
            await message.reply(replyText);
            console.log("[PASSO 4] Resposta enviada com sucesso!");
        } else {
            console.error("[ERRO DE LÓGICA] O backend respondeu, mas não encontrou o campo 'reply' no JSON.");
        }
    } catch (error) {
        // ... (bloco catch inalterado) ...
        console.error("[ERRO CRÍTICO] Falha na comunicação com o backend ou no envio da resposta.", error.message);
        await message.reply("Desculpe, meu cérebro (serviço principal) está temporariamente fora do ar. Tente novamente mais tarde.");
    }
});

client.initialize();