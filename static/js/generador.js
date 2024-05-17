// server.js
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
const port = 3000;

app.use(bodyParser.json());

app.post('/generate', async (req, res) => {
    const { prompt, technique, examples, steps } = req.body;

    let finalPrompt = prompt;
    if (technique === 'few-shot') {
        examples.forEach((example, index) => {
            finalPrompt += `\nEjemplo ${index + 1}: ${example}`;
        });
    } else if (technique === 'cot') {
        steps.forEach((step, index) => {
            finalPrompt += `\nPaso ${index + 1}: ${step}`;
        });
    }

    try {
        const response = await axios.post('http://localhost:3306/generate', { 
            prompt: finalPrompt,
        });

        res.json({ output: response.data.output });
    } catch (error) {
        console.error('Error generating prompt:', error);
        res.status(500).json({ error: 'Error generating prompt' });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
