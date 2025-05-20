function initializePage() {
    document.getElementById("encryptSection").style.display = "none";
    document.getElementById("decryptSection").style.display = "none";
    document.getElementById("fileOptionsSection").style.display = "none";
}


function showEncrypt() {
    document.getElementById("encryptSection").style.display = "block";
    document.getElementById("decryptSection").style.display = "none";
    document.getElementById("fileOptionsSection").style.display = "none";
}

function showDecrypt() {
    document.getElementById("encryptSection").style.display = "none";
    document.getElementById("decryptSection").style.display = "block";
    document.getElementById("fileOptionsSection").style.display = "none";
}

function showFileOptions() {
    document.getElementById("encryptSection").style.display = "none";
    document.getElementById("decryptSection").style.display = "none";
    document.getElementById("fileOptionsSection").style.display = "block";
}

async function copyToClipboard(outputId) {
    const outputElement = document.getElementById(outputId);
    try {
        await navigator.clipboard.writeText(outputElement.innerText);
        alert('Text copied to clipboard!');
    } catch (err) {
        alert('Failed to copy text: ' + err);
    }
}

async function pasteFromClipboard(inputId) {
    const inputElement = document.getElementById(inputId);
    try {
        const text = await navigator.clipboard.readText();
        inputElement.value = text;
    } catch (err) {
        alert('Failed to paste text: ' + err);
    }
}

function validateInputs(note, key) {
    if (!note || note.trim() === "") {
        alert("Please enter a note to encrypt or decrypt.");
        return false;
    }
    if (!key || key.trim() === "") {
        alert("Please enter a key.");
        return false;
    }
    return true;
}

function getCipherMethod() {
    return document.getElementById("cipherSelect").value;
}

function getCipherMethodDecrypt() {
    return document.getElementById("cipherSelectDecrypt").value;
}

function getCipherMethodFile() {
    return document.getElementById("cipherSelectFile").value;
}

function caesarEncrypt(text, shift) {
    let result = "";
    for (let i = 0; i < text.length; i++) {
        let char = text[i];
        if (char.match(/[a-zA-Z]/)) {
            const charCode = char.charCodeAt(0);
            const base = (charCode >= 65 && charCode <= 90) ? 65 : 97;
            const newChar = String.fromCharCode((charCode - base + shift) % 26 + base);
            result += newChar;
        } else {
            result += char;
        }
    }
    return result;
}

function caesarDecrypt(text, shift) {
    let result = "";
    for (let i = 0; i < text.length; i++) {
        let char = text[i];
        if (char.match(/[a-zA-Z]/)) {
            const charCode = char.charCodeAt(0);
            const base = (charCode >= 65 && charCode <= 90) ? 65 : 97;
            const newChar = String.fromCharCode((charCode - base - shift + 26) % 26 + base);
            result += newChar;
        } else {
            result += char;
        }
    }
    return result;
}

function vigenereEncrypt(text, key) {
    const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    text = text.toUpperCase();
    key = key.toUpperCase();
    let encrypted = "";
    let keyIndex = 0;

    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (alphabet.includes(char)) {
            const charIndex = alphabet.indexOf(char);
            const keyCharIndex = alphabet.indexOf(key[keyIndex % key.length]);
            const encryptedChar = alphabet[(charIndex + keyCharIndex) % 26];
            encrypted += encryptedChar;
            keyIndex++;
        } else {
            encrypted += char;
        }
    }
    return encrypted;
}

function vigenereDecrypt(text, key) {
    const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    text = text.toUpperCase();
    key = key.toUpperCase();
    let decrypted = "";
    let keyIndex = 0;

    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (alphabet.includes(char)) {
            const charIndex = alphabet.indexOf(char);
            const keyCharIndex = alphabet.indexOf(key[keyIndex % key.length]);
            const decryptedChar = alphabet[(charIndex - keyCharIndex + 26) % 26];
            decrypted += decryptedChar;
            keyIndex++;
        } else {
            decrypted += char;
        }
    }
    return decrypted;
}

