export default {
    template : `
        <div>
            <p style="font-size:110%">
                <router-link style="margin-right: 20px;" to="/admin_dashboard/parking_lots">Parking Lots</router-link>
                <router-link style="margin-right: 20px;" to="/admin_dashboard/users">Users</router-link> 
                <router-link style="margin-right: 20px;" to="/admin_dashboard/parkings">Parkings</router-link>
                <router-link style="margin-right: 20px;" to="/admin_dashboard/search">Search</router-link> 
                <router-link style="margin-right: 20px;" to="/admin_dashboard/summary">Summary</router-link>  
                <a style="margin-right: 550px;" href="/#/login" @click="LogoutUser" >Logout</a> 
            </p>
        </div>    
    `,
    methods : {
        LogoutUser() {
            fetch("/api/logout", {
                method: "GET",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token")
                }
            })
            localStorage.removeItem("auth_token")
        } 
    }
}