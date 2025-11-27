import UserNavBar from "./user_dashboard_components/UserNavBar.js";

export default {
    template : `
        <div>
            <user-nav-bar></user-nav-bar>
            <router-view></router-view>
        </div>    
    `,
    components : {
        "user-nav-bar": UserNavBar
    }
}