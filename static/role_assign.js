async function assignRoles() {

    const TOKEN = localStorage.getItem("token");

    if (!TOKEN) {
        alert("You are not logged in. Please login first.");
        window.location.href = "/";
        return;
    }

    const userId = document.getElementById("user_id").value;
    const selectedRole = document.querySelector('input[name="role"]:checked');
    const messageEl = document.getElementById("message");

    if (!userId || isNaN(parseInt(userId))) {
        messageEl.innerText = "Please enter a valid User ID.";
        messageEl.style.color = "red";
        return;
    }

    if (!selectedRole) {
        messageEl.innerText = "Please select a role.";
        messageEl.style.color = "red";
        return;
    }

    const roleId = parseInt(selectedRole.value);

    try {
        const response = await fetch("http://localhost:8000/users/assign-role", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${TOKEN}`
            },
            body: JSON.stringify({
                user_id: parseInt(userId),
                role_id: roleId
            })
        });

        const result = await response.json();
        console.log("Response:", result);

        if (response.ok) {
            messageEl.innerText = result.message || "Role assigned successfully!";
            messageEl.style.color = "green";
        } else {
            messageEl.innerText = "Error: " + (result.detail || "Something went wrong");
            messageEl.style.color = "red";
        }

    } catch (err) {
        messageEl.innerText = "Request failed: " + err.message;
        messageEl.style.color = "red";
    }
}