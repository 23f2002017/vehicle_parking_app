import UserNavBar from "./user_dashboard_components/UserNavBar.js";

export default {
    template : `
        <div>
            <user-nav-bar></user-nav-bar>
            <router-view v-if="status"></router-view>
            <h1 v-else style='color: red;'>Your account is currently BLOCKED by the Admin.</h1>
        </div>    
    `,
    data() {
        return {
            status : true,
        }
    },
    components : {
        "user-nav-bar": UserNavBar
    },
    mounted : async function() {
        const res = await fetch('/api/status', {
            method: 'GET',
            headers: {
                'auth-token': localStorage.getItem('auth_token'),
            }
        })
        if (!res.ok) {
            this.status = false
        }
    }
}