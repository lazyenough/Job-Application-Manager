// const API_BASE_URL = "http://127.0.0.1:8000";
const API_BASE_URL = "https://job-application-manager-xfxz.onrender.com";

const authEmailInput = document.getElementById("authEmail");
const authPasswordInput = document.getElementById("authPassword");
const loginBtn = document.getElementById("loginBtn");
const registerBtn = document.getElementById("registerBtn");
const errorBox = document.getElementById("errorBox");
const successBox = document.getElementById("successBox");

function resetMessages() {
    errorBox.style.display = "none";
    successBox.style.display = "none";
}

const fetchOptions = (method, dataPayload) => {
    return {
        method: method,
        headers: {
            "Content-Type": "application/json" // Tells Pydantic JSON is coming
        },
        credentials: "include",
        body: JSON.stringify(dataPayload) // Converted to strict JSON string
    };
};

// 1. Handle Registration
registerBtn.addEventListener("click", async () => {
    const email = authEmailInput.value.trim();
    const password = authPasswordInput.value.trim();
    resetMessages();

    if (!email || !password) {
        errorBox.textContent = "Please provide both an email and password.";
        errorBox.style.display = "block";
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, fetchOptions("POST", { email, password }));
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Registration failed.");
        }
        successBox.textContent = "Account created! You can now log in.";
        successBox.style.display = "block";
        authPasswordInput.value = "";
    } catch (error) {
        errorBox.textContent = error.message;
        errorBox.style.display = "block";
    }
});

// 2. Handle Login & Redirect
loginBtn.addEventListener("click", async () => {
    const email = authEmailInput.value.trim();
    const password = authPasswordInput.value.trim();
    resetMessages();

    const credentialPayload = {
        email: email,
        password: password
    };

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, fetchOptions("POST", credentialPayload));
        if (!response.ok) throw new Error("Invalid credentials.");

        successBox.textContent = "Success! Redirecting...";
        successBox.style.display = "block";

        // SUCCESS ROUTING: Send the user straight to the dashboard page!
        window.location.href = "../index.html";
    } catch (error) {
        errorBox.textContent = error.message;
        errorBox.style.display = "block";
    }
});