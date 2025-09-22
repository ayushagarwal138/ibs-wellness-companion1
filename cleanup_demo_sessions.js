// Script to clean all demo login sessions and authentication data
console.log("🔍 Checking for existing authentication data...");

// Check localStorage for authentication tokens
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');
const userInfo = localStorage.getItem('user');

console.log("Current localStorage contents:");
console.log("- access_token:", accessToken ? "EXISTS" : "NOT FOUND");
console.log("- refresh_token:", refreshToken ? "EXISTS" : "NOT FOUND");
console.log("- user:", userInfo ? "EXISTS" : "NOT FOUND");

if (userInfo) {
    try {
        const user = JSON.parse(userInfo);
        console.log("- User email:", user.email);
        console.log("- User ID:", user.id);
    } catch (e) {
        console.log("- User data corrupted");
    }
}

// Check sessionStorage as well
const sessionKeys = Object.keys(sessionStorage);
console.log("SessionStorage keys:", sessionKeys);

// Clean all authentication data
console.log("\n🧹 Cleaning all authentication data...");

// Clear localStorage authentication items
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
localStorage.removeItem('user');

// Clear any other potential auth-related items
const allLocalStorageKeys = Object.keys(localStorage);
allLocalStorageKeys.forEach(key => {
    if (key.includes('auth') || key.includes('token') || key.includes('session')) {
        console.log(`Removing localStorage key: ${key}`);
        localStorage.removeItem(key);
    }
});

// Clear sessionStorage
sessionStorage.clear();

// Clear any cookies that might contain auth data
document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
});

console.log("✅ All authentication data cleared!");
console.log("🔄 Reloading page to ensure clean state...");

// Reload the page to ensure clean state
setTimeout(() => {
    window.location.reload();
}, 1000);
