console.log("Dashboard JS Loaded");

// Session management
let currentSessionId = generateSessionId();

function generateSessionId() {
  return (
    "chat_" + Date.now() + "_" + Math.random().toString(36).substring(2, 8)
  );
}

// Load dashboard
async function loadDashboard() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    window.location.href = "/";
    return;
  }

  try {
    const response = await fetch("http://localhost:8000/users/me", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      alert("Session expired. Please login again.");
      localStorage.removeItem("token");
      window.location.href = "/";
      return;
    }

    const user = await response.json();
    const role = user.role || user["role"];

    document.getElementById("currentUser").innerText =
      user.name || user["name"] || user.email;
    const nameStr = user.name || user["name"] || user.email || "U";
    document.getElementById("avatarLetter").innerText = nameStr
      .charAt(0)
      .toUpperCase();

    if (role !== "admin") {
      document.getElementById("addRoleBtn").style.display = "none";
      document.getElementById("deleteDocsBtn").style.display = "none";
    } else {
      document.getElementById("addRoleBtn").style.display = "block";
      document.getElementById("deleteDocsBtn").style.display = "inline-block";
    }

    // Load chat history sidebar
    loadChatSessions();
  } catch (err) {
    console.error("Failed to load dashboard:", err);
  }
}

// Upload document
async function uploadDoc() {
  const fileInput = document.getElementById("file");
  const token = localStorage.getItem("token");
  const statusDiv = document.getElementById("status");

  if (!fileInput.files[0]) {
    statusDiv.innerText = "Please select a file first.";
    statusDiv.style.color = "red";
    return;
  }

  if (!token) {
    alert("Please login first");
    window.location.href = "/";
    return;
  }

  statusDiv.innerText = "Uploading...";
  statusDiv.style.color = "orange";

  try {
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("title", fileInput.files[0].name);
    formData.append("company_name", "Default");
    formData.append("document_type", "report");

    const response = await fetch("http://localhost:8000/documents/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    const data = await response.json();
    if (response.ok) {
      statusDiv.innerText = data.message || "Uploaded successfully!";
      statusDiv.style.color = "green";
    } else {
      statusDiv.innerText =
        "Upload failed: " + (data.detail || "Unknown error");
      statusDiv.style.color = "red";
    }
  } catch (err) {
    statusDiv.innerText = "Upload error: " + err.message;
    statusDiv.style.color = "red";
  }
}

// Show/hide documents for deletion
async function showDocuments() {
  const token = localStorage.getItem("token");
  const docListDiv = document.getElementById("docList");
  const panel = document.getElementById("docListPanel");

  docListDiv.innerHTML = "<p>Loading documents...</p>";
  panel.style.display = "block";

  try {
    const response = await fetch("http://localhost:8000/documents/", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });

    const docs = await response.json();
    if (!docs || docs.length === 0) {
      docListDiv.innerHTML = "<p>No documents found.</p>";
      return;
    }

    let html =
      '<table class="doc-table"><tr><th>ID</th><th>Title</th><th>Company</th><th>Type</th><th>Uploaded By</th><th>Action</th></tr>';
    docs.forEach((doc) => {
      html += `<tr>
        <td>${doc.document_id}</td>
        <td>${doc.title}</td>
        <td>${doc.company_name || "-"}</td>
        <td>${doc.document_type || "-"}</td>
        <td>${doc.uploaded_by || "-"}</td>
        <td><button class="delete-btn" onclick="deleteDoc(${doc.document_id}, '${doc.title}')">Delete</button></td>
      </tr>`;
    });
    html += "</table>";
    docListDiv.innerHTML = html;
  } catch (err) {
    docListDiv.innerHTML =
      "<p style='color:red'>Failed to load documents: " + err.message + "</p>";
  }
}

function hideDocuments() {
  document.getElementById("docListPanel").style.display = "none";
}

