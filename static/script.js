// register..

let registerForm = document.getElementById("registerForm")

if(registerForm){

    registerForm.addEventListener("submit", async (e)=>{

        e.preventDefault()

        let formData = new FormData(registerForm)

        let res = await fetch("/register",{
            method:"POST",
            body:formData
        })

        let data = await res.json()

        document.getElementById("msg").innerText=data.message

    })
}


// login..

async function login(){

const email = document.getElementById("email").value
const password = document.getElementById("password").value

const response = await fetch("http://127.0.0.1:8000/login",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
email: email,
password: password
})
})

const data = await response.json()

console.log("LOGIN RESPONSE:", data)

const messageBox = document.getElementById("message")

if(!response.ok){
messageBox.innerText = data.detail
messageBox.style.color = "red"
return
}

messageBox.innerText = "Login successful"
messageBox.style.color = "green"

localStorage.setItem("token", data.token)

window.location.href = "/dashboard"

}