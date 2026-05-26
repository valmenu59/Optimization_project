import express from "express";
import path from 'path';
import {exec} from 'child_process';
import { fileURLToPath } from 'url';
import fs from 'fs';
import readline from 'readline';

const port = 3000;
const app = express();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);


app.set('view engine', 'ejs');
app.use(express.static('public'));

const promises = [];
let all_results;

for (let i = 1; i <= 24; i++) {
    const file_path = path.join(__dirname, 'results', `result${i}.txt`);

    const p = readFile(file_path)
        .catch((error) => {
            console.warn(`File result${i}.txt no present or corrupted`);
            return null;
        });

    promises.push(p);
}

Promise.all(promises)
    .then((ordered_results) => {
        all_results = ordered_results;
    })
    .catch((err) => {
        console.error("Critical error: ", err);
    });





async function readFile(path) {
    try {
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
            if (count % 2 === 0) {
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
        //console.log(matrix);
        return matrix;
    } catch (error) {
        console.error(error);
        return null;
    }
}




app.get("/", (req, res) => {
    if (all_results){
        res.render("cplex", { results: all_results});
    } else {
        res.send("Critical error");
    }
});




app.listen(port, () => {
    console.log(`[server]: Server is running at http://localhost:${port}`);
});