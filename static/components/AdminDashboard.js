import AdminNavBar from "./admin_dashboard_components/AdminNavBar.js";

export default {
    template : `
        <div>
            <admin-nav-bar></admin-nav-bar>
            <router-view></router-view>
        </div>    
    `,
    components : {
        "admin-nav-bar": AdminNavBar
    }
}