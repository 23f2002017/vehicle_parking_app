export default {
    template : `
        <div>
            <p style="font-size:110%">
                <router-link style="margin-right: 20px;" to="/user_dashboard/home">Home</router-link>
                <router-link style="margin-right: 20px;" to="/user_dashboard/parking_history">Parking History</router-link> 
                <router-link style="margin-right: 20px;" to="/user_dashboard/search">Search</router-link> 
                <router-link style="margin-right: 20px;" to="/user_dashboard/summary">Summary</router-link>  
                <a href="/#/login" @click="LogoutUser" >Logout</a> 
                <span style="float: right;">Hello, {{userData.name}}&nbsp;&nbsp;<router-link to="/user_dashboard/edit_profile">Edit Profile</a></span>
            </p>
        </div>    
    `,
    data() {
        return {
            userData : {
                id : "",
                name : "",
                email : "",
            }
        }
    },
    methods : {
        LogoutUser() {
            fetch("/api/logout", {
                method: "GET",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token")
                }
            })
            localStorage.removeItem("auth_token")
        },
        GetUser: async function() {
            const res = await fetch("/api/profile", {
                method: "GET",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token")
                }
            })
            const data = await res.json()
            if (res.ok) {
                this.userData = data.user_profile 
            }
        }
    },
    mounted(){
        this.GetUser()
    }
}