function encryptNote() {
    const note = document.getElementById("note").value;
    const key = document.getElementById("key").value;
    if (!validateInputs(note, key)) return;

    const cipher = getCipherMethod();
    let encryptedNote = "";

    if (cipher === "caesar") {
        const shift = parseInt(key);
        if (isNaN(shift)) {
            alert("Invalid shift value for Caesar cipher. Please enter a valid number.");
            return;
        }
        encryptedNote = caesarEncrypt(note, shift);
    } else if (cipher === "vigenere") {
        encryptedNote = vigenereEncrypt(note, key);
    }

    document.getElementById("output").innerText = encryptedNote;
}

function saveEncryptToFile() {
    const encryptedNote = document.getElementById("output").innerText.replace("Encrypted Note: \n", "");
    const fileNameInput = document.getElementById("fileNameEncrypt").value.trim();
    const fileName = fileNameInput !== "" ? fileNameInput + ".txt" : "encrypted_note.txt";

    if (encryptedNote.trim() === "") {
        alert("There is no encrypted content to save.");
        return;
    }

    const blob = new Blob([encryptedNote], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    link.click();
}

function decryptNote() {
    const note = document.getElementById("noteDecrypt").value;
    const key = document.getElementById("keyDecrypt").value;
    if (!validateInputs(note, key)) return;

    const cipher = getCipherMethodDecrypt();
    let decryptedNote = "";

    if (cipher === "caesar") {
        const shift = parseInt(key);
        if (isNaN(shift)) {
            alert("Invalid shift value for Caesar cipher. Please enter a valid number.");
            return;
        }
        decryptedNote = caesarDecrypt(note, shift);
    } else if (cipher === "vigenere") {
        decryptedNote = vigenereDecrypt(note, key);
    }

    document.getElementById("outputDecrypt").innerText = decryptedNote;
}

function loadFromFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    const key = document.getElementById("keyFile").value.trim();
    const cipher = getCipherMethodFile();

    if (!file) {
        alert("Please select a file.");
        return;
    }
    if (!key) {
        alert("Please enter a key to decrypt the file.");
        return;
    }

    const reader = new FileReader();
    reader.onload = function (event) {
        const content = event.target.result;
        let decryptedContent = "";

        try {
            if (cipher === "caesar") {
                const shift = parseInt(key);
                if (isNaN(shift)) {
                    alert("Invalid shift value for Caesar cipher. Please enter a valid number.");
                    return;
                }
                decryptedContent = caesarDecrypt(content, shift);
            } else if (cipher === "vigenere") {
                decryptedContent = vigenereDecrypt(content, key);
            }

            document.getElementById("outputFile").innerText = "Decrypted File Content:\n" + decryptedContent;
        } catch (error) {
            alert("Error during decryption: " + error.message);
        }
    };

    reader.onerror = function () {
        alert("Failed to read the file. Please try again.");
    };

    reader.readAsText(file);
}

function showEncrypt() {
    document.getElementById("encryptSection").style.display = "block";
    document.getElementById("decryptSection").style.display = "none";
    document.getElementById("fileOptionsSection").style.display = "none";
}

function showDecrypt() {
    document.getElementById("encryptSection").style.display = "none";
    document.getElementById("decryptSection").style.display = "block";
    document.getElementById("fileOptionsSection").style.display = "none";
}

function showFileOptions() {
    document.getElementById("encryptSection").style.display = "none";
    document.getElementById("decryptSection").style.display = "none";
    document.getElementById("fileOptionsSection").style.display = "block";
}

function saveToDatabase(type) {
    const outputId = type === "encrypt" ? "output" : "outputDecrypt";
    const note = document.getElementById(outputId).innerText.replace(type === "encrypt" ? "Encrypted Note: \n" : "Decrypted Note: \n", "");

    if (!note || note.trim() === "") {
        alert(`There is no ${type === "encrypt" ? "encrypted" : "decrypted"} content to save.`);
        return;
    }

    fetch("/save_note", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            content: note,
            type: type,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert(`${type === "encrypt" ? "Encrypted" : "Decrypted"} note saved to database successfully!`);
            } else {
                alert(`Failed to save ${type === "encrypt" ? "encrypted" : "decrypted"} note: ${data.error}`);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while saving to database.");
        });
}

window.onload = function() {
    initializePage();
};
