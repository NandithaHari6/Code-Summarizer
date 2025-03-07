import { useEffect, useState } from "react";

const DummyLogin = () => {
    const [user, setUser] = useState(null);

    const handleLogin = () => {
        window.location.href = "https://code-summarizer.onrender.com/github-login";
    };
    const checkForCode = () => {
        const query = new URLSearchParams(window.location.search);
        const access_token = query.get("access_token");  // Extract `code` from URL
        
        if (access_token) {
            localStorage.setItem("token", access_token);
            console.log(access_token)
        }
    };

    // Attach the function to `window.onload`
    window.onload = checkForCode;

    // useEffect(() => {
    //     const query = new URLSearchParams(window.location.search);
    //     const token = query.get("access_token");

    //     if (token) {
    //         localStorage.setItem("token", token);
    //         console.log(access_token)
    //     }
    // }, []);

    return (
        <div>
            <h1>GitHub Login</h1>
            {user ? (
                <p>Welcome, GitHub ID: {user.github_id}</p>
            ) : (
                <button onClick={handleLogin}>Login with GitHub</button>
            )}
        </div>
    );
};

export default DummyLogin;