const express = require('express');
const { engine } = require('express-handlebars');
const { spawn } = require('child_process');

const app = express()
app.use(express.urlencoded({ extended: true }));
const path = require('path')

app.engine('hbs', engine({ extname: 'hbs' }))
app.set('view engine', 'hbs')
app.set('views', path.join(__dirname, 'views'))

app.get('/', (req, res) => {
    res.render('index', {
        user: 'Katya'
    })
})

app.post('/analyze', (req, res) => {
    const inputText = req.body.koreanText

    const child = spawn('python', ['./scripts/process_text.py'])
    
    child.stdin.write(inputText);
    child.stdin.end();

    let outputData = '';
    let errorData = '';

    child.stdout.on('data', (chunk) => {
        outputData += chunk.toString();
    })

    child.stderr.on('data', (chunk) => {
        errorData += chunk.toString();
    })

    child.on('close', (code) => {
        if (code !== 0) {
            console.log('Помилка Python:', errorData)
            return res.render('index', {
                error: 'Сталася помилка при обробці тексту.'
            })
        }
        try {
            const parsedWords = JSON.parse(outputData.trim());
            res.render('index', {
                words: parsedWords, 
                originalText: inputText
            })
        } catch (err) {
            console.error('Помилка парсингу JSON:', err)
            res.render('index', { 
                error: 'Не вдалося прочитати дані від Python.' 
            });
        }
        
    })
    
})

const PORT = 3000
app.listen(PORT , ()  => {
    console.log(`Server started: http://localhost:${PORT}`)
})