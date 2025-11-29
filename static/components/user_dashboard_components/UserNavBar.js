export default {
    template : `
        <div>
            <p style="font-size:110%">
                <router-link style="margin-right: 20px;" to="/user_dashboard/home">Home</router-link>
                <router-link style="margin-right: 20px;" to="/user_dashboard/parking_history">Parking History</router-link> 
                <router-link style="margin-right: 20px;" to="/user_dashboard/search">Search</router-link> 
                <router-link style="margin-right: 20px;" to="/summary">Summary</router-link>  
                <a href="/#/login" @click="LogoutUser" >Logout</a> 
                <span v-if="status" style="float: right;">Hello, {{userData.name}} &nbsp; <router-link to="/user_dashboard/edit_profile"><button style="font-size: medium">Edit Profile</button></router-link> &nbsp; <button @click="DownloadCSVReport(userData.id)" style="font-size: medium">Download Report</button></span>
            </p>
        </div>    
    `,
    data() {
        return {
            userData : {
                id : "",
                name : "",
                email : "",
            },
            status : false
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
                this.status = true
            }
        },
        DownloadCSVReport: async function(id) {
            fetch(`/api/create_user_report/${id}`)
                .then(res => res.json())
                .then(data =>
                    window.location.href = `/api/download_user_report/${data.task_id}`
                )
        }
    },
    mounted(){
        this.GetUser()
    }
}