async function deleteDoc(docId, title) {
  if (!confirm(`Are you sure you want to delete "${title}"?`)) return;

  const token = localStorage.getItem("token");
  try {
    const response = await fetch(`http://localhost:8000/documents/${docId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    if (response.ok) {
      alert(data.message || "Document deleted!");
      showDocuments();
    } else {
      alert("Delete failed: " + (data.detail || "Unknown error"));
    }
  } catch (err) {
    alert("Delete error: " + err.message);
  }
}

// Chat bubble helper
function addBubble(type, html) {
  const chatDiv = document.getElementById("chatMessages");
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${type}`;
  bubble.innerHTML = html;
  chatDiv.appendChild(bubble);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

//  Ask question (with chat save)
async function askQuestion() {
  const input = document.getElementById("question");
  const question = input.value.trim();

  if (!question) return;

  addBubble("user", question);
  input.value = "";

  // Show loading spinner as bot bubble
  const loadingBubble = document.createElement("div");
  loadingBubble.className = "chat-bubble bot";
  loadingBubble.id = "loadingBubble";
  loadingBubble.innerHTML = '<div class="spinner" style="margin:0"></div>';
  const chatDiv = document.getElementById("chatMessages");
  chatDiv.appendChild(loadingBubble);
  chatDiv.scrollTop = chatDiv.scrollHeight;

  try {
    const response = await fetch("http://localhost:8000/rag/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({ query: question }),
    });

    const data = await response.json();
    const lb = document.getElementById("loadingBubble");
    if (lb) lb.remove();

    let responseText = "";

    if (response.ok) {
      if (data.results && data.results.length > 0) {
        const resultsHtml = data.results
          .map((r, i) => {
            const text = r.document || r;
            const score = r.score
              ? `<span class="score">relevance: ${r.score.toFixed(2)}</span>`
              : "";
            return `<div class="result-item"><strong>${i + 1}.</strong> ${text} ${score}</div>`;
          })
          .join("");
        addBubble("bot", resultsHtml);
        responseText = data.results.map((r) => r.document || r).join(" | ");
      } else {
        addBubble("bot", "No results found.");
        responseText = "No results found.";
      }
    } else {
      const errMsg = "❌ " + (data.detail || "Something went wrong");
      addBubble("bot", errMsg);
      responseText = errMsg;
    }

    // Save to DB
    saveChat(question, responseText);
  } catch (err) {
    const lb = document.getElementById("loadingBubble");
    if (lb) lb.remove();
    const errMsg = "Request failed: " + err.message;
    addBubble("bot", errMsg);
    saveChat(question, errMsg);
  }
}

// Save chat to backend
async function saveChat(question, response) {
  try {
    await fetch("http://localhost:8000/chat/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        session_id: currentSessionId,
        question: question,
        response: response,
      }),
    });
    // Refresh sidebar
    loadChatSessions();
  } catch (err) {
    console.error("Failed to save chat:", err);
  }
}

// Load chat sessions in sidebar
async function loadChatSessions() {
  const token = localStorage.getItem("token");
  const historyList = document.getElementById("history");

  try {
    const response = await fetch("http://localhost:8000/chat/sessions", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });
    const sessions = await response.json();

    historyList.innerHTML = "";

    sessions.forEach((session) => {
      const li = document.createElement("li");
      li.className = "history-item";
      if (session.session_id === currentSessionId) li.classList.add("active");
      li.title = `${session.message_count} messages`;
      li.onclick = () => loadSession(session.session_id);

      const titleSpan = document.createElement("span");
      titleSpan.className = "history-title";
      titleSpan.textContent = session.title;

      const deleteBtn = document.createElement("button");
      deleteBtn.className = "history-delete-btn";
      deleteBtn.textContent = "Delete";
      deleteBtn.title = "Delete this chat";
      deleteBtn.onclick = (e) => deleteChatSession(e, session.session_id);

      li.appendChild(titleSpan);
      li.appendChild(deleteBtn);
      historyList.appendChild(li);
    });
  } catch (err) {
    console.error("Failed to load sessions:", err);
  }
}

// Load a previous chat session
async function loadSession(sessionId) {
  const token = localStorage.getItem("token");
  currentSessionId = sessionId;

  // Clear chat area
  document.getElementById("chatMessages").innerHTML = "";

  try {
    const response = await fetch(
      `http://localhost:8000/chat/history/${sessionId}`,
      {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    const messages = await response.json();

    messages.forEach((msg) => {
      addBubble("user", msg.question);
      addBubble("bot", msg.response);
    });

    // Update active item in sidebar
    document
      .querySelectorAll(".history-item")
      .forEach((li) => li.classList.remove("active"));
    document.querySelectorAll(".history-item").forEach((li) => {
      if (li.onclick.toString().includes(sessionId)) li.classList.add("active");
    });

    loadChatSessions();
  } catch (err) {
    console.error("Failed to load session:", err);
  }
}

// Delete a chat session
async function deleteChatSession(event, sessionId) {
  event.stopPropagation();

  if (!confirm("Are you sure you want to delete this chat session?")) return;

  const token = localStorage.getItem("token");
  try {
    const response = await fetch(
      `http://localhost:8000/chat/sessions/${sessionId}`,
      {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    const data = await response.json();

    if (response.ok) {
      alert(data.message || "Chat session deleted");
      if (sessionId === currentSessionId) {
        startNewChat();
      }
      loadChatSessions();
    } else {
      alert(
        "Failed to delete session: " +
          (data.detail || data.message || "Unknown error"),
      );
    }
  } catch (err) {
    alert("Error deleting chat session: " + err.message);
  }
}

// Start a new chat
function startNewChat() {
  currentSessionId = generateSessionId();
  document.getElementById("chatMessages").innerHTML = "";
  document.getElementById("question").value = "";

  // Remove active highlight
  document
    .querySelectorAll(".history-item")
    .forEach((li) => li.classList.remove("active"));
}

// Utility
function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}

function toggleMenu() {
  document.getElementById("menuDropdown").classList.toggle("hidden");
}

function addRole() {
  window.location.href = "/admin/assign-role";
}

window.onload = function () {
  loadDashboard();
  document.getElementById("logoutBtn").onclick = logout;
  document.getElementById("addRoleBtn").onclick = addRole;
};
