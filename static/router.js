import Home from "./components/Home.js"
import Login from "./components/Login.js"
import Register from "./components/Register.js"
import AdminDashboard from "./components/AdminDashboard.js"
import AdminDashHome from './components/admin_dashboard_components/AdminDashHome.js'
import AdminViewParkingLot from './components/admin_dashboard_components/AdminViewParkingLot.js'
import AdminAddParkingLot from './components/admin_dashboard_components/AdminAddParkingLot.js'
import AdminUpdateParkingLot from './components/admin_dashboard_components/AdminUpdateParkingLot.js'
import AdminDashUsers from './components/admin_dashboard_components/AdminDashUsers.js'
import AdminDashParkings from "./components/admin_dashboard_components/AdminDashParkings.js"
import AdminDashSearch from './components/admin_dashboard_components/AdminDashSearch.js'
import UserDashboard from "./components/UserDashboard.js"
import UserEditProfile from "./components/user_dashboard_components/UserEditProfile.js"
import UserDashHome from './components/user_dashboard_components/UserDashHome.js'
import UserDashParkHist from './components/user_dashboard_components/UserDashParkHist.js'
import UserDashSearch from './components/user_dashboard_components/UserDashSearch.js'
import Summary from './components/Summary.js'


const routes = [
  {path: "/", component: Home},
  {path: "/login", component: Login},
  {path: "/register", component: Register},
  {
    path: "/admin_dashboard", 
    component: AdminDashboard,
    children : [
      {path: "parking_lots", component: AdminDashHome},
      {path: "view_lot/:id", name: "view_lot", component: AdminViewParkingLot},
      {path: "add_parking_lot", component: AdminAddParkingLot},
      {path: "users", component: AdminDashUsers},
      {path: "parkings", component: AdminDashParkings},
      {path: "update_lot/:id", name: "update_lot", component: AdminUpdateParkingLot},
      {path: "search", component: AdminDashSearch},
    ]
  },
  {
    path: "/user_dashboard", 
    component: UserDashboard, 
    children : [
      {path: "home", component: UserDashHome},
      {path: "parking_history", component: UserDashParkHist},
      {path: "search", component: UserDashSearch},
      {path: "edit_profile", component: UserEditProfile}
    ]
  },
  {path: "/summary", component: Summary}
]

const router = new VueRouter({
  routes
}) 

export default router;