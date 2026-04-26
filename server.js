import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 5000;

app.use(cors());
app.use(bodyParser.json());
app.use('/static', express.static(path.join(__dirname, 'static')));

// ── Page Routes ─────────────────────────────────────────────────────────────
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'templates', 'index.html')));
app.get('/result', (req, res) => res.sendFile(path.join(__dirname, 'templates', 'result.html')));

// POST /api/chat: The main bridge to the local NLP & fuzzy inference engine
app.post('/api/chat', async (req, res) => {
    const { message } = req.body;
    
    const payload = {
        message
    };

    const pythonPath = path.join(__dirname, '.venv', 'Scripts', 'python.exe');
    console.log('Spawning inference process for message...');
    const pythonProcess = spawn(pythonPath, ['run_inference.py', JSON.stringify(payload)]);
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
            return res.status(500).json({ error: 'Inference engine failed.' });
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
        const pythonPath = path.join(__dirname, '.venv', 'Scripts', 'python.exe');
        const pythonProcess = spawn(pythonPath, ['predict_qa.py', question]);
        
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
