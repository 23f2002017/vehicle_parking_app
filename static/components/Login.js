export default {
    template : `
        <div style="height:445px">
            <h1>Login Page</h1>
            <p style="color: red">{{message}}</p>
            <form @submit.prevent="LoginUser">
                <fieldset style="margin-right: 980px;">
                    <legend>Input Login Details</legend>
                        <p>Email : <input type="email" v-model="LoginData.email" style="width: 90%"> </p> 
                        <p>Password : <input type="password" v-model="LoginData.password" style="width: 90%"></p>
                        <button type="submit"> Login </button>  
                </fieldset>
            </form>    
            <p>Not registered ? <router-link to="/register">Sign up as a new user</router-link></p>
        </div>    
    `,
    data() {
        return {
            LoginData : {
                email : "" ,
                password : ""
            },
            message : ""
        }
    },
    methods : {
        LoginUser: async function() {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(this.LoginData)
            })
            const data = await response.json()
            if (response.ok) {
                localStorage.setItem('auth_token', data.auth_token)       // Store the token in localStorage
                if (data.role == "admin") {
                    this.$router.push("/admin_dashboard/parking_lots")      // Redirect to admin dashboard
                } else {
                    this.$router.push("/user_dashboard/home")      // Redirect to user dashboard
                }
            } else {
                this.message = data.message;
            }
        }
    }
}