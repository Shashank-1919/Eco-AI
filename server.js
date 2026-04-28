import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import { spawn } from 'child_process';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';
import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
import User from './models/User.js';
import Chat from './models/Chat.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Cross-platform Python path detection
const pythonExecutable = process.env.PYTHON_PATH || (os.platform() === 'win32' ? path.join(__dirname, '.venv', 'Scripts', 'python.exe') : 'python3');

const app = express();
const PORT = process.env.PORT || 5000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/ecoai';
const JWT_SECRET = process.env.JWT_SECRET || 'ecoai_secret_key_2024';

// MongoDB Connection
mongoose.connect(MONGODB_URI)
    .then(() => console.log('Connected to MongoDB via Compass'))
    .catch(err => console.error('MongoDB connection error:', err));

app.use(cors());
app.use(bodyParser.json());
app.use('/static', express.static(path.join(__dirname, 'static')));

// ── Auth Middleware ──────────────────────────────────────────────────────────
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token || token === 'null' || token === 'undefined') {
        return res.status(401).json({ error: 'Unauthorized. Please login.' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Forbidden. Invalid session.' });
        req.user = user;
        next();
    });
};

// ── Page Routes ─────────────────────────────────────────────────────────────
app.get('/login', (req, res) => res.sendFile(path.join(__dirname, 'templates', 'login.html')));
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'templates', 'index.html')));
app.get('/result', (req, res) => res.sendFile(path.join(__dirname, 'templates', 'result.html')));

// ── Auth API ───────────────────────────────────────────────────────────────
app.post('/api/auth/signup', async (req, res) => {
    try {
        const { email, password } = req.body;
        console.log(`Signup attempt for: ${email}`);
        const existingUser = await User.findOne({ email });
        
        if (existingUser) {
            return res.status(400).json({ error: 'Account already exists. Please login instead.' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({ email, password: hashedPassword });
        await newUser.save();

        res.status(201).json({ message: 'User created successfully' });
    } catch (err) {
        console.error('Signup error:', err.message, err.code);
        res.status(500).json({ error: err.message || 'Signup failed' });
    }
});

app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        console.log(`Login attempt for: ${email}`);
        const user = await User.findOne({ email });

        if (!user) {
            return res.status(404).json({ error: 'Account does not exist. Please sign up.' });
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const token = jwt.sign({ id: user._id, email: user.email }, JWT_SECRET, { expiresIn: '1d' });
        res.json({ token, email: user.email });
    } catch (err) {
        console.error('Login error:', err.message);
        res.status(500).json({ error: err.message || 'Login failed' });
    }
});

// ── History API ──────────────────────────────────────────────────────────────
app.get('/api/history', authenticateToken, async (req, res) => {
    try {
        const chats = await Chat.find({ userId: req.user.id }).sort({ updatedAt: -1 });
        res.json(chats);
    } catch (err) {
        console.error('History Fetch Error:', err);
        res.status(500).json({ error: 'Failed to fetch history.' });
    }
});

app.post('/api/history', authenticateToken, async (req, res) => {
    try {
        const { chatId, title, messages } = req.body;
        
        let chat;
        // Case 1: Client-side ID (starts with 'chat_') -> Create new
        if (chatId && typeof chatId === 'string' && chatId.startsWith('chat_')) {
            chat = new Chat({
                userId: req.user.id,
                title: title || 'New Chat',
                messages: messages || []
            });
            await chat.save();
        } 
        // Case 2: Existing Database ID -> Update
        else if (chatId && mongoose.Types.ObjectId.isValid(chatId)) {
            chat = await Chat.findOneAndUpdate(
                { _id: chatId, userId: req.user.id },
                { title, messages, updatedAt: Date.now() },
                { new: true }
            );

            // Fallback: If not found (e.g. deleted or wrong user), create new instead of returning null
            if (!chat) {
                chat = new Chat({
                    userId: req.user.id,
                    title: title || 'New Chat',
                    messages: messages || []
                });
                await chat.save();
            }
        } 
        // Case 3: No ID or invalid -> Create new
        else {
            chat = new Chat({
                userId: req.user.id,
                title: title || 'New Chat',
                messages: messages || []
            });
            await chat.save();
        }
        
        res.json(chat);
    } catch (err) {
        console.error('History Save Error:', err);
        res.status(500).json({ error: 'Failed to save history: ' + err.message });
    }
});

app.delete('/api/history/:id', authenticateToken, async (req, res) => {
    try {
        await Chat.findOneAndDelete({ _id: req.params.id, userId: req.user.id });
        res.json({ message: 'Chat deleted.' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to delete chat.' });
    }
});

// POST /api/chat: The main bridge to the local NLP & fuzzy inference engine
app.post('/api/chat', async (req, res) => {
    const { message } = req.body;
    
    const payload = {
        message
    };

    console.log('Spawning inference process for message...');
    const pythonProcess = spawn(pythonExecutable, ['run_inference.py', JSON.stringify(payload)]);
    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => result += data.toString());
    pythonProcess.stderr.on('data', (data) => error += data.toString());

    pythonProcess.on('error', (err) => {
        console.error('Failed to start Python process:', err);
        if (!res.headersSent) {
            res.status(500).json({ error: 'Failed to start inference engine.' });
        }
    });

    pythonProcess.on('close', (code) => {
        if (res.headersSent) return;

        if (code !== 0) {
            console.error('Python Error (Code ' + code + '):', error);
            if (!res.headersSent) {
                res.status(500).json({ error: 'Inference engine failed: ' + error });
            }
            return;
        }
        try {
            res.json(JSON.parse(result));
        } catch (e) {
            console.error('JSON Parse Error:', e.message, 'Result:', result);
            res.status(500).json({ error: 'Failed to parse recommendation output.' });
        }
    });

    // Timeout safety
    setTimeout(() => {
        if (!res.headersSent) {
            pythonProcess.kill();
            res.status(504).json({ error: 'Inference engine timeout. Please try a simpler query.' });
        }
    }, 60000); 
});

// POST /api/expand: Pre-defined local content for the result page
app.post('/api/expand', async (req, res) => {
    const { topic, energyData, question } = req.body;

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const sendEvent = (data) => res.write(`data: ${JSON.stringify(data)}\n\n`);

    // Handle NLP Q&A
    if (topic === 'question' && question) {
        console.log('Spawning NLP QA engine for:', question);
        const pythonProcess = spawn(pythonExecutable, ['predict_qa.py', question]);
        
        let fullResult = '';
        pythonProcess.stdout.on('data', (data) => {
            fullResult += data.toString();
        });

        pythonProcess.on('close', (code) => {
            const words = fullResult.trim().split(' ');
            words.forEach(word => sendEvent({ text: word + ' ' }));
            sendEvent({ done: true });
            res.end();
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`NLP Error: ${data}`);
        });
        return;
    }

    const localMap = {
        installation: energyData?.installation_guide,
        safety:       energyData?.safety_plan,
        environment:  energyData?.detailed_impact,
        roi:          energyData?.financial_roi,
        subsidy:      energyData?.government_subsidy_detailed
    };

    let content = localMap[topic] || "No detailed analysis found for this topic.";
    
    // Immediate response for local content
    const words = content.split(' ');
    words.forEach(word => sendEvent({ text: word + ' ' }));
    sendEvent({ done: true });
    res.end();
});

// Status check for UI consistency
app.get('/api/status', (req, res) => {
    res.json({ status: 'online' });
});

app.listen(PORT, () => {
    console.log(`Eco-AI server running: http://localhost:${PORT}`);
    console.log(`   Intelligence: LOCAL (No external API)`);
});
