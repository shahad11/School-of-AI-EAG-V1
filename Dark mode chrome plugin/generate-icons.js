const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function generateIcons() {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    // Read the HTML file
    const html = fs.readFileSync('icon-generator.html', 'utf8');
    await page.setContent(html);

    // Generate icons for each size
    const sizes = [16, 48, 128];
    
    for (const size of sizes) {
        const element = await page.$(`#icon${size}`);
        await element.screenshot({
            path: path.join('images', `icon${size}.png`),
            omitBackground: true
        });
    }

    await browser.close();
    
    // Clean up temporary files
    fs.unlinkSync('icon-generator.html');
    fs.unlinkSync('package.json');
    fs.unlinkSync('generate-icons.js');
}

generateIcons().catch(console.error); 