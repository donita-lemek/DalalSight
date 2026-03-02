import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import http from 'http';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;
const ML_ENGINE_URL = process.env.ML_ENGINE_URL || "https://dalalsight.onrender.com";

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
    res.json({ status: 'API Gateway is running' });
});

app.post('/api/allocate', async (req, res) => {
    try {
        const { risk_capacity, selected_industries } = req.body;

        // Instead of using axios, we use native fetch to call the ML Engine
        const mlResponse = await fetch(`${ML_ENGINE_URL}/allocate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ risk_capacity, selected_industries })
        });

        if (!mlResponse.ok) {
            throw new Error(`ML Engine answered with status ${mlResponse.status}`);
        }

        const data = await mlResponse.json();
        res.json(data);
    } catch (error: any) {
        console.error('Error calling ML Engine:', error.message);
        res.status(500).json({ error: 'Failed to process portfolio allocation' });
    }
});

app.listen(port, () => {
    console.log(`API Gateway listening on ${port}`);
});
