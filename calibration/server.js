const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadPath = path.join(__dirname, 'uploads');
        if (!fs.existsSync(uploadPath)) {
            fs.mkdirSync(uploadPath);
        }
        cb(null, uploadPath);
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ storage: storage });

app.use(express.static('public'));

app.post('/calibrate', upload.array('images'), (req, res) => {
    try{const chessboardSize = req.body.chessboardSize;
        const squareSize = req.body.squareSize;
        const uploadPath = path.join(__dirname, 'uploads');
        console.log(chessboardSize, squareSize, uploadPath);
        //print out the length of the files
        let pythonData = '';
    
        const imageFiles = req.files.map(file => file.filename);
        //check if all files are images and whether there is any files 
        if (imageFiles.length === 0) {
            res.status(400).json({ error: 'No files uploaded' });
            console.log('No files uploaded');
            imageFiles.forEach(file => {
                fs.unlinkSync(path.join(uploadPath, file));
            });
            return;
        }
    
        const pythonProcess = spawn('python', [
            'cali.py',
            uploadPath,
            chessboardSize,
            squareSize,
            ...imageFiles  
        ]);
    
        
        pythonProcess.stdout.on('data', (data) => {
            pythonData += data.toString();
        });
    
        pythonProcess.on('close', (code) => {
            console.log(`Python exit，code：${code}`);
            res.json(JSON.parse(pythonData));
            imageFiles.forEach(file => {
                fs.unlinkSync(path.join(uploadPath, file));
            });
        });
    }
    catch(err){
        console.log(err);res.status(500).json({ error: 'Something broke!', details: err.message });
    }
    
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something broke!', details: err.message });
});

app.listen(3000, () => console.log('Server running on port 3000'));