import mongoose from 'mongoose';

const chatSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    title: {
        type: String,
        default: 'New Chat'
    },
    messages: [
        {
            text: { type: String, required: true },
            sender: { type: String, enum: ['user', 'bot'], required: true },
            timestamp: { type: Date, default: Date.now }
        }
    ],
    createdAt: {
        type: Date,
        default: Date.now
    },
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, { timestamps: true });

// Note: Mongoose automatically handles createdAt and updatedAt with timestamps: true

const Chat = mongoose.model('Chat', chatSchema);

export default Chat;
