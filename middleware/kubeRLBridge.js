const express = require("express");
const axios = require("axios");

const app = express();
const PORT = 3000;

app.get("/score", async (req, res) => {
    try {
        
        const nodesRaw = req.query?.nodes;
        const podName = req.query?.podName;
        const podPriority = req.query?.podPriority;
        const podSchedulerNameAffilation = req.query?.podSchedulerNameAffilation;
        console.log("nodesRaw", nodesRaw)
        console.log("podName", podName)
        if(!nodesRaw || !podName || !podPriority || !podSchedulerNameAffilation ) { 
            return res.json({
                "errorMsg": 'Parameters are missing',
                'bestNode': '',
                'statusCode': 400
            });
        }    
        let nodesArr;
        nodesArr = nodesRaw.split(',');
        // if(nodesRaw.includes('[') && nodesRaw.includes(']')  ) nodesArr = nodesRaw.replace('[', '').replace(']', '');

        const nodesLen = nodesArr.length;
        console.log("nodesLen", nodesLen)
        console.log("nodes:::--__", nodesArr)

        let energyUsage = Math.floor(Math.random() * 100); 
        let score = 100 - energyUsage;

        console.log(`Node: ${nodesRaw}, Energy Usage: ${energyUsage}, Score: ${score}`);
        return res.json({
            "errorMsg": '',
            'bestNode': nodesArr[0],
            'statusCode': 200
        });
    }
    catch (err) {
        console.warn("err____", String(err));
        return res.json({
            'errMsg': String(err),
            'bestNode': '',
            'statusCode': 400
        });
    }
});

// Start the server
app.listen(PORT, "0.0.0.0", () => {
    console.log(`Middleware is running on http://0.0.0.0:${PORT}`);
});
