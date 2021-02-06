const express = require('express');

const cors = require('cors');

const amqp = require('amqplib/callback_api');

const app = express();


const socket = require('socket.io');

app.use('/socket.io', cors({
    origin: 'http://localhost:5000',
    optionsSuccessStatus: 200
}));

const server = app.listen(9000, () => {
    console.log(`Server started on port 9000`);
})

const io = socket(server);

let activeSocket;

io.on('connection', (socket) => {
    console.log(`made socket connection`);

    amqp.connect('amqp://localhost', (error0, connection) => {
    if(error0) {
        throw error0;
    }
    connection.createChannel((error1, channel) => {
        if(error1) {
            throw error1
        }

        let queue = 'counter';

        channel.assertQueue(queue, {
            durable: false
        });

        console.log(` [*] Waiting for messages in ${queue}. To exit press CTRL + C`)

        channel.consume(queue, (msg) => {
            if(msg.content.toString().length > 0) {
                console.log(` [x] Received ${msg.content.toString()}`);
                io.sockets.emit('counter', msg.content.toString());
            }
        }, {
            noAck: true
        });

        socket.on('reset', (data) => {
            console.log('RESET EVENT');
            console.log(data);
            channel.sendToQueue(queue, Buffer.from(data));
        });

    })
})

});




