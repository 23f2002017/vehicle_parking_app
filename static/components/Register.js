export default {
    template : `
        <div style="margin: 20px; height:70vh">
            <h1>Registeration Page</h1>
            <p style="color: red">{{message}}</p>
            <form @submit.prevent="RegisterUser">
                <fieldset style="margin-right: 920px;">
                    <legend>Input User Registration Details</legend>
                        <p>Name : <input type="text" v-model="RegistrationData.name" style="width:71%;"/></p>
                        <p>Email : <input type="email" v-model="RegistrationData.email" style="width:72%;"/></p>
                        <p>Password : <input type="password" v-model="RegistrationData.password" style="width:60%;"/></p>    
                        <button type="submit"> Register </button>
                </fieldset>
            </form>    
        </div>    
    `,
    data() {
        return {
            RegistrationData : {
                name :  "",
                email :  "",
                password :  ""
            },
            message : ""
        }
    },
    methods : {
        RegisterUser: async function() {
            const response = await fetch("/api/register", {
                    method : "POST",
                    headers : {
                        "Content-Type": "application/json"
                    },
                    body : JSON.stringify(this.RegistrationData)
                })
            const data = await response.json()
            if (response.ok) {
                alert(data.message)
                this.$router.push("/login")             // Redirect to login page after successful registration
            } else {
                this.message = data.message;           // Display error message if registration fails
            }
        }
    }
}