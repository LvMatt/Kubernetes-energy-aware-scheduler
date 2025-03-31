const express = require("express");
const axios = require("axios");

const app = express();
const PORT = 3000;

app.get("/score", async (req, res) => {
    const nodeName = req.query?.nodeName;
    const podName = req.query?.podName;
    const podPriority = req.query?.podPriority;
    const podSchedulerNameAffilation = req.query?.podSchedulerNameAffilation;

    if(!nodeName || !podName || !podPriority || !podSchedulerNameAffilation ) res.json({
        'score': 0,
        'node': '',
        'statusCode': 400
    })
    
    let energyUsage = Math.floor(Math.random() * 100); 
    let score = 100 - energyUsage;

    console.log(`Node: ${nodeName}, Energy Usage: ${energyUsage}, Score: ${score}`);
    res.json({
        'score': score,
        'node': nodeName,
        'statusCode': 200
    });
});

// Start the server
app.listen(PORT, "0.0.0.0", () => {
    console.log(`Middleware is running on http://0.0.0.0:${PORT}`);
});
