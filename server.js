import express from "express";
//import path from 'path';
import {exec} from 'child_process';
import fs from 'fs';
import readline from 'readline';

const port = 3000;
const app = express();
app.set('view engine', 'ejs');
app.use(express.static('public'));

async function readFile(path) {
    const fileStream = fs.createReadStream(path);

    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    let matrix = [];
    let count = 0;
    let countPeople = 0;
    for await (const line of rl) {
        //text += line + "\n";
        if (count % 2 === 0){
            //text += line + "/n";
            matrix.push([line])
        } else {
            //text += line + "/n";
            matrix[countPeople].push(line)
            countPeople++;
        }
        count++;


        //console.log(`Ligne lue : ${line}`);
    }
    console.log(matrix);
    return matrix;
}




exec('python3 main.py', (error, stdout, stderr) => {
    if (error) {
        console.error(`Error: ${error.message}`);
        return;
    }
    if (stderr) {
        console.error(`Software error: ${stderr}`);
        return;
    }
    //console.log(`{stdout}`);
    app.get("/", (req, res) => {
        readFile("results.txt").then(r => {
            res.render("cplex", {results: r});
        });

    });
});



app.listen(port, () => {
    console.log(`[server]: Server is running at http://localhost:${port}`);
});