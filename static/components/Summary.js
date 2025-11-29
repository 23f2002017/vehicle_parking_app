import AdminNavBar from "./admin_dashboard_components/AdminNavBar.js";
import UserNavBar from "./user_dashboard_components/UserNavBar.js";

export default {
    template : `
        <div>
            <div v-if="role === 'admin'">
                <admin-nav-bar></admin-nav-bar>
                <h1>Summary</h1>
                <img src="./static/images/summary.png" alt="Summary Plot" style="width: 100%; max-width: 600px; height: auto;"><br>
                <div style="margin: 20px 50px; font-size: 120%; line-height: 1.5;">
                    Total Parking Lots: {{ details.total_parking_lots }}<br>
                    Total Parking Spots: {{ details.total_parking_spots }}<br>
                    Total Users: {{ details.total_users }}<br>
                    No. of Available Parking Spots: {{ details.total_available_parking_spots }}<br>
                    No. of Current Parkings: {{ details.total_current_parkings }}<br>
                    Total Parkings: {{ details.total_parkings }}<br>
                    Total Revenue: ₹{{ details.total_revenue }}/-<br>
                </div>
            </div> 
            <div v-else>
                <user-nav-bar></user-nav-bar>
                <div v-if="status">
                    <h1>Summary</h1>
                    <img src="./static/images/summary.png" alt="Summary Plot" style="width: 100%; max-width: 600px; height: auto;"><br>
                    <div style="margin: 20px 50px; font-size: 120%; line-height: 1.5;">
                        Total Parkings: {{ details.total_parkings }}<br>
                        No. of Current Parkings: {{ details.total_current_parkings }}<br>
                        Total Expenditure: ₹ {{ details.total_amount_spent }}/-<br>
                    </div>
                </div>
                <h1 v-else style='color: red;'>Your account is currently BLOCKED by the Admin.</h1>
            </div>
        </div>    
    `,
    data() {
        return {
            message : '',
            role : '',
            details : {},
            status : true
        }
    },
    mounted : async function() { 
        const res = await fetch('/api/summary', {
            method: 'GET',
            headers: {
                'auth-token': localStorage.getItem('auth_token'),
            }
        })
        const data = await res.json()
        if (res.ok) {
            this.details = data.details[0]
            this.role = data.role
        } else {
            this.message = data.message
            this.status = false
        }
        
    },
    components : {
            "user-nav-bar": UserNavBar,
            "admin-nav-bar": AdminNavBar
    }
}