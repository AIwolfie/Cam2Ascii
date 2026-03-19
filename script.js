const video = document.getElementById('pip-video');
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d', { willReadFrequently: true });

const asciiContainer = document.getElementById('ascii-container');
const btnStart = document.getElementById('start-btn');
const resSelect = document.getElementById('resolution');
const colorToggle = document.getElementById('color-toggle');
const edgeToggle = document.getElementById('edge-toggle');
const scanlineToggle = document.getElementById('scanline-toggle');
const faceToggle = document.getElementById('face-toggle');
const scanlinesDiv = document.getElementById('scanlines');

const ASCII_CHARS = " .'`^\",:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$".split("");
const NUM_CHARS = ASCII_CHARS.length;

let isPlaying = false;
let faceDetector = null;
let detectedFaces = [];
let frameCount = 0;

if ('FaceDetector' in window) {
    faceDetector = new FaceDetector({ maxDetectedFaces: 5, fastMode: true });
}

btnStart.addEventListener('click', async () => {
    if (isPlaying) {
        video.srcObject.getTracks().forEach(track => track.stop());
        isPlaying = false;
        btnStart.textContent = "Start Camera";
        video.style.display = 'none';
        return;
    }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.play();
        isPlaying = true;
        btnStart.textContent = "Stop Camera";
        video.style.display = 'block';
        requestAnimationFrame(renderLoop);
    } catch (err) {
        alert("Camera access denied or unavaliable.");
    }
});

scanlineToggle.addEventListener('change', (e) => {
    if (e.target.checked) scanlinesDiv.classList.remove('hidden');
    else scanlinesDiv.classList.add('hidden');
});

function adjustFontSize(width, height) {
    if (!height) return;
    const container = document.getElementById('container');
    const containerW = container.clientWidth;
    const containerH = container.clientHeight;
    
    // A typical monospace character is about 0.6 times as wide as its font-size.
    // Our line-height is also tightly packed (approx 0.8 * font-size).
    // Let's accurately scale it to fit the window bounds.
    let fitHeight = containerH / height / 0.8;
    let fitWidth = containerW / width / 0.6;
    
    let fontSize = Math.min(fitWidth, fitHeight) * 0.98; // 0.98 for a small inner padding margin
    if (fontSize < 1) fontSize = 1;

    asciiContainer.style.fontSize = `${fontSize}px`;
    asciiContainer.style.lineHeight = `${fontSize * 0.8}px`; // tight line height for ascii art
    asciiContainer.style.letterSpacing = `0px`;
}

window.addEventListener('resize', () => {
    if (canvas.width && canvas.height) {
        adjustFontSize(canvas.width, canvas.height);
    }
});

function renderLoop() {
    if (!isPlaying) return;

    const width = parseInt(resSelect.value);
    const aspect = video.videoHeight / video.videoWidth || 0.75;
    const height = Math.floor(width * aspect * 0.5);

    if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
        adjustFontSize(width, height);
    }

    ctx.drawImage(video, 0, 0, width, height);
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;

    let asciiStr = "";
    const useColor = colorToggle.checked;
    const useEdges = edgeToggle.checked;
    const useFace = faceToggle.checked;

    if (useFace && faceDetector && frameCount % 10 === 0) {
        faceDetector.detect(canvas).then(faces => {
            detectedFaces = faces;
        }).catch(() => {});
    }

    // Fast HTML buffer rendering
    for (let y = 0; y < height; y++) {
        let currentSpanColor = null;

        for (let x = 0; x < width; x++) {
            const index = (y * width + x) * 4;
            const r = data[index], g = data[index + 1], b = data[index + 2];

            const gray = (r * 0.299 + g * 0.587 + b * 0.114);
            let charIndex = Math.floor((gray / 255.0) * (NUM_CHARS - 1));
            let char = ASCII_CHARS[charIndex];

            if (useEdges && x < width - 1 && y < height - 1) {
                const rR = data[index + 4], gR = data[index + 5], bR = data[index + 6];
                const rD = data[index + width * 4], gD = data[index + width * 4 + 1], bD = data[index + width * 4 + 2];
                const grayRight = (rR * 0.299 + gR * 0.587 + bR * 0.114);
                const grayDown = (rD * 0.299 + gD * 0.587 + bD * 0.114);
                if (Math.abs(gray - grayRight) + Math.abs(gray - grayDown) > 40) {
                    char = '#';
                }
            }

            let color = '';
            if (useColor) color = `rgb(${r},${g},${b})`;

            if (useFace && detectedFaces.length > 0) {
                for (const face of detectedFaces) {
                    const bb = face.boundingBox;
                    if (x >= bb.x && x <= bb.x + bb.width && y >= bb.y && y <= bb.y + bb.height) {
                        color = 'red';
                        break;
                    }
                }
            }

            if (color !== '') {
                if (color !== currentSpanColor) {
                    if (currentSpanColor !== null) asciiStr += "</span>";
                    asciiStr += `<span style="color:${color}">`;
                    currentSpanColor = color;
                }
            } else if (currentSpanColor !== null) {
                asciiStr += "</span>";
                currentSpanColor = null;
            }

            if (char === '<') char = '&lt;';
            else if (char === '>') char = '&gt;';
            else if (char === '&') char = '&amp;';
            
            asciiStr += char;
        }
        if (currentSpanColor !== null) asciiStr += "</span>";
        asciiStr += "\n";
    }

    asciiContainer.innerHTML = asciiStr;
    frameCount++;
    requestAnimationFrame(renderLoop);
}
